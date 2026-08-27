# Task 8: Streak service — tracks daily coding streaks and awards milestones
from datetime import date
from typing import Any, Dict, List

from sqlalchemy.orm import Session


class StreakService:
    """Calculates and persists daily coding streaks for a user.

    A streak increments when the user has at least one commit on consecutive
    calendar days.  Milestones are awarded at pre-defined streak thresholds.
    """

    MILESTONE_THRESHOLDS: Dict[int, str] = {
        7: "7-Day Streak",
        30: "30-Day Streak",
        90: "90-Day Streak",
        365: "365-Day Streak",
    }

    def update_streak(self, db: Session, user_id: int, commit_dates: List[date]) -> Dict[str, Any]:
        """Recompute and persist the user's current and longest streak.

        Args:
            db:           Active SQLAlchemy session.
            user_id:      Primary key of the User row to update.
            commit_dates: List of dates on which the user made at least one commit.

        Returns:
            Dict with 'current_streak', 'longest_streak', and 'new_milestones'
            (list of milestone labels just earned this run).
        """
        pass

    def check_and_award_milestones(self, db: Session, user_id: int, current_streak: int) -> List[str]:
        """Award any streak milestones the user has not yet earned.

        Args:
            db:             Active SQLAlchemy session.
            user_id:        Primary key of the User row.
            current_streak: The freshly computed current streak value.

        Returns:
            List of milestone labels that were newly awarded during this call.
        """
        pass

    def get_streak_summary(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Return the current streak summary for display on the dashboard.

        Args:
            db:      Active SQLAlchemy session.
            user_id: Primary key of the User row.

        Returns:
            Dict with 'current_streak', 'longest_streak', 'last_streak_date',
            and 'milestones' (list of earned milestone dicts).
        """
        pass
