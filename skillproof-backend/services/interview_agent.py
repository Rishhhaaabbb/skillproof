# Task 9: Interview agent — generates targeted technical scenarios and evaluates responses
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session


class InterviewAgent:
    """Generates role-specific technical interview scenarios and evaluates candidate answers.

    Scenarios are grounded in the user's actual GitHub evidence so questions
    probe real work rather than hypothetical knowledge.
    """

    def generate_scenario(
        self,
        db: Session,
        user_id: int,
        target_role_id: int,
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate a targeted technical scenario for a verification session.

        Args:
            db:             Active SQLAlchemy session.
            user_id:        Primary key of the User.
            target_role_id: Primary key of the TargetRole.
            analysis:       Latest analysis dict (features, breakdown, flags).

        Returns:
            Scenario dict with 'question', 'context' (GitHub evidence cited),
            'expected_signals', and 'difficulty'.
        """
        pass

    def evaluate_answer(
        self,
        db: Session,
        session_id: int,
        candidate_answer: str,
    ) -> Dict[str, Any]:
        """Evaluate a candidate's free-text answer against the scenario.

        Args:
            db:               Active SQLAlchemy session.
            session_id:       Primary key of the VerificationSession row.
            candidate_answer: The candidate's submitted answer text.

        Returns:
            Dict with 'quality_score' (float 0-10), 'reasoning' (explanation),
            and 'pass_fail' ('pass' | 'fail').
        """
        pass

    def save_session(
        self,
        db: Session,
        user_id: int,
        target_role_id: Optional[int],
        scenario: Dict[str, Any],
    ) -> int:
        """Persist a new VerificationSession row and return its id.

        Args:
            db:             Active SQLAlchemy session.
            user_id:        Primary key of the User.
            target_role_id: Optional primary key of the TargetRole.
            scenario:       Generated scenario dict to store as JSON.

        Returns:
            The integer id of the newly created VerificationSession row.
        """
        pass
