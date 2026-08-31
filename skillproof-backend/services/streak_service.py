# Task 8: Streak service — tracks weekly coding streaks and awards milestones
"""
Computes and persists coding streaks from heatmap data.

Uses weekly granularity (not daily) because the GitHub fetcher's heatmap
is week-keyed. A 'streak' is the longest run of consecutive active weeks.
"""
from __future__ import annotations

import logging
from datetime import date
from typing import Any, Dict, List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.database import Milestone, User

logger = logging.getLogger(__name__)

# Milestone definitions: weeks_threshold -> (key, label)
_STREAK_MILESTONES = {
    4:  ("streak_4w",  "4-Week Active Streak"),
    13: ("streak_13w", "13-Week Active Streak"),
    26: ("streak_26w", "26-Week Active Streak"),
    52: ("streak_52w", "52-Week Active Streak"),
}


class StreakService:
    """Calculates and persists weekly coding streaks and milestone badges."""

    def update_streak(
        self,
        db: Session,
        user_id: int,
        heatmap: Dict[str, int],
    ) -> Dict[str, Any]:
        """Recompute streak from heatmap and persist to User row.

        Args:
            db:      Active SQLAlchemy session.
            user_id: Primary key of the User row.
            heatmap: 52-week dict {"YYYY-WNN": count} from GitHubFetcher.

        Returns:
            Dict with current_streak, longest_streak, new_milestones.
        """
        user = db.get(User, user_id)
        if user is None:
            return {"current_streak": 0, "longest_streak": 0, "new_milestones": []}

        sorted_weeks = sorted(heatmap.keys())

        # Current streak = consecutive active weeks counting backwards from most recent
        current_streak = 0
        for week in reversed(sorted_weeks):
            if heatmap.get(week, 0) > 0:
                current_streak += 1
            else:
                break

        # Longest streak = max run of consecutive active weeks
        longest = 0
        run = 0
        prev_idx = -2
        for i, week in enumerate(sorted_weeks):
            if heatmap.get(week, 0) > 0:
                if i == prev_idx + 1:
                    run += 1
                else:
                    run = 1
                longest = max(longest, run)
                prev_idx = i
            else:
                prev_idx = -2

        user.current_streak = current_streak
        user.longest_streak = max(longest, user.longest_streak or 0)
        user.last_streak_date = date.today()
        db.commit()

        new_milestones = self.check_and_award_milestones(db, user_id, current_streak)
        return {
            "current_streak": current_streak,
            "longest_streak": user.longest_streak,
            "new_milestones": new_milestones,
        }

    def check_and_award_milestones(
        self,
        db: Session,
        user_id: int,
        current_streak: int,
    ) -> List[str]:
        """Award streak milestones not yet earned. Returns list of newly awarded labels."""
        awarded = []
        for threshold, (key, label) in _STREAK_MILESTONES.items():
            if current_streak >= threshold:
                result = self._award_milestone(db, user_id, key, label)
                if result:
                    awarded.append(result)
        return awarded

    def check_behavior_milestones(
        self,
        db: Session,
        user_id: int,
        features: Dict[str, Any],
        is_first_analysis: bool = False,
    ) -> List[str]:
        """Award behavior-based milestones based on feature values."""
        awarded = []
        if is_first_analysis:
            m = self._award_milestone(db, user_id, "first_analysis", "First Analysis Run")
            if m:
                awarded.append(m)
        if features.get("pr_merge_rate", 0) > 0 and features.get("total_prs_365d", 0) >= 1:
            m = self._award_milestone(db, user_id, "first_pr", "First PR Merged")
            if m:
                awarded.append(m)
        if features.get("total_reviews_given_365d", 0) >= 10:
            m = self._award_milestone(db, user_id, "reviewer_10", "Reviewed 10 Pull Requests")
            if m:
                awarded.append(m)
        if features.get("distinct_languages_count", 0) >= 3:
            m = self._award_milestone(db, user_id, "multi_lang", "Multi-Language Developer")
            if m:
                awarded.append(m)
        if features.get("avg_repo_stars", 0) >= 5:
            m = self._award_milestone(db, user_id, "stars_earned", "Community Recognition (5+ Stars)")
            if m:
                awarded.append(m)
        return awarded

    def get_streak_summary(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Return streak summary for dashboard display."""
        user = db.get(User, user_id)
        if user is None:
            return {"current_streak": 0, "longest_streak": 0, "milestones": []}
        milestones = (
            db.query(Milestone)
            .filter(Milestone.user_id == user_id)
            .order_by(Milestone.earned_at.desc())
            .all()
        )
        return {
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "last_streak_date": str(user.last_streak_date) if user.last_streak_date else None,
            "milestones": [
                {"key": m.milestone_key, "label": m.milestone_label, "earned_at": str(m.earned_at)}
                for m in milestones
            ],
        }

    def _award_milestone(
        self, db: Session, user_id: int, key: str, label: str
    ) -> str | None:
        """Insert a milestone row if not already present. Returns label if newly awarded."""
        try:
            m = Milestone(user_id=user_id, milestone_key=key, milestone_label=label)
            db.add(m)
            db.commit()
            return label
        except IntegrityError:
            db.rollback()
            return None
