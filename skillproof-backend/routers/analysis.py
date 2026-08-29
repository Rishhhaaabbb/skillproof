# Task 8: Analysis router — fully implemented in Task 8
# This stub boots cleanly and defines correct route signatures
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, get_db
from models.database import Analysis, User

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/trigger")
def trigger_analysis(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger a full GitHub analysis. Fully implemented in Task 8."""
    return {"status": "not_yet_implemented", "message": "Coming in Task 8"}


@router.get("/latest")
def get_latest_analysis(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return latest analysis. Fully implemented in Task 8."""
    return {"status": "not_yet_implemented"}


@router.get("/history")
def get_analysis_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return analysis history. Fully implemented in Task 8."""
    return []


@router.get("/heatmap")
def get_heatmap(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return 52-week heatmap. Fully implemented in Task 8."""
    return {}
