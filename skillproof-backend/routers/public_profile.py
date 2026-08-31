# Task 13: Public profile router — /u/{username} public page + settings endpoint
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, get_db
from models.database import Analysis, Milestone, SkillTag, User
from models.schemas import UserUpdate

router = APIRouter(tags=["public-profile"])


@router.get("/u/{username}")
def get_public_profile(username: str, db: Session = Depends(get_db)):
    """Return the public profile for a user who has opted in (is_public=True).

    Returns 404 for non-public users — indistinguishable from non-existent
    users to prevent username enumeration.
    """
    user = db.query(User).filter(User.github_username == username).first()
    if not user or not user.is_public:
        raise HTTPException(status_code=404, detail="Profile not found.")

    analysis = (
        db.query(Analysis)
        .filter(Analysis.user_id == user.id)
        .order_by(Analysis.created_at.desc())
        .first()
    )
    tags = (
        db.query(SkillTag)
        .filter(SkillTag.user_id == user.id)
        .order_by(SkillTag.confidence.desc())
        .limit(10)
        .all()
    )
    milestones = db.query(Milestone).filter(Milestone.user_id == user.id).all()

    tpr = analysis.tpr_score if analysis else 0
    tier_label = "Strong" if tpr >= 65 else ("Developing" if tpr >= 35 else "Early Stage")

    return {
        "github_username": user.github_username,
        "full_name": user.full_name,
        "profile_headline": user.profile_headline,
        "tier_label": tier_label,
        "current_streak": user.current_streak,
        "longest_streak": user.longest_streak,
        "skill_tags": [{"tag": t.tag, "source": t.source} for t in tags],
        "milestones": [{"label": m.milestone_label, "key": m.milestone_key} for m in milestones],
        "heatmap": analysis.heatmap_data if analysis else {},
    }


@router.patch("/api/settings")
def update_settings(
    payload: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile settings — headline, public visibility, github username."""
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.profile_headline is not None:
        user.profile_headline = payload.profile_headline
    if payload.is_public is not None:
        user.is_public = payload.is_public
    if payload.github_username is not None:
        user.github_username = payload.github_username
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "github_username": user.github_username,
        "profile_headline": user.profile_headline,
        "is_public": user.is_public,
    }
