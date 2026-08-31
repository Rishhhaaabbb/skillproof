# Task 10: JD analyzer — gap analysis between candidate profile and job description
"""
Analyzes a job description against a candidate's GitHub analysis to produce:
- Matched requirements with specific evidence citations
- Missing requirements
- Recommended actions
- Readiness estimate (0-100)

Every matched requirement MUST cite a specific repo or skill tag as evidence.
If no real evidence exists, the requirement goes to missing_requirements.
This is the citation hallucination prevention mechanism.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from services.llm_generator import LLMGenerator
from utils.text_utils import clean_jd_text

logger = logging.getLogger(__name__)


class JDAnalyzer:
    """Produces evidence-grounded gap analysis between a JD and a candidate profile."""

    def __init__(self) -> None:
        self.llm = LLMGenerator()

    def analyze(
        self,
        jd_text: str,
        analysis: Dict[str, Any],
        top_repos: List[Dict] = None,
        skill_tags: List[Dict] = None,
    ) -> Dict[str, Any]:
        """Run full gap analysis and return structured result."""
        top_repos = top_repos or []
        skill_tags = skill_tags or []
        clean_jd = clean_jd_text(jd_text)

        valid_repo_names = {r.get("name", "") for r in top_repos}
        valid_tags = {t.get("tag", "").lower() for t in skill_tags}
        evidence_names = valid_repo_names | valid_tags

        tpr_score = analysis.get("tpr_score", 0)
        flags = analysis.get("flags", {})
        green_flags = flags.get("green_flags", [])
        red_flags = flags.get("red_flags", [])

        repo_summary = "\n".join(
            f"- {r.get('name')}: {r.get('description') or ''} ({r.get('language', '?')})"
            for r in top_repos[:8]
        ) or "- No repositories available"

        tag_summary = ", ".join(t.get("tag", "") for t in skill_tags[:15]) or "None"

        prompt = f"""Analyze this candidate's GitHub evidence against a job description.

JOB DESCRIPTION:
{clean_jd[:2000]}

CANDIDATE EVIDENCE:
TPR Score: {tpr_score}/100
Strengths: {green_flags}
Gaps: {red_flags}

REPOSITORIES:
{repo_summary}

SKILL TAGS: {tag_summary}

CRITICAL RULE: Every matched_requirement MUST cite a specific repo name or skill tag
from the evidence above as evidence_citation. If you cannot find real evidence for a
requirement, put it in missing_requirements instead. Never assert a match without
naming exactly which repo or skill tag proves it.

Return ONLY this JSON:
{{
  "matched_requirements": [
    {{"requirement": "...", "evidence_citation": "exact repo name or skill tag from above"}}
  ],
  "missing_requirements": ["..."],
  "recommended_actions": ["...", "...", "..."],
  "readiness_estimate": <integer 0-100>
}}"""

        result = self.llm.generate_json(prompt)

        if not result.success or not result.data:
            logger.warning("JD analysis failed: %s", result.error_message)
            return {
                "matched_requirements": [],
                "missing_requirements": [],
                "recommended_actions": ["Analysis temporarily unavailable — try again."],
                "readiness_estimate": int(tpr_score),
                "citation_hallucination_rate": 0.0,
            }

        data = result.data
        matched = data.get("matched_requirements", [])
        missing = list(data.get("missing_requirements", []))

        valid_matched = []
        invalid_count = 0
        for item in matched:
            citation = (item.get("evidence_citation") or "").strip()
            citation_lower = citation.lower()
            is_valid = any(
                citation_lower == name.lower()
                for name in evidence_names
                if name
            )
            if is_valid:
                valid_matched.append(item)
            else:
                missing.append(item.get("requirement", ""))
                invalid_count += 1

        total_citations = len(matched)
        hallucination_rate = (invalid_count / total_citations) if total_citations > 0 else 0.0

        if hallucination_rate > 0:
            logger.info(
                "Citation validation: %d/%d citations hallucinated (%.0f%%)",
                invalid_count, total_citations, hallucination_rate * 100,
            )

        return {
            "matched_requirements": valid_matched,
            "missing_requirements": [r for r in missing if r],
            "recommended_actions": data.get("recommended_actions", []),
            "readiness_estimate": int(data.get("readiness_estimate", tpr_score)),
            "citation_hallucination_rate": round(hallucination_rate, 3),
        }
