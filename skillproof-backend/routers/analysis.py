# Task 8: Analysis router — complete implementation
"""
Analysis pipeline router.

POST /api/analysis/trigger  — queues a background job, returns job_id immediately
GET  /api/analysis/latest   — returns the most recent Analysis for the user
GET  /api/analysis/history  — returns paginated analysis history (for trend chart)
GET  /api/analysis/heatmap  — returns 52-week heatmap from the latest analysis
GET  /api/analysis/skills   — returns extracted skill tags
GET  /api/analysis/streaks  — returns streak summary + milestones
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, get_db
from models.database import Analysis, SkillTag, User
from models.schemas import AnalysisOut, JobStatusOut
from utils.background import create_job, run_in_background

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


# ---------------------------------------------------------------------------
# Background worker function
# ---------------------------------------------------------------------------

def _run_analysis(user_id: int, github_username: str) -> Dict[str, Any]:
    """Full analysis pipeline — runs in a background thread.

    Fetches GitHub data, extracts features, scores with TPR + LR,
    updates streaks and milestones, upserts skill tags, persists Analysis row.

    Returns a JSON-serialisable dict that becomes job.result.
    """
    from models.database import SessionLocal, SkillTag as SkillTagModel
    from services.feature_extractor import FeatureExtractor
    from services.github_fetcher import GitHubFetcher
    from services.lr_scorer import LRScorer
    from services.streak_service import StreakService
    from services.tpr_scorer import TPRScorer

    db: Session = SessionLocal()
    try:
        # 1. Fetch GitHub data (privacy: always the authenticated user's own account)
        fetcher = GitHubFetcher()
        github_data = fetcher.get_user_data(github_username)

        # 2. Extract features
        extractor = FeatureExtractor()
        features = extractor.extract_all_features(github_data)

        # 3. TPR score
        tpr_scorer = TPRScorer()
        tpr_score, confidence, breakdown = tpr_scorer.score(features)
        flags = tpr_scorer.generate_flags(features, breakdown)

        # 4. LR score (None if model not yet trained — graceful fallback)
        lr_scorer = LRScorer()
        lr_score, lr_confidence = lr_scorer.score(features)

        # 5. Check if this is the user's first analysis
        existing = (
            db.query(Analysis)
            .filter(Analysis.user_id == user_id)
            .first()
        )
        is_first = existing is None

        # 6. Persist Analysis row
        # Make breakdown JSON-serialisable (convert any non-serialisable types)
        import json
        def _safe(obj):
            try:
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                return str(obj)

        safe_breakdown = {k: _safe(v) for k, v in breakdown.items()}
        safe_features = {k: float(v) for k, v in features.items()}
        safe_flags = {k: list(v) for k, v in flags.items()}

        analysis = Analysis(
            user_id=user_id,
            tpr_score=tpr_score,
            lr_score=lr_score,
            confidence_level=lr_confidence or confidence,
            breakdown=safe_breakdown,
            features=safe_features,
            flags=safe_flags,
            heatmap_data=github_data.get("heatmap", {}),
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        # 7. Upsert skill tags — delete old, insert fresh
        skill_tags = extractor.extract_skill_tags(github_data)
        db.query(SkillTagModel).filter(SkillTagModel.user_id == user_id).delete()
        for tag_data in skill_tags:
            db.add(SkillTagModel(
                user_id=user_id,
                tag=tag_data["tag"],
                confidence=tag_data["confidence"],
                source=tag_data["source"],
            ))
        db.commit()

        # 8. Update streaks and milestones
        streak_svc = StreakService()
        streak_result = streak_svc.update_streak(
            db, user_id, github_data.get("heatmap", {})
        )
        streak_svc.check_behavior_milestones(
            db, user_id, features, is_first_analysis=is_first
        )

        return {
            "analysis_id": analysis.id,
            "tpr_score": tpr_score,
            "lr_score": lr_score,
            "confidence_level": confidence,
            "breakdown": safe_breakdown,
            "flags": safe_flags,
            "streak": streak_result,
            "data_quality": github_data.get("data_quality", "full"),
        }
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/trigger", response_model=JobStatusOut)
def trigger_analysis(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger a full GitHub analysis for the authenticated user.

    Returns immediately with a job_id. Poll GET /api/jobs/{job_id} for status.
    Privacy: always analyses the authenticated user's own github_username.
    """
    if not user.github_username:
        raise HTTPException(
            status_code=400,
            detail="No GitHub username linked to your account. Update your profile first.",
        )

    job = create_job(db, user.id, "base_analysis")
    background_tasks.add_task(
        run_in_background,
        job.id,
        _run_analysis,
        user.id,
        user.github_username,
    )
    return job


@router.get("/latest", response_model=AnalysisOut)
def get_latest_analysis(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the most recent Analysis for the authenticated user."""
    analysis = (
        db.query(Analysis)
        .filter(Analysis.user_id == user.id)
        .order_by(Analysis.created_at.desc())
        .first()
    )
    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="No analysis found. Run an analysis first.",
        )
    return analysis


@router.get("/history")
def get_analysis_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Return paginated analysis history for trend charts."""
    analyses = (
        db.query(Analysis)
        .filter(Analysis.user_id == user.id)
        .order_by(Analysis.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": a.id,
            "tpr_score": a.tpr_score,
            "lr_score": a.lr_score,
            "confidence_level": a.confidence_level,
            "created_at": a.created_at.isoformat(),
        }
        for a in analyses
    ]


@router.get("/heatmap")
def get_heatmap(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return 52-week commit heatmap from the most recent analysis."""
    analysis = (
        db.query(Analysis)
        .filter(Analysis.user_id == user.id)
        .order_by(Analysis.created_at.desc())
        .first()
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail="No analysis found.")
    return analysis.heatmap_data or {}


@router.get("/skills")
def get_skill_tags(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the user's extracted skill tags sorted by confidence."""
    tags = (
        db.query(SkillTag)
        .filter(SkillTag.user_id == user.id)
        .order_by(SkillTag.confidence.desc())
        .all()
    )
    return [
        {"tag": t.tag, "confidence": t.confidence, "source": t.source}
        for t in tags
    ]


@router.get("/streaks")
def get_streaks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return streak summary and earned milestones."""
    from services.streak_service import StreakService
    return StreakService().get_streak_summary(db, user.id)
