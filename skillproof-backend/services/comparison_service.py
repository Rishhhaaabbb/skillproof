# Task 14: Comparison service — diffs two analyses to show progress over time
from typing import Any, Dict

from sqlalchemy.orm import Session


class ComparisonService:
    """Computes a structured diff between a before and after Analysis.

    Used to show candidates how their GitHub profile has improved relative to
    a target role's requirements after completing assigned tasks.
    """

    def compare(
        self,
        db: Session,
        user_id: int,
        target_role_id: int,
        before_analysis_id: int,
        after_analysis_id: int,
    ) -> Dict[str, Any]:
        """Diff two analyses and persist an AnalysisComparison row.

        Args:
            db:                  Active SQLAlchemy session.
            user_id:             Primary key of the User.
            target_role_id:      Primary key of the TargetRole.
            before_analysis_id:  Primary key of the earlier Analysis.
            after_analysis_id:   Primary key of the later Analysis.

        Returns:
            Dict with:
              - 'before_readiness': float
              - 'after_readiness': float
              - 'score_delta': float (positive = improvement)
              - 'newly_matched': list of skills now demonstrated
              - 'resolved_flags': list of flags that no longer appear
              - 'remaining_flags': list of flags still present
              - 'comparison_id': int pk of the saved AnalysisComparison row
        """
        pass

    def _diff_flags(self, before_flags: list, after_flags: list) -> Dict[str, list]:
        """Return sets of resolved and remaining flags.

        Args:
            before_flags: Flag list from the earlier analysis.
            after_flags:  Flag list from the later analysis.

        Returns:
            Dict with 'resolved' and 'remaining' lists.
        """
        pass

    def _diff_skills(
        self,
        before_features: Dict[str, Any],
        after_features: Dict[str, Any],
        jd_requirements: Dict[str, Any],
    ) -> list:
        """Identify skills present in after_features but absent in before_features.

        Args:
            before_features: Feature dict from the earlier analysis.
            after_features:  Feature dict from the later analysis.
            jd_requirements: Structured JD requirements for context.

        Returns:
            List of newly matched skill strings.
        """
        pass
