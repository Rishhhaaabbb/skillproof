# Task 4: GitHub data fetcher — retrieves raw repository and contribution data
from typing import Any, Dict, List, Optional


class GitHubFetcher:
    """Fetches raw GitHub activity data for a given username.

    Uses PyGithub authenticated with the GITHUB_TOKEN from settings.
    Applies the GITHUB_REPO_CAP limit to avoid hitting rate limits.
    """

    def __init__(self) -> None:
        """Initialise the PyGithub client with the token from settings."""
        pass

    def fetch_user_profile(self, username: str) -> Dict[str, Any]:
        """Fetch a GitHub user's public profile information.

        Args:
            username: GitHub login name.

        Returns:
            Dict containing name, bio, public_repos, followers, following,
            created_at, and other profile fields.
        """
        pass

    def fetch_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Fetch the user's repositories up to GITHUB_REPO_CAP.

        Repositories are sorted by pushed_at descending so the most recently
        active repos are prioritised within the cap.

        Args:
            username: GitHub login name.

        Returns:
            List of dicts, each containing name, description, language,
            stargazers_count, forks_count, pushed_at, topics, etc.
        """
        pass

    def fetch_commit_activity(self, username: str, repos: List[str]) -> List[Dict[str, Any]]:
        """Fetch commit metadata across the provided repository list.

        Args:
            username: GitHub login name (used to filter commits by author).
            repos:    List of full repo names (``owner/repo``).

        Returns:
            List of commit dicts with sha, message, date, repo_name, and
            additions/deletions if available.
        """
        pass

    def fetch_pull_requests(self, username: str, repos: List[str]) -> List[Dict[str, Any]]:
        """Fetch pull request data authored by the user across repos.

        Args:
            username: GitHub login name.
            repos:    List of full repo names to search.

        Returns:
            List of PR dicts with title, state, created_at, merged_at,
            changed_files, additions, deletions, and review_comments.
        """
        pass

    def fetch_code_reviews(self, username: str, repos: List[str]) -> List[Dict[str, Any]]:
        """Fetch code review events (PR reviews) submitted by the user.

        Args:
            username: GitHub login name.
            repos:    List of full repo names to search.

        Returns:
            List of review dicts with pr_number, state (APPROVED/CHANGES_REQUESTED
            /COMMENTED), submitted_at, and body.
        """
        pass

    def fetch_issues(self, username: str, repos: List[str]) -> List[Dict[str, Any]]:
        """Fetch issues opened by the user across repos.

        Args:
            username: GitHub login name.
            repos:    List of full repo names to search.

        Returns:
            List of issue dicts with number, title, state, created_at,
            closed_at, labels, and comments count.
        """
        pass

    def fetch_readme(self, repo_full_name: str) -> Optional[str]:
        """Fetch the raw README text for a repository.

        Args:
            repo_full_name: Full repo name in ``owner/repo`` format.

        Returns:
            Decoded README text, or None if no README exists.
        """
        pass
