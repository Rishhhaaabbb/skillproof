# Task 6: TPR (Technical Proficiency Rating) scorer — heuristic rule-based scoring
from typing import Any, Dict, Tuple


class TPRScorer:
    """Computes the Technical Proficiency Rating using a rule-based heuristic.

    The TPR score is a float in [0, 100] that reflects the breadth and depth
    of a developer's GitHub behaviour independent of any specific job description.
    It is designed to be explainable: each sub-dimension contributes a labelled
    portion to the final score.
    """

    def score(self, features: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """Compute the TPR score and a breakdown of sub-dimension contributions.

        Args:
            features: Canonical feature dict from FeatureExtractor.extract().

        Returns:
            A tuple of:
              - tpr_score (float): Overall score in [0, 100].
              - breakdown (dict): Maps sub-dimension labels (e.g. 'commit_quality',
                'pr_collaboration', 'code_review', 'consistency', 'repo_depth')
                to their individual scores and weights.
        """
        pass

    def generate_flags(self, features: Dict[str, float], breakdown: Dict[str, Any]) -> list:
        """Identify behavioural red-flags from features and sub-scores.

        Red-flags are short human-readable strings describing patterns that may
        concern a technical reviewer (e.g. 'No code reviews found',
        'Commit messages lack descriptive text').

        Args:
            features:  Canonical feature dict.
            breakdown: Sub-dimension breakdown from :meth:`score`.

        Returns:
            List of red-flag strings (may be empty).
        """
        pass

    def generate_heatmap_data(self, commits: list) -> Dict[str, int]:
        """Build a contribution-calendar dict for the activity heatmap.

        Args:
            commits: Raw commit list from GitHubFetcher.

        Returns:
            Dict mapping ISO date strings (``YYYY-MM-DD``) to commit counts
            for the last 52 weeks.
        """
        pass
