# Task 9: Interview agent — generates targeted technical scenarios
"""
Generates personalized verification scenarios grounded in the candidate's
actual GitHub repos — not generic algorithm questions.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from models.database import VerificationSession
from services.llm_generator import LLMGenerator

logger = logging.getLogger(__name__)

_SCENARIO_INSTRUCTION = """You are a senior engineer generating a targeted technical verification scenario.
Rules:
- Ground the scenario in ONE specific repo from the candidate's actual repository list.
- Do NOT ask generic algorithm or leetcode-style questions.
- The scenario should probe real engineering judgment: architecture, trade-offs, debugging, or code quality decisions.
- Keep the scenario concise (2-4 sentences).
- Return ONLY valid JSON — no markdown fences."""

_EVALUATION_INSTRUCTION = """You are a senior engineer evaluating a candidate's response to a technical scenario.
Rules:
- Score objectively based on depth, specificity, and engineering judgment shown.
- A score of 70+ means the candidate demonstrated solid understanding.
- Keep reasoning under 100 words.
- Return ONLY valid JSON — no markdown fences."""


class InterviewAgent:
    """Generates personalized verification scenarios and evaluates responses."""

    def __init__(self) -> None:
        self.llm = LLMGenerator()

    def generate_scenario(
        self,
        db: Session,
        user_id: int,
        target_role_id: int,
        analysis: Dict[str, Any],
        top_repos: Optional[List[Dict]] = None,
        jd_text: str = "",
    ) -> Dict[str, Any]:
        """Generate a scenario grounded in the candidate's actual repos."""
        top_repos = top_repos or []
        repo_summary = "\n".join(
            f"- {r.get('name')}: {r.get('description') or 'No description'} ({r.get('language', '?')})"
            for r in top_repos[:5]
        ) or "- No repositories available"

        flags = analysis.get("flags", {})
        red_flags = flags.get("red_flags", [])
        jd_context = f"\nTarget role context:\n{jd_text[:500]}" if jd_text else ""

        prompt = f"""{jd_context}

CANDIDATE'S TOP REPOSITORIES:
{repo_summary}

RED FLAGS TO PROBE: {red_flags}

Pick ONE specific gap evidenced above and design a SHORT concrete scenario the candidate can answer in a few sentences or a short code snippet, grounded in one of their actual repos.

Return ONLY this JSON:
{{
  "target_repo": "exact repo name from list above",
  "scenario": "2-4 sentence scenario question",
  "what_a_strong_answer_shows": "what good understanding looks like",
  "difficulty": "easy|medium|hard"
}}"""

        result = self.llm.generate_json(prompt, system_instruction=_SCENARIO_INSTRUCTION)
        if result.success and result.data:
            return result.data
        logger.warning("Scenario generation failed: %s", result.error_message)
        return {
            "target_repo": top_repos[0].get("name") if top_repos else None,
            "scenario": "Describe the most complex technical challenge you solved in one of your projects and how you approached it.",
            "what_a_strong_answer_shows": "Structured thinking, awareness of trade-offs, and specific technical decisions.",
            "difficulty": "medium",
        }

    def evaluate_answer(
        self,
        db: Session,
        session_id: int,
        candidate_answer: str,
    ) -> Dict[str, Any]:
        """Evaluate a candidate's answer and update the VerificationSession row."""
        session = db.get(VerificationSession, session_id)
        if session is None:
            return {"quality_score": 0, "reasoning": "Session not found.", "pass_fail": "fail"}

        scenario = session.scenario or {}
        prompt = f"""SCENARIO: {scenario.get('scenario', 'N/A')}
WHAT A STRONG ANSWER SHOWS: {scenario.get('what_a_strong_answer_shows', 'N/A')}
CANDIDATE'S ANSWER: {candidate_answer}

Return ONLY this JSON:
{{
  "quality_score": <integer 0-100>,
  "reasoning": "1-2 sentences specific to this answer",
  "pass_fail": "pass|fail"
}}"""

        result = self.llm.generate_json(prompt, system_instruction=_EVALUATION_INSTRUCTION)
        if result.success and result.data:
            quality_score = float(result.data.get("quality_score", 50))
            reasoning = result.data.get("reasoning", "")
            pass_fail = result.data.get("pass_fail", "pass" if quality_score >= 60 else "fail")

            session.candidate_answer = candidate_answer
            session.quality_score = quality_score
            session.reasoning = reasoning
            db.commit()

            return {"quality_score": quality_score, "reasoning": reasoning, "pass_fail": pass_fail}

        logger.warning("Answer evaluation failed: %s", result.error_message)
        return {"quality_score": 50, "reasoning": "Evaluation temporarily unavailable.", "pass_fail": "pass"}

    def save_session(
        self,
        db: Session,
        user_id: int,
        target_role_id: Optional[int],
        scenario: Dict[str, Any],
    ) -> int:
        """Persist a new VerificationSession and return its id."""
        session = VerificationSession(
            user_id=user_id,
            target_role_id=target_role_id,
            scenario=scenario,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session.id
