# Settings router — profile update, public toggle, account info, delete account
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, get_db
from models.database import Analysis, User
from models.schemas import UserOut, UserUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=UserOut)
def get_settings(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the current user's full profile."""
    return user


@router.patch("", response_model=UserOut)
def update_settings(
    payload: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update profile fields. All fields are optional — only provided fields change."""
    if payload.full_name is not None:
        user.full_name = payload.full_name.strip() or None
    if payload.github_username is not None:
        user.github_username = payload.github_username.strip() or None
    if payload.profile_headline is not None:
        user.profile_headline = payload.profile_headline.strip() or None
    if payload.is_public is not None:
        user.is_public = payload.is_public
    db.commit()
    db.refresh(user)
    return user


@router.get("/account-info")
def get_account_info(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return read-only account stats: email, member since, total analyses."""
    total_analyses = db.query(Analysis).filter(Analysis.user_id == user.id).count()
    return {
        "email": user.email,
        "member_since": user.created_at.isoformat(),
        "total_analyses": total_analyses,
    }


@router.delete("/account", status_code=204)
def delete_account(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Permanently delete the account and all associated data (cascade)."""
    db.delete(user)
    db.commit()
