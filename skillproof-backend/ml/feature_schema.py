# Task 5: Canonical feature vector contract
# This list defines the order in which features are assembled into the numpy
# array that is passed to the LR model.  Any change here must be accompanied
# by a model retrain — treat this file as a versioned schema.

FEATURE_NAMES: list[str] = [
    # --- Commit volume & frequency ---
    "total_commits_90d",
    "total_commits_365d",
    "active_days_90d",
    "active_days_365d",
    "avg_commits_per_active_day",
    # --- Commit quality ---
    "avg_commit_message_length",
    "pct_commits_with_body",
    "pct_commits_conventional_format",
    # --- Pull request behaviour ---
    "total_prs_90d",
    "total_prs_365d",
    "pr_merge_rate",
    "avg_pr_size_lines",
    "avg_pr_review_comments",
    # --- Code review activity ---
    "total_reviews_given_90d",
    "total_reviews_given_365d",
    "pct_reviews_requesting_changes",
    "review_to_pr_ratio",
    # --- Repository depth ---
    "distinct_languages_count",
    "avg_repo_stars",
    "pct_repos_with_readme",
    "pct_repos_with_topics",
    "has_pinned_repos",
    # --- Temporal consistency ---
    "longest_commit_streak_days",
    "weeks_with_activity_52w",
    "pct_weeks_active_52w",
    # --- Issue participation ---
    "total_issues_opened_365d",
    "total_issues_closed_365d",
    "issue_close_rate",
]
"""Canonical ordered list of feature names for the SkillProof feature vector.

The position of each name in this list corresponds to column index ``i`` in the
numpy array passed to ``LRScorer.score()``.  Do not reorder entries without
retraining the model.
"""
