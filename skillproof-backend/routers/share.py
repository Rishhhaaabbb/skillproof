# Task 13: Share router — share tokens and recruiter requests
"""
Share token endpoints:
  POST /api/share/token            — generate share token
  GET  /api/share/token            — get current token
  DELETE /api/share/token          — revoke token
  GET  /api/share/requests         — candidate views incoming recruiter requests
  GET  /api/share/{token}          — public recruiter view (no auth required)
  POST /api/share/{token}/request  — recruiter submits contact request
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, get_db
from models.database import (
    Analysis, Milestone, Notification, RecruiterRequest,
    ShareToken, SkillTag, User,
)
from models.schemas import RecruiterRequestCreate, RecruiterRequestOut, ShareTokenOut

router = APIRouter(prefix="/api/share", tags=["share"])

_TOKEN_EXPIRY_DAYS = 90


@router.post("/token", response_model=ShareTokenOut, status_code=201)
def create_share_token(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a new shareable profile token. Revokes any existing token first."""
    existing = db.query(ShareToken).filter(ShareToken.user_id == user.id).first()
    if existing:
        db.delete(existing)
        db.commit()

    token = ShareToken(
        user_id=user.id,
        token=secrets.token_urlsafe(48),
        expires_at=datetime.now(timezone.utc) + timedelta(days=_TOKEN_EXPIRY_DAYS),
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


@router.get("/token", response_model=ShareTokenOut)
def get_share_token(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the user's active share token."""
    token = db.query(ShareToken).filter(ShareToken.user_id == user.id).first()
    if not token:
        raise HTTPException(
            status_code=404, detail="No share token found. Create one first."
        )
    return token


@router.delete("/token", status_code=204)
def revoke_share_token(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revoke the user's share token."""
    token = db.query(ShareToken).filter(ShareToken.user_id == user.id).first()
    if token:
        db.delete(token)
        db.commit()


@router.get("/requests", response_model=List[RecruiterRequestOut])
def get_recruiter_requests(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return incoming recruiter requests for the authenticated candidate."""
    return (
        db.query(RecruiterRequest)
        .filter(RecruiterRequest.candidate_user_id == user.id)
        .order_by(RecruiterRequest.created_at.desc())
        .all()
    )


@router.get("/{token}")
def get_shared_profile(token: str, db: Session = Depends(get_db)):
    """Public recruiter view — no auth required.

    Returns TPR score, top strengths, skill tags, milestones.
    Does NOT expose: gap details, missing requirements, raw features.
    """
    share_token = db.query(ShareToken).filter(ShareToken.token == token).first()
    if not share_token:
        raise HTTPException(
            status_code=404,
            detail="This report link is invalid or has been revoked.",
        )

    if share_token.expires_at:
        expires = share_token.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires:
            raise HTTPException(
                status_code=404,
                detail="This report link has expired. Ask the candidate to generate a new one.",
            )

    user = db.get(User, share_token.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found.")

    analysis = (
        db.query(Analysis)
        .filter(Analysis.user_id == user.id)
        .order_by(Analysis.created_at.desc())
        .first()
    )

    top_strengths: list = []
    if analysis and analysis.flags:
        top_strengths = (analysis.flags.get("green_flags") or [])[:3]

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
        "candidate_name": user.full_name or user.github_username,
        "github_username": user.github_username,
        "profile_headline": user.profile_headline,
        "tpr_score": tpr,
        "tier_label": tier_label,
        "top_strengths": top_strengths,
        "skill_tags": [{"tag": t.tag, "source": t.source} for t in tags],
        "milestones": [{"label": m.milestone_label, "key": m.milestone_key} for m in milestones],
        "current_streak": user.current_streak,
        "share_token": token,
    }


@router.post("/{token}/request", response_model=RecruiterRequestOut, status_code=201)
def recruiter_request(
    token: str,
    payload: RecruiterRequestCreate,
    db: Session = Depends(get_db),
):
    """Submit a recruiter contact request via a share token — no auth required."""
    share_token = db.query(ShareToken).filter(ShareToken.token == token).first()
    if not share_token:
        raise HTTPException(status_code=404, detail="Invalid share link.")

    req = RecruiterRequest(
        share_token_id=share_token.id,
        candidate_user_id=share_token.user_id,
        recruiter_name=payload.recruiter_name,
        recruiter_email=payload.recruiter_email,
        recruiter_company=payload.recruiter_company,
        message=payload.message,
    )
    db.add(req)

    company_str = f" from {payload.recruiter_company}" if payload.recruiter_company else ""
    db.add(Notification(
        user_id=share_token.user_id,
        message=f"Recruiter {payload.recruiter_name}{company_str} viewed your profile and sent a request.",
    ))
    db.commit()
    db.refresh(req)
    return req
