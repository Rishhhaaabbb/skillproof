# Task 14: Comparison service — before/after analysis diff
"""
Computes a structured diff between two Analysis rows to show a candidate
how their GitHub profile improved after completing assigned tasks.

The comparison is persisted to AnalysisComparison and exposed via
GET /api/target-roles/{id}/comparison.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from models.database import Analysis, AnalysisComparison, TargetRole

logger = logging.getLogger(__name__)


class ComparisonService:
    """Diffs two analyses to show progress toward a target role."""

    def compare(
        self,
        db: Session,
        user_id: int,
        target_role_id: int,
        before_analysis_id: int,
        after_analysis_id: int,
    ) -> Dict[str, Any]:
        """Diff two analyses and persist an AnalysisComparison row."""
        before = db.get(Analysis, before_analysis_id)
        after = db.get(Analysis, after_analysis_id)
        role = db.get(TargetRole, target_role_id)

        if not before or not after:
            logger.warning(
                "Comparison failed: before=%s after=%s",
                before_analysis_id, after_analysis_id,
            )
            return {"error": "One or both analysis records not found"}

        before_flags = (before.flags or {}).get("red_flags", [])
        after_flags = (after.flags or {}).get("red_flags", [])
        flag_diff = self._diff_flags(before_flags, after_flags)

        before_gap: Dict[str, Any] = {}
        after_gap: Dict[str, Any] = {}
        if role:
            before_gap = _extract_gap(before, role)
            after_gap = _extract_gap(after, role)

        newly_matched = self._diff_requirements(
            before_gap.get("missing_requirements", []),
            after_gap.get("missing_requirements", []),
        )

        score_delta = (after.tpr_score or 0) - (before.tpr_score or 0)

        comp = AnalysisComparison(
            user_id=user_id,
            target_role_id=target_role_id,
            before_analysis_id=before_analysis_id,
            after_analysis_id=after_analysis_id,
            before_readiness=before.tpr_score,
            after_readiness=after.tpr_score,
            newly_matched=newly_matched,
            resolved_flags=flag_diff["resolved"],
        )
        db.add(comp)
        db.commit()
        db.refresh(comp)

        return {
            "comparison_id": comp.id,
            "before_tpr_score": before.tpr_score,
            "after_tpr_score": after.tpr_score,
            "score_delta": round(score_delta, 1),
            "newly_matched": newly_matched,
            "resolved_flags": flag_diff["resolved"],
            "remaining_flags": flag_diff["remaining"],
            "before_readiness": before.tpr_score,
            "after_readiness": after.tpr_score,
        }

    def get_latest_comparison(
        self, db: Session, user_id: int, target_role_id: int
    ) -> Optional[Dict[str, Any]]:
        """Return the most recent comparison for a user+role, or None."""
        comp = (
            db.query(AnalysisComparison)
            .filter(
                AnalysisComparison.user_id == user_id,
                AnalysisComparison.target_role_id == target_role_id,
            )
            .order_by(AnalysisComparison.created_at.desc())
            .first()
        )
        if not comp:
            return None
        return {
            "comparison_id": comp.id,
            "before_readiness": comp.before_readiness,
            "after_readiness": comp.after_readiness,
            "score_delta": round(
                (comp.after_readiness or 0) - (comp.before_readiness or 0), 1
            ),
            "newly_matched": comp.newly_matched or [],
            "resolved_flags": comp.resolved_flags or [],
            "created_at": comp.created_at.isoformat(),
        }

    def _diff_flags(
        self, before_flags: List[str], after_flags: List[str]
    ) -> Dict[str, List[str]]:
        """Return resolved (gone) and remaining (still present) red flags."""
        before_set = set(before_flags)
        after_set = set(after_flags)
        return {
            "resolved": sorted(before_set - after_set),
            "remaining": sorted(after_set),
        }

    def _diff_requirements(
        self,
        before_missing: List[str],
        after_missing: List[str],
    ) -> List[str]:
        """Requirements that were missing before but are no longer missing after."""
        before_set = set(before_missing)
        after_set = set(after_missing)
        return sorted(before_set - after_set)


def _extract_gap(analysis: Analysis, role: TargetRole) -> Dict[str, Any]:
    """Extract gap analysis from a TargetRole's latest_gap_analysis."""
    if role.latest_gap_analysis:
        return role.latest_gap_analysis
    return {}
