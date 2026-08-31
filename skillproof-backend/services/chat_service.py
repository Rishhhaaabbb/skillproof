# Task 11: Chat service — conversational AI grounded in user's analysis data
"""
Multi-turn chat grounded in the user's actual TPR score, breakdown,
flags, and target role context. Never gives generic advice.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from models.database import Analysis, ChatMessage, TargetRole
from services.llm_generator import LLMGenerator

logger = logging.getLogger(__name__)

_CHAT_SYSTEM_INSTRUCTION = """You are SkillProof's AI mentor, helping a developer understand and improve their GitHub readiness score.

Rules:
- ALWAYS ground your responses in the candidate's specific data (scores, flags, repos).
- NEVER give generic advice like "contribute to open source" without citing their specific situation.
- Keep responses under 150 words.
- Be encouraging but honest — surface real gaps with actionable suggestions.
- If asked something outside the candidate's profile, politely redirect to their data."""

_MAX_HISTORY_MESSAGES = 6
_MAX_CONTEXT_CHARS = 1500


class ChatService:
    """Handles multi-turn chat sessions grounded in analysis data."""

    def __init__(self) -> None:
        self.llm = LLMGenerator()

    def send_message(
        self,
        db: Session,
        user_id: int,
        message: str,
        target_role_id: Optional[int],
    ) -> str:
        """Process a user message and return the assistant's response."""
        analysis = (
            db.query(Analysis)
            .filter(Analysis.user_id == user_id)
            .order_by(Analysis.created_at.desc())
            .first()
        )
        target_role = db.get(TargetRole, target_role_id) if target_role_id else None
        history = self.get_history(db, user_id, target_role_id, limit=_MAX_HISTORY_MESSAGES)
        system_prompt = self._build_system_prompt(analysis, target_role)

        history_text = "\n".join(f"{m.role.upper()}: {m.content}" for m in history)

        prompt = f"""{system_prompt}

RECENT CONVERSATION:
{history_text or '(no previous messages)'}

USER: {message}

Respond as the AI mentor (under 150 words, grounded in the data above):"""

        result = self.llm.generate(prompt)
        response_text = (
            result.text if result.success
            else "I couldn't generate a response right now — please try again."
        )

        db.add(ChatMessage(user_id=user_id, target_role_id=target_role_id, role="user", content=message))
        db.add(ChatMessage(user_id=user_id, target_role_id=target_role_id, role="assistant", content=response_text))
        db.commit()
        return response_text

    def get_history(
        self,
        db: Session,
        user_id: int,
        target_role_id: Optional[int],
        limit: int = 50,
    ) -> List[Any]:
        """Return recent chat messages ordered by created_at ascending."""
        query = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
        if target_role_id is not None:
            query = query.filter(ChatMessage.target_role_id == target_role_id)
        else:
            query = query.filter(ChatMessage.target_role_id.is_(None))
        return query.order_by(ChatMessage.created_at.desc()).limit(limit).all()[::-1]

    def clear_history(self, db: Session, user_id: int, target_role_id: Optional[int]) -> None:
        """Delete all chat messages for a user (and optional target role)."""
        query = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
        if target_role_id is not None:
            query = query.filter(ChatMessage.target_role_id == target_role_id)
        else:
            query = query.filter(ChatMessage.target_role_id.is_(None))
        query.delete()
        db.commit()

    def _build_system_prompt(self, analysis: Optional[Any], target_role: Optional[Any]) -> str:
        """Compose the grounded system prompt."""
        if analysis is None:
            return f"{_CHAT_SYSTEM_INSTRUCTION}\n\nNo analysis data available yet. Encourage the user to run their first analysis."

        breakdown = analysis.breakdown or {}
        flags = analysis.flags or {}

        def _score(key):
            val = breakdown.get(key, {})
            return val.get("raw_score", 0) if isinstance(val, dict) else 0

        green = ", ".join(flags.get("green_flags", [])) or "None identified"
        red = ", ".join(flags.get("red_flags", [])) or "None identified"

        context = f"""CANDIDATE PROFILE:
TPR Score: {analysis.tpr_score}/100 (confidence: {analysis.confidence_level})
Sub-scores: commit_quality={_score('commit_quality')}/100, pr_collaboration={_score('pr_collaboration')}/100, code_review={_score('code_review')}/100, consistency={_score('consistency')}/100, repo_depth={_score('repo_depth')}/100
Strengths: {green}
Areas to improve: {red}"""[:_MAX_CONTEXT_CHARS]

        if target_role:
            gap = target_role.latest_gap_analysis or {}
            missing = ", ".join(gap.get("missing_requirements", [])[:3]) or "Not yet analyzed"
            context += f"\n\nTARGET ROLE: {target_role.role_title}"
            if target_role.company_name:
                context += f" at {target_role.company_name}"
            context += f"\nKey gaps: {missing}"

        return f"{_CHAT_SYSTEM_INSTRUCTION}\n\n{context}"
