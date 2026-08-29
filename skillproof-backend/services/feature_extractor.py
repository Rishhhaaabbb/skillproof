# Task 5: Feature extractor — transforms raw GitHub data into a numeric feature vector
"""Feature extraction pipeline.

Transforms the raw dict returned by GitHubFetcher into the canonical 28-feature
vector defined in ml.feature_schema.FEATURE_NAMES.

Design decisions:
- Every method returns 0.0 for features it cannot compute (no None values, no
  exceptions propagate to callers).
- Feature names are hard-coded to match FEATURE_NAMES exactly — any rename in
  feature_schema.py must be mirrored here.
- Known limitations are documented inline:
    * pct_reviews_requesting_changes: not available from search API
    * has_pinned_repos: not available in PyGithub free tier
    * issue features: not fetched to conserve API quota
"""
from __future__ import annotations

import logging
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Regex for Conventional Commits format  (feat:, fix(scope):, etc.)
_CONVENTIONAL_RE = re.compile(
    r"^(feat|fix|docs|style|refactor|test|chore|perf|ci|build)(\(.+\))?:",
    re.IGNORECASE,
)

# Keywords scanned in commit messages for skill tag extraction
_SKILL_KEYWORDS = [
    "docker", "kubernetes", "k8s", "ci", "cd", "pipeline",
    "api", "graphql", "sql", "postgres", "redis",
    "aws", "gcp", "azure", "terraform",
    "typescript", "react", "vue", "angular",
    "fastapi", "django", "flask", "spring", "rails",
]


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _to_aware(dt: Any) -> Optional[datetime]:
    """Convert a naive or aware datetime (or None) to UTC-aware."""
    if dt is None:
        return None
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    return None


