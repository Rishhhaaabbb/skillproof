# Task 5: Feature extractor — transforms raw GitHub data into a numeric feature vector
from typing import Any, Dict, List


class FeatureExtractor:
    """Transforms raw GitHub activity data into the canonical feature vector.

    The output feature order matches ``ml.feature_schema.FEATURE_NAMES`` so it
    can be passed directly to the trained logistic-regression model.
    """

    def extract(self, raw_data: Dict[str, Any]) -> Dict[str, float]:
        """Produce the full feature vector from raw GitHub data.

        Args:
            raw_data: Dict returned by GitHubFetcher containing profile,
                      repositories, commits, pull_requests, reviews, and issues.

        Returns:
            Dict mapping each feature name (from FEATURE_NAMES) to its
            computed numeric value.
        """
        pass

    def _compute_commit_features(self, commits: List[Dict[str, Any]]) -> Dict[str, float]:
        """Compute commit-related features (volume, frequency, message quality).

        Args:
            commits: Raw commit dicts from GitHubFetcher.

        Returns:
            Partial feature dict for commit features.
        """
        pass

    def _compute_pr_features(self, pull_requests: List[Dict[str, Any]]) -> Dict[str, float]:
        """Compute pull-request-related features (merge rate, size distribution).

        Args:
            pull_requests: Raw PR dicts from GitHubFetcher.

        Returns:
            Partial feature dict for PR features.
        """
        pass

    def _compute_review_features(self, reviews: List[Dict[str, Any]]) -> Dict[str, float]:
        """Compute code-review features (review count, approval rate).

        Args:
            reviews: Raw review dicts from GitHubFetcher.

        Returns:
            Partial feature dict for review features.
        """
        pass

    def _compute_repo_features(self, repositories: List[Dict[str, Any]]) -> Dict[str, float]:
        """Compute repository-level features (language diversity, star signal, readme quality).

        Args:
            repositories: Raw repo dicts from GitHubFetcher.

        Returns:
            Partial feature dict for repo features.
        """
        pass

    def _compute_consistency_features(self, commits: List[Dict[str, Any]]) -> Dict[str, float]:
        """Compute temporal consistency features (active days, streak proxy).

        Args:
            commits: Raw commit dicts used to derive activity calendar.

        Returns:
            Partial feature dict for consistency features.
        """
        pass
