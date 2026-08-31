# Task 10: Target roles router — complete implementation
"""
Full CRUD for target roles plus the async analysis pipeline:
  POST /api/target-roles              — create (max 3 per user)
  GET  /api/target-roles              — list all
  GET  /api/target-roles/{id}         — get one
  PATCH /api/target-roles/{id}        — update JD or title
  DELETE /api/target-roles/{id}       — delete
  POST /api/target-roles/{id}/analyze — trigger gap analysis + adversarial eval + tasks
  GET  /api/target-roles/{id}/history — readiness score history
  GET  /api/target-roles/{id}/verdict — latest adversarial verdict
  GET  /api/target-roles/{id}/tasks   — active tasks
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, get_db
from config import settings
from models.database import (
    Analysis, EvaluationVerdict, Notification, ReadinessHistory,
    SkillTag, Task, TargetRole, User,
)
from models.schemas import (
    JobStatusOut, ReadinessHistoryOut, TargetRoleCreate,
    TargetRoleOut, TargetRoleUpdate,
)
from utils.background import create_job, run_in_background

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/target-roles", tags=["target-roles"])


# ---------------------------------------------------------------------------
# Background worker
# ---------------------------------------------------------------------------

def _run_role_analysis(user_id: int, target_role_id: int) -> Dict[str, Any]:
    """Full role analysis pipeline — runs in background thread."""
    from datetime import datetime, timezone

    from models.database import SessionLocal
    from models.database import SkillTag as ST
    from services.adversarial_evaluator import AdversarialEvaluator
    from services.feature_extractor import FeatureExtractor
    from services.github_fetcher import GitHubFetcher
    from services.jd_analyzer import JDAnalyzer
    from services.task_service import TaskService
    from services.tpr_scorer import TPRScorer

    db: Session = SessionLocal()
    try:
        role = db.get(TargetRole, target_role_id)
        user = db.get(User, user_id)
        if not role or not user:
            return {"error": "Role or user not found"}

        # 1. Fetch GitHub data (uses TTL cache)
        fetcher = GitHubFetcher()
        github_data = fetcher.get_user_data(user.github_username)

        # 2. Build analysis context
        latest = (
            db.query(Analysis)
            .filter(Analysis.user_id == user_id)
            .order_by(Analysis.created_at.desc())
            .first()
        )
        if latest:
            analysis_ctx = {
                "tpr_score": latest.tpr_score,
                "confidence_level": latest.confidence_level,
                "breakdown": latest.breakdown or {},
                "flags": latest.flags or {},
                "features": latest.features or {},
            }
        else:
            extractor = FeatureExtractor()
            features = extractor.extract_all_features(github_data)
            scorer = TPRScorer()
            tpr_score, confidence, breakdown = scorer.score(features)
            flags = scorer.generate_flags(features, breakdown)
            analysis_ctx = {
                "tpr_score": tpr_score,
                "confidence_level": confidence,
                "breakdown": breakdown,
                "flags": flags,
                "features": features,
            }

        # 3. Skill tags for citation validation
        skill_tags_db = db.query(ST).filter(ST.user_id == user_id).all()
        tag_dicts = [{"tag": t.tag, "confidence": t.confidence} for t in skill_tags_db]

        # 4. JD gap analysis
        jd_analyzer = JDAnalyzer()
        gap = jd_analyzer.analyze(
            jd_text=role.jd_text,
            analysis=analysis_ctx,
            top_repos=github_data.get("repos", []),
            skill_tags=tag_dicts,
        )

        # 5. Adversarial evaluation
        evaluator = AdversarialEvaluator()
        verdict = evaluator.run_evaluation(
            db=db,
            user_id=user_id,
            target_role_id=target_role_id,
            analysis=analysis_ctx,
            jd_text=role.jd_text,
            top_repos=github_data.get("repos", []),
            save=True,
        )

        # 6. Expire old tasks, generate new ones for top 2 missing
        task_svc = TaskService()
        task_svc.expire_old_tasks(db, user_id, target_role_id)
        active_count = len(task_svc.get_active_tasks(db, user_id, target_role_id))
        new_tasks = []
        for missing in gap.get("missing_requirements", [])[:2]:
            if active_count >= 2:
                break
            task_data = task_svc.generate_task(missing, github_data.get("repos", []))
            t = Task(
                user_id=user_id,
                target_role_id=target_role_id,
                missing_requirement=missing,
                target_repo=task_data.get("target_repo"),
                task_description=task_data.get("task_description", ""),
                verification_signal=task_data.get("verification_signal"),
            )
            db.add(t)
            new_tasks.append(missing)
            active_count += 1

        # 7. Persist gap analysis
        prev_score = role.latest_readiness_score
        role.latest_readiness_score = gap["readiness_estimate"]
        role.latest_gap_analysis = gap
        role.last_analyzed_at = datetime.now(timezone.utc)

        db.add(ReadinessHistory(
            target_role_id=target_role_id,
            readiness_score=gap["readiness_estimate"],
            gap_summary=gap,
        ))

        # 8. Notify on significant score change
        if prev_score is not None and abs(gap["readiness_estimate"] - prev_score) >= 10:
            direction = "improved" if gap["readiness_estimate"] > prev_score else "dropped"
            db.add(Notification(
                user_id=user_id,
                target_role_id=target_role_id,
                message=f"Your readiness for '{role.role_title}' {direction} to {gap['readiness_estimate']}%.",
            ))

        db.commit()

        return {
            "target_role_id": target_role_id,
            "readiness_estimate": gap["readiness_estimate"],
            "matched_count": len(gap.get("matched_requirements", [])),
            "missing_count": len(gap.get("missing_requirements", [])),
            "tasks_generated": new_tasks,
            "verdict_confidence": verdict.get("confidence"),
            "citation_hallucination_rate": gap.get("citation_hallucination_rate", 0),
        }
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=TargetRoleOut, status_code=201)
def create_target_role(
    payload: TargetRoleCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new target role. Max 3 per user."""
    count = db.query(TargetRole).filter(TargetRole.user_id == user.id).count()
    if count >= settings.MAX_TARGET_ROLES_PER_USER:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {settings.MAX_TARGET_ROLES_PER_USER} target roles allowed. Delete one to add a new one.",
        )
    role = TargetRole(
        user_id=user.id,
        role_title=payload.role_title,
        company_name=payload.company_name,
        jd_text=payload.jd_text,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.get("", response_model=List[TargetRoleOut])
def list_target_roles(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all target roles for the authenticated user."""
    return (
        db.query(TargetRole)
        .filter(TargetRole.user_id == user.id)
        .order_by(TargetRole.created_at.desc())
        .all()
    )


@router.get("/{role_id}", response_model=TargetRoleOut)
def get_target_role(
    role_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single target role."""
    role = db.query(TargetRole).filter(
        TargetRole.id == role_id, TargetRole.user_id == user.id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="Target role not found")
    return role


@router.patch("/{role_id}", response_model=TargetRoleOut)
def update_target_role(
    role_id: int,
    payload: TargetRoleUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a target role's title, company, or JD text."""
    role = db.query(TargetRole).filter(
        TargetRole.id == role_id, TargetRole.user_id == user.id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="Target role not found")
    if payload.role_title is not None:
        role.role_title = payload.role_title
    if payload.company_name is not None:
        role.company_name = payload.company_name
    if payload.jd_text is not None:
        role.jd_text = payload.jd_text
        role.latest_readiness_score = None
        role.latest_gap_analysis = None
    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}", status_code=204)
def delete_target_role(
    role_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a target role and all associated data."""
    role = db.query(TargetRole).filter(
        TargetRole.id == role_id, TargetRole.user_id == user.id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="Target role not found")
    db.delete(role)
    db.commit()


@router.post("/{role_id}/analyze", response_model=JobStatusOut)
def analyze_target_role(
    role_id: int,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger gap analysis + adversarial evaluation. Returns job_id immediately."""
    role = db.query(TargetRole).filter(
        TargetRole.id == role_id, TargetRole.user_id == user.id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="Target role not found")
    if not user.github_username:
        raise HTTPException(
            status_code=400,
            detail="No GitHub username linked. Update your profile first.",
        )
    job = create_job(db, user.id, "role_analysis")
    background_tasks.add_task(
        run_in_background, job.id, _run_role_analysis, user.id, role_id
    )
    return job


@router.get("/{role_id}/history", response_model=List[ReadinessHistoryOut])
def get_readiness_history(
    role_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=100),
):
    """Return readiness score history for trend chart."""
    role = db.query(TargetRole).filter(
        TargetRole.id == role_id, TargetRole.user_id == user.id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="Target role not found")
    return (
        db.query(ReadinessHistory)
        .filter(ReadinessHistory.target_role_id == role_id)
        .order_by(ReadinessHistory.recorded_at.asc())
        .limit(limit)
        .all()
    )


@router.get("/{role_id}/verdict")
def get_latest_verdict(
    role_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the latest adversarial evaluation verdict."""
    role = db.query(TargetRole).filter(
        TargetRole.id == role_id, TargetRole.user_id == user.id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="Target role not found")
    verdict = (
        db.query(EvaluationVerdict)
        .filter(
            EvaluationVerdict.target_role_id == role_id,
            EvaluationVerdict.user_id == user.id,
        )
        .order_by(EvaluationVerdict.created_at.desc())
        .first()
    )
    if not verdict:
        raise HTTPException(
            status_code=404, detail="No verdict found. Run an analysis first."
        )
    return {
        "skeptic_case": verdict.skeptic_case,
        "advocate_case": verdict.advocate_case,
        "final_verdict": verdict.final_verdict,
        "confidence": verdict.confidence,
        "surviving_skeptic_points": verdict.surviving_skeptic_points,
        "surviving_advocate_points": verdict.surviving_advocate_points,
        "created_at": verdict.created_at.isoformat(),
    }


@router.get("/{role_id}/tasks")
def get_tasks(
    role_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all tasks for a target role."""
    role = db.query(TargetRole).filter(
        TargetRole.id == role_id, TargetRole.user_id == user.id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="Target role not found")
    tasks = (
        db.query(Task)
        .filter(Task.user_id == user.id, Task.target_role_id == role_id)
        .order_by(Task.created_at.desc())
        .all()
    )
    return [
        {
            "id": t.id,
            "missing_requirement": t.missing_requirement,
            "target_repo": t.target_repo,
            "task_description": t.task_description,
            "verification_signal": t.verification_signal,
            "status": t.status,
            "created_at": t.created_at.isoformat(),
            "verified_at": t.verified_at.isoformat() if t.verified_at else None,
        }
        for t in tasks
    ]


@router.get("/{role_id}/comparison")
def get_comparison(
    role_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the latest before/after comparison for a target role."""
    role = db.query(TargetRole).filter(
        TargetRole.id == role_id, TargetRole.user_id == user.id
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="Target role not found")
    from services.comparison_service import ComparisonService
    result = ComparisonService().get_latest_comparison(db, user.id, role_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No comparison available yet. Complete a task and re-analyze to see your progress.",
        )
    return result
