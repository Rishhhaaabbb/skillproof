# Task 13: Share router — shareable profile token management and recruiter requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.database import get_db
from models.schemas import ShareTokenOut, RecruiterRequestCreate, RecruiterRequestOut

router = APIRouter(prefix="/api/share", tags=["share"])


@router.post("/token", response_model=ShareTokenOut, status_code=201)
def create_share_token(db: Session = Depends(get_db)):
    """Generate a new shareable profile token for the authenticated user."""
    return {}


@router.get("/token", response_model=ShareTokenOut)
def get_share_token(db: Session = Depends(get_db)):
    """Return the user's active share token (or 404 if none exists)."""
    return {}


@router.delete("/token", status_code=204)
def revoke_share_token(db: Session = Depends(get_db)):
    """Revoke the user's share token."""
    return None


@router.post("/{token}/contact", response_model=RecruiterRequestOut, status_code=201)
def recruiter_contact(token: str, payload: RecruiterRequestCreate, db: Session = Depends(get_db)):
    """Submit a recruiter contact request via a share token."""
    return {}
