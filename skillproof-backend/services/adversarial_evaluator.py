# Task 9: Adversarial evaluator — multi-pass skeptic/advocate/judge evaluation
"""
Three-pass evaluation using the same LLM in different roles:
  Pass 1 — Skeptic: argues the strongest honest case AGAINST readiness
  Pass 2 — Advocate: argues the strongest honest case FOR readiness
  Pass 3 — Judge: weighs both cases, produces a calibrated final verdict

This is 'multi-pass adversarial evaluation' — not multiple model vendors,
but three distinct prompted perspectives on the same evidence. Forces the
system to surface the strongest honest case for each position before
synthesizing, reducing single-pass confirmation bias.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from models.database import EvaluationVerdict
from services.llm_generator import LLMGenerator

logger = logging.getLogger(__name__)

_SKEPTIC_INSTRUCTION = """You are a rigorous technical reviewer evaluating a developer's GitHub evidence.
Your job: argue the STRONGEST HONEST CASE for why this candidate may NOT be production-ready for the described role.
Rules:
- Only cite evidence actually present in the data provided. Never invent commits, PRs, or projects.
- Be specific: reference actual scores and feature values.
- Keep your case under 150 words.
- Be honest, not cruel. Flag genuine gaps, not fabricated ones."""

_ADVOCATE_INSTRUCTION = """You are a developer advocate reviewing a candidate's GitHub evidence.
Your job: argue the STRONGEST HONEST CASE for why this candidate IS ready or shows strong potential for the described role.
Rules:
- Only cite evidence actually present in the data provided. Never invent achievements.
- Be specific: reference actual scores and feature values.
- Keep your case under 150 words.
- Be honest, not promotional. Surface genuine strengths only."""

_JUDGE_INSTRUCTION = """You are a neutral technical hiring judge. Two reviewers have evaluated the same developer.
Your job: weigh both cases, identify which points actually hold up against the evidence, and produce a calibrated final verdict.
Return ONLY valid JSON — no markdown, no explanation outside the JSON."""


class AdversarialEvaluator:
    """Runs three-pass adversarial evaluation to produce a calibrated EvaluationVerdict."""

    def __init__(self) -> None:
        self.llm = LLMGenerator()

    def run_evaluation(
        self,
        db: Session,
        user_id: int,
        target_role_id: int,
        analysis: Dict[str, Any],
        jd_text: str,
        top_repos: Optional[List[Dict]] = None,
        save: bool = True,
    ) -> Dict[str, Any]:
        """Execute skeptic → advocate → judge pipeline.

        Args:
            save: If False, skip persisting the verdict (used in tests when
                  no target_role row exists yet).
        """
        top_repos = top_repos or []
        evidence = self._build_evidence_block(analysis, top_repos)

        skeptic_case = self._call_skeptic(evidence, jd_text)
        advocate_case = self._call_advocate(evidence, jd_text)
        verdict = self._synthesize(skeptic_case, advocate_case, evidence)

        result = {
            "skeptic_case": skeptic_case,
            "advocate_case": advocate_case,
            **verdict,
        }

        if save:
            self.save_verdict(db, user_id, target_role_id, result)
        return result

    def _build_evidence_block(self, analysis: Dict[str, Any], top_repos: List[Dict]) -> str:
        """Format analysis data into a concise evidence block for prompts."""
        breakdown = analysis.get("breakdown", {})
        flags = analysis.get("flags", {})
        tpr = analysis.get("tpr_score", 0)
        confidence = analysis.get("confidence_level", "unknown")

        repo_lines = "\n".join(
            f"  - {r.get('name', 'unknown')} ({r.get('language', '?')}, {r.get('stars', 0)} stars)"
            for r in top_repos[:5]
        ) or "  - No repositories available"

        green = "\n".join(f"  ✓ {f}" for f in flags.get("green_flags", [])) or "  None"
        red = "\n".join(f"  ✗ {f}" for f in flags.get("red_flags", [])) or "  None"

        def _raw(key):
            val = breakdown.get(key, {})
            return val.get("raw_score", 0) if isinstance(val, dict) else 0

        return f"""CANDIDATE EVIDENCE:
