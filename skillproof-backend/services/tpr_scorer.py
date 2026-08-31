# Task 6: TPR (Technical Proficiency Rating) scorer — heuristic rule-based scoring
"""
Hand-set weighted scorer that maps the 28 canonical features onto a [0, 100]
Technical Proficiency Rating score.

Five sub-dimensions and weights:
    commit_quality   0.25
    pr_collaboration 0.25
    code_review      0.20
    consistency      0.20
    repo_depth       0.10

The weights are validated against the labeled dataset in evaluation/run_validation.py.
The stretch goal (Task 18) replaces these with learned weights from a logistic
regression trained on the same dataset.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from ml.feature_schema import FEATURE_NAMES

_WEIGHTS = {
    "commit_quality":   0.25,
    "pr_collaboration": 0.25,
    "code_review":      0.20,
    "consistency":      0.20,
    "repo_depth":       0.10,
}


class TPRScorer:
    """Computes the Technical Proficiency Rating using a rule-based heuristic."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def score(
        self, features: Dict[str, float]
    ) -> Tuple[float, str, Dict[str, Any]]:
        """Compute the TPR score and a breakdown of sub-dimension contributions.

        Args:
            features: Canonical feature dict from FeatureExtractor.extract_all_features().

        Returns:
            Tuple of:
              - tpr_score (float): Overall score in [0, 100], rounded to 1 dp.
              - confidence_level (str): 'high', 'medium', or 'low'.
              - breakdown (dict): Sub-dimension raw scores and weighted contributions.
        """
        sub_scores = {
            "commit_quality":   self._score_commit_quality(features),
            "pr_collaboration": self._score_pr_collaboration(features),
            "code_review":      self._score_code_review(features),
            "consistency":      self._score_consistency(features),
            "repo_depth":       self._score_repo_depth(features),
        }

        tpr_score = sum(
            sub_scores[dim] * _WEIGHTS[dim] for dim in _WEIGHTS
        )
        tpr_score = round(min(100.0, max(0.0, tpr_score)), 1)

        data_points = (
            features.get("total_commits_365d", 0.0)
            + features.get("total_prs_365d", 0.0)
            + features.get("total_reviews_given_365d", 0.0)
        )
        if data_points >= 50:
            confidence = "high"
        elif data_points >= 15:
            confidence = "medium"
        else:
            confidence = "low"

        breakdown = {
            dim: {
                "raw_score": round(sub_scores[dim], 1),
                "weight": _WEIGHTS[dim],
                "weighted": round(sub_scores[dim] * _WEIGHTS[dim], 2),
            }
            for dim in _WEIGHTS
        }
        breakdown["data_points"] = data_points

        return tpr_score, confidence, breakdown

    def generate_flags(
        self,
        features: Dict[str, float],
        breakdown: Dict[str, Any],
    ) -> Dict[str, List[str]]:
        """Identify behavioural green and red flags from features.

        Args:
            features:  Canonical feature dict.
            breakdown: Sub-dimension breakdown from :meth:`score`.

        Returns:
            Dict with 'green_flags' and 'red_flags' lists of human-readable strings.
        """
        green: List[str] = []
        red: List[str] = []

        # --- Green flags ---
        if features.get("pct_commits_conventional_format", 0) > 0.3:
            green.append("Uses Conventional Commits format")
        if features.get("pct_commits_with_body", 0) > 0.3:
            green.append("Writes descriptive commit messages")
        if features.get("pr_merge_rate", 0) > 0.7:
            green.append("High PR acceptance rate")
        if features.get("avg_pr_review_comments", 0) >= 2:
            green.append("PRs attract meaningful code review")
        if features.get("total_reviews_given_365d", 0) >= 10:
            green.append("Active code reviewer")
        if features.get("weeks_with_activity_52w", 0) >= 30:
            green.append("Consistent year-round contributor")
        if features.get("distinct_languages_count", 0) >= 3:
            green.append("Multi-language experience")
        if features.get("avg_repo_stars", 0) >= 5:
            green.append("Projects attract community interest")

        # --- Red flags ---
        if features.get("total_commits_365d", 0) < 10:
            red.append("Very low commit activity in the past year")
        if features.get("avg_commit_message_length", 0) < 15:
            red.append("Commit messages lack descriptive text")
        if features.get("total_prs_365d", 0) == 0:
            red.append("No pull requests found — limited collaboration evidence")
        if features.get("total_reviews_given_365d", 0) == 0:
            red.append("No code reviews found — limited peer collaboration")
        if features.get("weeks_with_activity_52w", 0) < 10:
            red.append("Sporadic contribution pattern")
        if features.get("distinct_languages_count", 0) <= 1:
            red.append("Limited language diversity")

        return {"green_flags": green, "red_flags": red}

    # ------------------------------------------------------------------
    # Sub-dimension scorers — each returns a value in [0, 100]
    # ------------------------------------------------------------------

    def _score_commit_quality(self, f: Dict[str, float]) -> float:
        score = 0.0

        # Volume signal (max 40 points)
        commits_365 = f.get("total_commits_365d", 0.0)
        if commits_365 >= 200:
            score += 40
        elif commits_365 >= 100:
            score += 30
        elif commits_365 >= 50:
            score += 20
        elif commits_365 >= 20:
            score += 10
        elif commits_365 >= 5:
            score += 5

        # Frequency signal (max 20 points)
        cpd = f.get("avg_commits_per_active_day", 0.0)
        if cpd >= 3:
            score += 20
        elif cpd >= 1.5:
            score += 15
        elif cpd >= 1.0:
            score += 10
        elif cpd > 0:
            score += 5

        # Message quality (max 20 points)
        msg_len = f.get("avg_commit_message_length", 0.0)
        if msg_len >= 50:
            score += 10
        elif msg_len >= 20:
            score += 5
        score += f.get("pct_commits_with_body", 0.0) * 5
        score += f.get("pct_commits_conventional_format", 0.0) * 5

        # Recent activity bonus (max 20 points)
        commits_90 = f.get("total_commits_90d", 0.0)
        if commits_90 >= 20:
            score += 20
        elif commits_90 >= 10:
            score += 15
        elif commits_90 >= 5:
            score += 10
        elif commits_90 >= 1:
            score += 5

        return min(100.0, score)

    def _score_pr_collaboration(self, f: Dict[str, float]) -> float:
        score = 0.0

        prs_365 = f.get("total_prs_365d", 0.0)
        if prs_365 >= 20:
            score += 40
        elif prs_365 >= 10:
            score += 30
        elif prs_365 >= 5:
            score += 20
        elif prs_365 >= 1:
            score += 10

        score += f.get("pr_merge_rate", 0.0) * 30

        avg_size = f.get("avg_pr_size_lines", 0.0)
        if 100 <= avg_size <= 500:
            score += 20
        elif 50 <= avg_size < 100:
            score += 15
        elif avg_size > 0:
            score += 10

        if f.get("avg_pr_review_comments", 0.0) >= 3:
            score += 10
        elif f.get("avg_pr_review_comments", 0.0) >= 1:
            score += 5

        return min(100.0, score)

    def _score_code_review(self, f: Dict[str, float]) -> float:
        score = 0.0

        reviews = f.get("total_reviews_given_365d", 0.0)
        if reviews >= 30:
            score += 60
        elif reviews >= 15:
            score += 45
        elif reviews >= 5:
            score += 30
        elif reviews >= 1:
            score += 15

        ratio = f.get("review_to_pr_ratio", 0.0)
        if ratio >= 1.0:
            score += 40
        elif ratio >= 0.5:
            score += 25
        elif ratio > 0:
            score += 10

        return min(100.0, score)

    def _score_consistency(self, f: Dict[str, float]) -> float:
        score = 0.0

        weeks = f.get("weeks_with_activity_52w", 0.0)
        if weeks >= 40:
            score += 50
        elif weeks >= 30:
            score += 40
        elif weeks >= 20:
            score += 30
        elif weeks >= 10:
            score += 20
        elif weeks >= 4:
            score += 10

        score += f.get("pct_weeks_active_52w", 0.0) * 30

        streak = f.get("longest_commit_streak_days", 0.0)
        if streak >= 90:
            score += 20
        elif streak >= 30:
            score += 15
        elif streak >= 14:
            score += 10
        elif streak >= 7:
            score += 5

        return min(100.0, score)

    def _score_repo_depth(self, f: Dict[str, float]) -> float:
        score = 0.0

        langs = f.get("distinct_languages_count", 0.0)
        if langs >= 5:
            score += 30
        elif langs >= 3:
            score += 20
        elif langs >= 2:
            score += 15
        elif langs >= 1:
            score += 10

        stars = f.get("avg_repo_stars", 0.0)
        if stars >= 100:
            score += 30
        elif stars >= 10:
            score += 20
        elif stars >= 1:
            score += 10

        score += f.get("pct_repos_with_readme", 0.0) * 20
        score += f.get("pct_repos_with_topics", 0.0) * 20

        return min(100.0, score)
