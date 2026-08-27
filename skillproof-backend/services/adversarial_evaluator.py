# Task 9: Adversarial evaluator — skeptic/advocate debate to produce final verdict
from typing import Any, Dict

from sqlalchemy.orm import Session


class AdversarialEvaluator:
    """Runs a two-sided debate (skeptic vs. advocate) to produce an EvaluationVerdict.

    The skeptic LLM call challenges the candidate's GitHub evidence against the
    JD requirements; the advocate LLM call defends it.  A synthesis call
    produces a balanced final verdict with surviving points from each side.
    """

    def run_evaluation(
        self,
        db: Session,
        user_id: int,
        target_role_id: int,
        analysis: Dict[str, Any],
        jd_text: str,
    ) -> Dict[str, Any]:
        """Execute the full skeptic → advocate → synthesis pipeline.

        Args:
            db:             Active SQLAlchemy session.
            user_id:        Primary key of the User.
            target_role_id: Primary key of the TargetRole.
            analysis:       Latest analysis dict (features, breakdown, flags).
            jd_text:        Cleaned job description text.

        Returns:
            Dict with 'skeptic_case', 'advocate_case', 'final_verdict',
            'confidence', 'surviving_skeptic_points', 'surviving_advocate_points'.
        """
        pass

    def _call_skeptic(self, analysis: Dict[str, Any], jd_text: str) -> str:
        """Construct and send the skeptic prompt to the LLM.

        Args:
            analysis: Analysis dict.
            jd_text:  Cleaned job description text.

        Returns:
            Raw LLM response string representing the skeptic case.
        """
        pass

    def _call_advocate(self, analysis: Dict[str, Any], jd_text: str) -> str:
        """Construct and send the advocate prompt to the LLM.

        Args:
            analysis: Analysis dict.
            jd_text:  Cleaned job description text.

        Returns:
            Raw LLM response string representing the advocate case.
        """
        pass

    def _synthesize(self, skeptic_case: str, advocate_case: str) -> Dict[str, Any]:
        """Synthesize the two cases into a balanced final verdict.

        Args:
            skeptic_case:  Raw skeptic LLM output.
            advocate_case: Raw advocate LLM output.

        Returns:
            Dict with 'final_verdict', 'confidence', 'surviving_skeptic_points',
            'surviving_advocate_points'.
        """
        pass

    def save_verdict(self, db: Session, user_id: int, target_role_id: int, verdict: Dict[str, Any]) -> None:
        """Persist the verdict as an EvaluationVerdict row.

        Args:
            db:             Active SQLAlchemy session.
            user_id:        Primary key of the User.
            target_role_id: Primary key of the TargetRole.
            verdict:        Dict returned by :meth:`run_evaluation`.
        """
        pass