TPR Score: {tpr}/100 (confidence: {confidence})
Sub-scores: commit_quality={_raw('commit_quality')}/100, pr_collaboration={_raw('pr_collaboration')}/100, code_review={_raw('code_review')}/100, consistency={_raw('consistency')}/100, repo_depth={_raw('repo_depth')}/100

GREEN FLAGS (strengths):
{green}

RED FLAGS (gaps):
{red}

TOP REPOSITORIES:
{repo_lines}"""

    def _call_skeptic(self, evidence: str, jd_text: str) -> str:
        prompt = f"""{evidence}

JOB DESCRIPTION (abbreviated):
{jd_text[:800]}

Write your skeptic case now (under 150 words, cite only evidence above):"""
        result = self.llm.generate(prompt, system_instruction=_SKEPTIC_INSTRUCTION)
        if result.success:
            return result.text
        logger.warning("Skeptic call failed: %s", result.error_message)
        return f"Skeptic analysis unavailable ({result.error_type})."

    def _call_advocate(self, evidence: str, jd_text: str) -> str:
        prompt = f"""{evidence}

JOB DESCRIPTION (abbreviated):
{jd_text[:800]}

Write your advocate case now (under 150 words, cite only evidence above):"""
        result = self.llm.generate(prompt, system_instruction=_ADVOCATE_INSTRUCTION)
        if result.success:
            return result.text
        logger.warning("Advocate call failed: %s", result.error_message)
        return f"Advocate analysis unavailable ({result.error_type})."

    def _synthesize(self, skeptic_case: str, advocate_case: str, evidence: str) -> Dict[str, Any]:
        prompt = f"""Two reviewers evaluated the same developer. Weigh both cases and produce a calibrated verdict.

EVIDENCE SUMMARY:
{evidence}

SKEPTIC CASE:
{skeptic_case}

ADVOCATE CASE:
{advocate_case}

Return ONLY this JSON (no markdown fences):
{{
  "final_verdict": "2-3 sentence balanced verdict citing the evidence",
  "confidence": <integer 0-100>,
  "surviving_skeptic_points": ["point1", "point2"],
  "surviving_advocate_points": ["point1", "point2"]
}}"""
        result = self.llm.generate_json(prompt, system_instruction=_JUDGE_INSTRUCTION)
        if result.success and result.data:
            return {
                "final_verdict": result.data.get("final_verdict", "Verdict unavailable."),
                "confidence": float(result.data.get("confidence", 50)),
                "surviving_skeptic_points": result.data.get("surviving_skeptic_points", []),
                "surviving_advocate_points": result.data.get("surviving_advocate_points", []),
            }
        logger.warning("Judge synthesis failed: %s", result.error_message)
        return {
            "final_verdict": "Verdict temporarily unavailable — please re-analyze.",
            "confidence": 0.0,
            "surviving_skeptic_points": [],
            "surviving_advocate_points": [],
        }

    def save_verdict(
        self,
        db: Session,
        user_id: int,
        target_role_id: int,
        verdict: Dict[str, Any],
    ) -> None:
        """Persist verdict to EvaluationVerdict table."""
        try:
            ev = EvaluationVerdict(
                user_id=user_id,
                target_role_id=target_role_id,
                skeptic_case=verdict.get("skeptic_case"),
                advocate_case=verdict.get("advocate_case"),
                final_verdict=verdict.get("final_verdict"),
                confidence=verdict.get("confidence"),
                surviving_skeptic_points=verdict.get("surviving_skeptic_points", []),
                surviving_advocate_points=verdict.get("surviving_advocate_points", []),
            )
            db.add(ev)
            db.commit()
        except Exception as exc:
            logger.error("Failed to save verdict: %s", exc)
            db.rollback()
