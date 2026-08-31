# Task 12: Scheduler router — weekly re-analysis triggered by GitHub Actions cron
"""
Protected endpoint called exclusively by GitHub Actions cron job.
Runs weekly for all users:
  1. Re-fetches GitHub data (cache invalidated first)
  2. Re-scores (TPR + LR)
  3. Checks open task completion via verification signals
  4. Updates streaks and milestones
  5. Notifies users of score changes >= 10 points
  6. Expires stale tasks and generates replacements

Rate-limited by the SCHEDULER_SECRET header — returns 403 on mismatch.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from models.database import (
    Analysis, Notification, SessionLocal,
    Task, TargetRole, User,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/internal", tags=["scheduler"])


@router.post("/run-weekly-reanalysis")
def run_weekly_reanalysis(
    x_scheduler_secret: str = Header(..., alias="X-Scheduler-Secret"),
) -> Dict[str, Any]:
    """Trigger weekly re-analysis for all users.

    Protected by X-Scheduler-Secret header — only GitHub Actions cron should
    call this endpoint. Returns 403 on secret mismatch.
    """
    if x_scheduler_secret != settings.SCHEDULER_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid scheduler secret",
        )

    db: Session = SessionLocal()
    results = {"processed": 0, "errors": 0, "task_completions": 0, "score_changes": 0}

    try:
        users = db.query(User).filter(User.github_username.isnot(None)).all()
        logger.info("Scheduler: processing %d users", len(users))

        for user in users:
            try:
                _process_user(db, user, results)
                results["processed"] += 1
            except Exception as exc:
                logger.error("Scheduler error for user %d: %s", user.id, exc)
                results["errors"] += 1
                continue

        db.commit()
        logger.info("Scheduler complete: %s", results)
        return results

    finally:
        db.close()


def _process_user(db: Session, user: User, results: Dict) -> None:
    """Run the full weekly pipeline for one user."""
    from services.feature_extractor import FeatureExtractor
    from services.github_fetcher import GitHubFetcher
    from services.lr_scorer import LRScorer
    from services.streak_service import StreakService
    from services.task_service import TaskService
    from services.tpr_scorer import TPRScorer
    from utils.cache import cache as _github_cache

    fetcher = GitHubFetcher()
    extractor = FeatureExtractor()
    tpr_scorer = TPRScorer()
    lr_scorer = LRScorer()
    streak_svc = StreakService()
    task_svc = TaskService()

    # 1. Bypass TTL cache — fetch fresh data
    _github_cache.invalidate(f"github:{user.github_username}")
    github_data = fetcher.get_user_data(user.github_username)

    # 2. Re-score
    features = extractor.extract_all_features(github_data)
    tpr_score, confidence, breakdown = tpr_scorer.score(features)
    flags = tpr_scorer.generate_flags(features, breakdown)
    lr_score, lr_confidence = lr_scorer.score(features)

    # Make breakdown JSON-serialisable
    safe_breakdown = {k: (dict(v) if isinstance(v, dict) else v) for k, v in breakdown.items()}
    safe_features = {k: float(v) for k, v in features.items()}
    safe_flags = {k: list(v) for k, v in flags.items()}

    # 3. Persist new Analysis row
    from models.database import SkillTag as ST

    analysis = Analysis(
        user_id=user.id,
        tpr_score=tpr_score,
        lr_score=lr_score,
        confidence_level=lr_confidence or confidence,
        breakdown=safe_breakdown,
        features=safe_features,
        flags=safe_flags,
        heatmap_data=github_data.get("heatmap", {}),
    )
    db.add(analysis)
    db.flush()  # get analysis.id without full commit

    # 4. Upsert skill tags
    db.query(ST).filter(ST.user_id == user.id).delete()
    skill_tags = extractor.extract_skill_tags(github_data)
    for tag_data in skill_tags:
        db.add(ST(
            user_id=user.id,
            tag=tag_data["tag"],
            confidence=tag_data["confidence"],
            source=tag_data["source"],
        ))

    # 5. Update streaks and milestones
    streak_svc.update_streak(db, user.id, github_data.get("heatmap", {}))
    streak_svc.check_behavior_milestones(db, user.id, features)

    # 6. Check task completion for all open tasks
    open_tasks = (
        db.query(Task)
        .filter(Task.user_id == user.id, Task.status == "assigned")
        .all()
    )
    for task in open_tasks:
        if task_svc.check_completion(task, github_data):
            task.status = "verified_complete"
            task.verified_at = datetime.now(timezone.utc)
            db.add(Notification(
                user_id=user.id,
                target_role_id=task.target_role_id,
                message=f"Verified: you completed the task for '{task.missing_requirement}'.",
            ))
            results["task_completions"] += 1

    # 7. Re-analyze each target role
    analysis_ctx = {
        "tpr_score": tpr_score,
        "confidence_level": confidence,
        "breakdown": safe_breakdown,
        "flags": safe_flags,
        "features": safe_features,
    }
    tag_dicts = [{"tag": t["tag"], "confidence": t["confidence"]} for t in skill_tags]

    roles = db.query(TargetRole).filter(TargetRole.user_id == user.id).all()
    for role in roles:
        try:
            _reanalyze_role(db, user, role, analysis_ctx, github_data, tag_dicts, task_svc, results)
        except Exception as exc:
            logger.error("Role reanalysis error for role %d: %s", role.id, exc)
            continue


def _reanalyze_role(
    db: Session,
    user: User,
    role: TargetRole,
    analysis_ctx: Dict,
    github_data: Dict,
    tag_dicts: list,
    task_svc: Any,
    results: Dict,
) -> None:
    """Re-run gap analysis for one target role and update readiness history."""
    from models.database import ReadinessHistory
    from services.jd_analyzer import JDAnalyzer

    jd_analyzer = JDAnalyzer()
    gap = jd_analyzer.analyze(
        jd_text=role.jd_text,
        analysis=analysis_ctx,
        top_repos=github_data.get("repos", []),
        skill_tags=tag_dicts,
    )

    prev_score = role.latest_readiness_score
    role.latest_readiness_score = gap["readiness_estimate"]
    role.latest_gap_analysis = gap
    role.last_analyzed_at = datetime.now(timezone.utc)

    db.add(ReadinessHistory(
        target_role_id=role.id,
        readiness_score=gap["readiness_estimate"],
        gap_summary=gap,
    ))

    if prev_score is not None and abs(gap["readiness_estimate"] - prev_score) >= 10:
        direction = "improved" if gap["readiness_estimate"] > prev_score else "dropped"
        db.add(Notification(
            user_id=user.id,
            target_role_id=role.id,
            message=f"Your readiness for '{role.role_title}' {direction} to {gap['readiness_estimate']}%.",
        ))
        results["score_changes"] += 1

    task_svc.expire_old_tasks(db, user.id, role.id)
    active_count = len(task_svc.get_active_tasks(db, user.id, role.id))
    for missing in gap.get("missing_requirements", [])[:2]:
        if active_count >= 2:
            break
        task_data = task_svc.generate_task(missing, github_data.get("repos", []))
        db.add(Task(
            user_id=user.id,
            target_role_id=role.id,
            missing_requirement=missing,
            target_repo=task_data.get("target_repo"),
            task_description=task_data.get("task_description", ""),
            verification_signal=task_data.get("verification_signal"),
        ))
        active_count += 1
