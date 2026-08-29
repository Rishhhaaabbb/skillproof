# Task 4: GitHub data fetcher — retrieves raw repository and contribution data
"""Production-hardened GitHub data fetcher.

Design decisions:
- Hard cap of GITHUB_REPO_CAP (15) non-fork repos sorted by pushed_at desc.
- In-memory TTL cache (900 s) keyed by username — avoids redundant API calls.
- Commit fetch is capped at 50 per repo and 500 total across all repos.
- Files per commit are stored as a list of paths (not just a count) to support
  structured task verification signals in Task 10.
- Partial results are returned on repo-level failures rather than aborting.
- Rate-limit (403/429) and not-found errors are handled at the top level.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from github import Github, GithubException, UnknownObjectException

from config import settings
from utils.cache import cache as _github_cache

logger = logging.getLogger(__name__)

_COMMITS_PER_REPO_CAP = 50
_TOTAL_COMMITS_CAP = 500
_PR_CAP = 50
_REVIEW_CAP = 50
_HEATMAP_WEEKS = 52


class GitHubFetcher:
    """Fetches raw GitHub activity data for a given username."""

    def __init__(self) -> None:
        self._client = Github(settings.GITHUB_TOKEN)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_user_data(self, username: str) -> Dict[str, Any]:
        """Return a fully structured activity dict for *username*.

        Results are cached for CACHE_TTL_SECONDS seconds.  Callers must always
        pass the authenticated user's own github_username — privacy enforcement
        happens in the router layer, not here.

        Args:
            username: GitHub login name.

        Returns:
            Structured dict — see module docstring for full key listing.

        Raises:
            ValueError: If the profile is private or does not exist.
        """
        cache_key = f"github:{username}"
        cached = _github_cache.get(cache_key)
        if cached is not None:
            logger.debug("Cache hit for %s", username)
            return cached

        try:
            result = self._fetch(username)
        except UnknownObjectException:
            raise ValueError(
                f"GitHub user '{username}' not found or profile is private"
            )
        except GithubException as exc:
            if exc.status in (403, 429):
                logger.warning("GitHub rate limit hit for %s: %s", username, exc)
                reset_time = self._client.get_rate_limit().core.reset
                now = datetime.now(timezone.utc)
                reset_in = max(0, int((reset_time.replace(tzinfo=timezone.utc) - now).total_seconds()))
                return {
                    "username": username,
                    "data_quality": "rate_limited",
                    "rate_limit_reset": reset_in,
                    "repos": [],
                    "commits": [],
                    "pull_requests": [],
                    "code_reviews": [],
                    "heatmap": {},
                    "repos_failed": 0,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "profile": {},
                }
            raise

        _github_cache.set(cache_key, result, ttl=settings.CACHE_TTL_SECONDS)
        return result

    # ------------------------------------------------------------------
    # Internal fetch orchestration
    # ------------------------------------------------------------------

    def _fetch(self, username: str) -> Dict[str, Any]:
        user = self._client.get_user(username)

        profile = {
            "name": user.name,
            "bio": user.bio,
            "public_repos": user.public_repos,
            "followers": user.followers,
            "following": user.following,
            "created_at": user.created_at,
            "avatar_url": user.avatar_url,
        }

        repos = self._fetch_repos(user)
        commits, repos_failed = self._fetch_commits(username, repos)
        heatmap = self._build_heatmap(commits)
        pull_requests = self._fetch_pull_requests(username)
        code_reviews = self._fetch_code_reviews(username)

        total_repos = len(repos)
        data_quality = (
            "partial"
            if (total_repos > 0 and repos_failed / total_repos > 0.5)
            else "full"
        )

        return {
            "username": username,
            "profile": profile,
            "repos": repos,
            "commits": commits,
            "pull_requests": pull_requests,
            "code_reviews": code_reviews,
            "heatmap": heatmap,
            "data_quality": data_quality,
            "repos_failed": repos_failed,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Repo fetching
    # ------------------------------------------------------------------

    def _fetch_repos(self, user) -> List[Dict[str, Any]]:
        repos: List[Dict[str, Any]] = []
        try:
            all_repos = user.get_repos(sort="pushed", direction="desc")
            for repo in all_repos:
                if len(repos) >= settings.GITHUB_REPO_CAP:
                    break
                if repo.fork:
                    continue

                # Language breakdown
                try:
                    languages = repo.get_languages()
                except Exception:
                    languages = {}

                # README detection — existence only, no content fetch
                has_readme = False
                try:
                    repo.get_readme()
                    has_readme = True
                except GithubException:
                    has_readme = False
                except Exception:
                    has_readme = False

                repos.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "language": repo.language,
                    "languages": languages,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "topics": repo.get_topics() if hasattr(repo, "get_topics") else [],
                    "pushed_at": repo.pushed_at,
                    "created_at": repo.created_at,
                    "has_readme": has_readme,
                    "size_kb": repo.size,
                })
        except Exception as exc:
            logger.warning("Error fetching repos: %s", exc)

        return repos

    # ------------------------------------------------------------------
    # Commit fetching
    # ------------------------------------------------------------------

    def _fetch_commits(
        self, username: str, repos: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], int]:
        since = datetime.now(timezone.utc) - timedelta(days=180)
        all_commits: List[Dict[str, Any]] = []
        repos_failed = 0

        for repo_data in repos:
            if len(all_commits) >= _TOTAL_COMMITS_CAP:
                break

            repo_name = repo_data["name"]
            full_name = repo_data["full_name"]

            try:
                repo = self._client.get_repo(full_name)
                commit_list = repo.get_commits(author=username, since=since)
                count = 0
                for commit in commit_list:
                    if count >= _COMMITS_PER_REPO_CAP:
                        break
                    if len(all_commits) >= _TOTAL_COMMITS_CAP:
                        break
                    try:
                        files = [f.filename for f in commit.files]
                        additions = commit.stats.additions
                        deletions = commit.stats.deletions
                    except Exception:
                        files = []
                        additions = 0
                        deletions = 0

                    all_commits.append({
                        "repo": repo_name,
                        "sha": commit.sha,
                        "message": commit.commit.message,
                        "date": commit.commit.author.date,
                        "additions": additions,
                        "deletions": deletions,
                        "files": files,
                        "files_changed": len(files),
                    })
                    count += 1

            except Exception as exc:
                logger.warning("Failed to fetch commits for %s: %s", full_name, exc)
                repos_failed += 1
                continue

        return all_commits, repos_failed

    # ------------------------------------------------------------------
    # Heatmap
    # ------------------------------------------------------------------

    def _build_heatmap(self, commits: List[Dict[str, Any]]) -> Dict[str, int]:
        """Build a 52-week activity heatmap from commit dates."""
        today = datetime.now(timezone.utc).date()
        heatmap: Dict[str, int] = {}

        # Initialise all 52 weeks to 0
        for i in range(_HEATMAP_WEEKS):
            week_date = today - timedelta(weeks=i)
            iso = week_date.isocalendar()
            key = f"{iso.year}-W{iso.week:02d}"
            heatmap[key] = 0

        # Increment from commits
        for commit in commits:
            date = commit["date"]
            if hasattr(date, "date"):
                d = date.date() if not isinstance(date, datetime.__class__) else date
                if isinstance(date, datetime):
                    d = date.date()
                else:
                    d = date
            else:
                continue
            iso = d.isocalendar()
            key = f"{iso.year}-W{iso.week:02d}"
            if key in heatmap:
                heatmap[key] += 1

        return heatmap

    # ------------------------------------------------------------------
    # Pull requests
    # ------------------------------------------------------------------

    def _fetch_pull_requests(self, username: str) -> List[Dict[str, Any]]:
        prs: List[Dict[str, Any]] = []
        try:
            results = self._client.search_issues(
                f"author:{username} is:pr", sort="created", order="desc"
            )
            for item in results[:_PR_CAP]:
                # Safely get repo name
                repo_name: Optional[str] = None
                try:
                    repo_name = item.repository.name
                except Exception:
                    pass

                # Get detailed PR data
                merged_at = None
                additions = 0
                deletions = 0
                changed_files = 0
                review_comments = 0
                merged = False
                try:
                    pr_obj = item.as_pull_request()
                    merged_at = pr_obj.merged_at
                    additions = pr_obj.additions or 0
                    deletions = pr_obj.deletions or 0
                    changed_files = pr_obj.changed_files or 0
                    review_comments = pr_obj.review_comments or 0
                    merged = pr_obj.merged or False
                except Exception:
                    pass

                body = item.body or ""
                prs.append({
                    "title": item.title,
                    "state": item.state,
                    "merged": merged,
                    "created_at": item.created_at,
                    "merged_at": merged_at,
                    "comments": item.comments,
                    "review_comments": review_comments,
                    "additions": additions,
                    "deletions": deletions,
                    "changed_files": changed_files,
                    "body": body[:500],
                    "repo": repo_name,
                })
        except Exception as exc:
            logger.warning("Error fetching pull requests for %s: %s", username, exc)

        return prs

    # ------------------------------------------------------------------
    # Code reviews
    # ------------------------------------------------------------------

    def _fetch_code_reviews(self, username: str) -> List[Dict[str, Any]]:
        reviews: List[Dict[str, Any]] = []
        try:
            results = self._client.search_issues(
                f"commenter:{username} is:pr -author:{username}",
                sort="created",
                order="desc",
            )
            for item in results[:_REVIEW_CAP]:
                repo_name: Optional[str] = None
                try:
                    repo_name = item.repository.name
                except Exception:
                    pass

                reviews.append({
                    "pr_title": item.title,
                    "comment_count": item.comments,
                    "repo": repo_name,
                })
        except Exception as exc:
            logger.warning("Error fetching code reviews for %s: %s", username, exc)

        return reviews
