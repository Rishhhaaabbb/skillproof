# Task 10: Task service — generates and verifies personalised skill-building tasks
"""
Creates verifiable improvement tasks from gap analysis.

Verification signal format (structured JSON, not free text):
  {"file_pattern": "test_*.py", "keyword": "assert", "repo": "reponame"}

check_completion() uses fnmatch on actual commit file paths — requires
the GitHubFetcher to return file lists per commit (implemented in Task 4).
"""
from __future__ import annotations

import fnmatch
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from models.database import Notification, Task
from services.llm_generator import LLMGenerator

logger = logging.getLogger(__name__)

_TASK_EXPIRY_DAYS = 21


class TaskService:
    """Generates personalised tasks and verifies completion via commit analysis."""

    def __init__(self) -> None:
        self.llm = LLMGenerator()

    def generate_task(
        self,
        missing_requirement: str,
        top_repos: List[Dict],
    ) -> Dict[str, Any]:
        """Generate ONE specific, verifiable task for a missing requirement.

        Returns a dict with target_repo, task_description, verification_signal.
        Does NOT persist — caller is responsible for saving to DB.
        """
        repo_summary = "\n".join(
            f"- {r.get('name')}: {r.get('description') or ''} ({r.get('language', '?')})"
            for r in top_repos[:5]
        ) or "- No repos available"

        prompt = f"""A developer is missing evidence for: "{missing_requirement}"

THEIR REPOS:
{repo_summary}

Design ONE specific, scoped, verifiable micro-task tied to an actual repo above
where possible. The task must be completable in a few hours.

The verification_signal MUST be structured JSON with these exact fields:
  file_pattern: glob pattern for files that should be added/modified (e.g. "test_*.py")
  keyword: keyword that should appear in the commit message (e.g. "test" or "ci")
  repo: the target repo name (or "new-repo" if creating a new one)

Return ONLY this JSON:
{{
  "target_repo": "repo name from list above or 'new-repo'",
  "task_description": "specific, actionable instructions (2-3 sentences)",
  "verification_signal": {{
    "file_pattern": "glob pattern",
    "keyword": "commit message keyword",
    "repo": "repo name"
  }}
}}"""

        result = self.llm.generate_json(prompt)
        if result.success and result.data:
            sig = result.data.get("verification_signal")
            if isinstance(sig, str):
                result.data["verification_signal"] = {
                    "file_pattern": "*",
                    "keyword": sig,
                    "repo": result.data.get("target_repo", ""),
                }
            return result.data

        logger.warning("Task generation failed: %s", result.error_message)
        return {
            "target_repo": top_repos[0].get("name") if top_repos else "new-repo",
            "task_description": (
                f"Add evidence for: {missing_requirement}. "
                "Create relevant code, tests, or documentation in one of your repos."
            ),
            "verification_signal": {
                "file_pattern": "*",
                "keyword": missing_requirement.split()[0].lower(),
                "repo": top_repos[0].get("name") if top_repos else "new-repo",
            },
        }

    def check_completion(
        self,
        task: Any,
        github_data: Dict[str, Any],
    ) -> bool:
        """Check if recent commits satisfy the task's structured verification_signal.

        Requires both conditions to be true:
        1. A commit in the target repo has a message containing the keyword.
        2. At least one file in that commit matches the file_pattern glob.
        """
        sig = task.verification_signal
        if not sig or not isinstance(sig, dict):
            return False

        target_repo = sig.get("repo") or task.target_repo
        keyword = (sig.get("keyword") or "").lower()
        file_pattern = sig.get("file_pattern") or "*"

        if not target_repo or not keyword:
            return False

        for commit in github_data.get("commits", []):
            if commit.get("repo") != target_repo:
                continue
            message = (commit.get("message") or "").lower()
            if keyword not in message:
                continue
            files = commit.get("files") or []
            for file_path in files:
                filename = file_path.split("/")[-1]
                if fnmatch.fnmatch(filename, file_pattern):
                    return True

        return False

    def get_active_tasks(
        self, db: Session, user_id: int, target_role_id: int
    ) -> List[Any]:
        """Return all assigned (non-expired) tasks for a user+role."""
        return (
            db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.target_role_id == target_role_id,
                Task.status == "assigned",
            )
            .order_by(Task.created_at.desc())
            .all()
        )

    def expire_old_tasks(
        self, db: Session, user_id: int, target_role_id: int
    ) -> int:
        """Mark tasks older than _TASK_EXPIRY_DAYS as expired. Returns count."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=_TASK_EXPIRY_DAYS)
        tasks = (
            db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.target_role_id == target_role_id,
                Task.status == "assigned",
                Task.created_at < cutoff,
            )
            .all()
        )
        for t in tasks:
            t.status = "expired"
            db.add(
                Notification(
                    user_id=user_id,
                    target_role_id=target_role_id,
                    message=f"Your task to address '{t.missing_requirement}' has expired and been reassigned.",
                )
            )
        db.commit()
        return len(tasks)