class FeatureExtractor:
    """Transforms raw GitHub activity data into the canonical feature vector."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_all_features(self, github_data: Dict[str, Any]) -> Dict[str, float]:
        """Produce the full 28-feature vector from raw GitHub data.

        Args:
            github_data: Dict returned by GitHubFetcher.get_user_data().

        Returns:
            Dict mapping every FEATURE_NAMES entry to a float value.
            Always complete — missing sections produce 0.0 values.
        """
        commits = github_data.get("commits") or []
        pull_requests = github_data.get("pull_requests") or []
        code_reviews = github_data.get("code_reviews") or []
        repos = github_data.get("repos") or []
        heatmap = github_data.get("heatmap") or {}

        features: Dict[str, float] = {}
        features.update(self._commit_features(commits))
        features.update(self._pr_features(pull_requests))
        features.update(self._review_features(code_reviews, pull_requests))
        features.update(self._repo_features(repos))
        features.update(self._consistency_features(heatmap))
        features.update(self._issue_features(commits, pull_requests))
        return features

    def extract_skill_tags(self, github_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract technology/skill tags from repos and commit messages.

        Args:
            github_data: Dict returned by GitHubFetcher.get_user_data().

        Returns:
            List of {"tag": str, "confidence": float, "source": str} dicts,
            sorted by confidence descending, deduplicated by tag name.
        """
        repos = github_data.get("repos") or []
        commits = github_data.get("commits") or []

        # --- Language tags from repo primary language ---
        lang_counter: Counter = Counter()
        for repo in repos:
            lang = repo.get("language")
            if lang:
                lang_counter[lang] += 1

        lang_tags: Dict[str, Dict[str, Any]] = {}
        for lang, count in lang_counter.items():
            confidence = 1.0 if count >= 3 else (0.7 if count == 2 else 0.4)
            lang_tags[lang.lower()] = {
                "tag": lang,
                "confidence": confidence,
                "source": "repo_language",
            }

        # --- Topic tags ---
        topic_tags: Dict[str, Dict[str, Any]] = {}
        for repo in repos:
            for topic in repo.get("topics") or []:
                key = topic.lower()
                if key not in topic_tags:
                    topic_tags[key] = {
                        "tag": topic,
                        "confidence": 0.8,
                        "source": "repo_topic",
                    }

        # --- Commit message keyword tags ---
        keyword_counter: Counter = Counter()
        all_messages = " ".join(
            (c.get("message") or "").lower() for c in commits
        )
        for kw in _SKILL_KEYWORDS:
            count = all_messages.count(kw)
            if count >= 3:
                keyword_counter[kw] = count

        kw_tags: Dict[str, Dict[str, Any]] = {
            kw: {"tag": kw, "confidence": 0.6, "source": "commit_keyword"}
            for kw in keyword_counter
        }

        # --- Merge, deduplicate (keep highest confidence per tag) ---
        merged: Dict[str, Dict[str, Any]] = {}
        for source_dict in (lang_tags, topic_tags, kw_tags):
            for key, entry in source_dict.items():
                if key not in merged or entry["confidence"] > merged[key]["confidence"]:
                    merged[key] = entry

        return sorted(merged.values(), key=lambda x: x["confidence"], reverse=True)

    # ------------------------------------------------------------------
    # Private feature computation methods
    # ------------------------------------------------------------------

    def _commit_features(self, commits: List[Dict[str, Any]]) -> Dict[str, float]:
        now = _now_utc()
        cutoff_90 = now - timedelta(days=90)
        cutoff_365 = now - timedelta(days=365)

        commits_90: List[Dict] = []
        commits_365: List[Dict] = []
        for c in commits:
            dt = _to_aware(c.get("date"))
            if dt is None:
                continue
            if dt >= cutoff_365:
                commits_365.append(c)
            if dt >= cutoff_90:
                commits_90.append(c)

        active_days_90 = len({
            _to_aware(c["date"]).date()
            for c in commits_90
            if _to_aware(c.get("date")) is not None
        })
        active_days_365 = len({
            _to_aware(c["date"]).date()
            for c in commits_365
            if _to_aware(c.get("date")) is not None
        })

        total_365 = float(len(commits_365))
        total_90 = float(len(commits_90))

        all_messages = [c.get("message") or "" for c in commits]
        avg_msg_len = (
            float(sum(len(m.strip()) for m in all_messages) / len(all_messages))
            if all_messages else 0.0
        )
        pct_with_body = (
            float(sum(1 for m in all_messages if "\n" in m) / len(all_messages))
            if all_messages else 0.0
        )
        pct_conventional = (
            float(
                sum(1 for m in all_messages if _CONVENTIONAL_RE.match(m))
                / len(all_messages)
            )
            if all_messages else 0.0
        )

        return {
            "total_commits_90d": total_90,
            "total_commits_365d": total_365,
            "active_days_90d": float(active_days_90),
            "active_days_365d": float(active_days_365),
            "avg_commits_per_active_day": total_365 / max(active_days_365, 1),
            "avg_commit_message_length": avg_msg_len,
            "pct_commits_with_body": pct_with_body,
            "pct_commits_conventional_format": pct_conventional,
        }

    def _pr_features(self, pull_requests: List[Dict[str, Any]]) -> Dict[str, float]:
        now = _now_utc()
        cutoff_90 = now - timedelta(days=90)
        cutoff_365 = now - timedelta(days=365)

        total = len(pull_requests)
        if total == 0:
            return {
                "total_prs_90d": 0.0,
                "total_prs_365d": 0.0,
                "pr_merge_rate": 0.0,
                "avg_pr_size_lines": 0.0,
                "avg_pr_review_comments": 0.0,
            }

        prs_90 = sum(
            1 for pr in pull_requests
            if _to_aware(pr.get("created_at")) is not None
            and _to_aware(pr["created_at"]) >= cutoff_90
        )
        prs_365 = sum(
            1 for pr in pull_requests
            if _to_aware(pr.get("created_at")) is not None
            and _to_aware(pr["created_at"]) >= cutoff_365
        )
        merged = sum(1 for pr in pull_requests if pr.get("merged"))
        pr_sizes = [
            pr.get("additions", 0) + pr.get("deletions", 0)
            for pr in pull_requests
        ]
        review_comments = [pr.get("review_comments", 0) for pr in pull_requests]

        return {
            "total_prs_90d": float(prs_90),
            "total_prs_365d": float(prs_365),
            "pr_merge_rate": float(merged) / max(total, 1),
            "avg_pr_size_lines": float(sum(pr_sizes)) / max(len(pr_sizes), 1),
            "avg_pr_review_comments": float(sum(review_comments)) / max(len(review_comments), 1),
        }

    def _review_features(
        self,
        code_reviews: List[Dict[str, Any]],
        pull_requests: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        # NOTE: review timestamps not available from GitHub search API.
        # Using total count as proxy for both 90d and 365d metrics.
        review_count = float(min(len(code_reviews), 50))
        pr_count = max(len(pull_requests), 1)

        return {
            "total_reviews_given_90d": review_count,
            "total_reviews_given_365d": review_count,
            # pct_reviews_requesting_changes: not available from search API
            "pct_reviews_requesting_changes": 0.0,
            "review_to_pr_ratio": review_count / pr_count,
        }

    def _repo_features(self, repos: List[Dict[str, Any]]) -> Dict[str, float]:
        if not repos:
            return {
                "distinct_languages_count": 0.0,
                "avg_repo_stars": 0.0,
                "pct_repos_with_readme": 0.0,
                "pct_repos_with_topics": 0.0,
                # has_pinned_repos: not exposed by PyGithub free-tier API
                "has_pinned_repos": 0.0,
            }

        languages = {r.get("language") for r in repos if r.get("language")}
        stars = [r.get("stars", 0) for r in repos]
        with_readme = sum(1 for r in repos if r.get("has_readme"))
        with_topics = sum(1 for r in repos if r.get("topics"))
        n = len(repos)

        return {
            "distinct_languages_count": float(len(languages)),
            "avg_repo_stars": float(sum(stars)) / max(n, 1),
            "pct_repos_with_readme": float(with_readme) / max(n, 1),
            "pct_repos_with_topics": float(with_topics) / max(n, 1),
            "has_pinned_repos": 0.0,
        }

    def _consistency_features(self, heatmap: Dict[str, int]) -> Dict[str, float]:
        if not heatmap:
            return {
                "longest_commit_streak_days": 0.0,
                "weeks_with_activity_52w": 0.0,
                "pct_weeks_active_52w": 0.0,
            }

        values = list(heatmap.values())
        total_weeks = len(values)
        active_weeks = sum(1 for v in values if v > 0)

        # Longest consecutive streak of active weeks (× 7 to approximate days)
        longest = 0
        current = 0
        for v in values:
            if v > 0:
                current += 1
                longest = max(longest, current)
            else:
                current = 0

        return {
            "longest_commit_streak_days": float(longest * 7),
            "weeks_with_activity_52w": float(active_weeks),
            "pct_weeks_active_52w": float(active_weeks) / max(total_weeks, 1),
        }

    def _issue_features(
        self,
        commits: List[Dict[str, Any]],
        pull_requests: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        # NOTE: Issues are not fetched separately to conserve GitHub API quota.
        # All three features are set to 0.0 and documented as known limitations
        # in the paper's evaluation section.
        return {
            "total_issues_opened_365d": 0.0,
            "total_issues_closed_365d": 0.0,
            "issue_close_rate": 0.0,
        }
