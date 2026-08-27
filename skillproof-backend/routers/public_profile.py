# Task 13: Public profile router — read-only public-facing profile endpoints
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.database import get_db

router = APIRouter(prefix="/api/u", tags=["public-profile"])


@router.get("/{username}")
def get_public_profile(username: str, db: Session = Depends(get_db)):
    """Return the public profile for a user whose is_public flag is True.

    Returns HTTP 404 if the user does not exist or has not opted in to a
    public profile.
    """
    return {"username": username, "message": "stub"}


@router.get("/share/{token}")
def get_shared_profile(token: str, db: Session = Depends(get_db)):
    """Return a full-detail profile view accessed via a share token.

    Returns HTTP 404 if the token is invalid or expired.
    """
    return {"token": token, "message": "stub"}
