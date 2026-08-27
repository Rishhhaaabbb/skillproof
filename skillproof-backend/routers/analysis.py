# Task 4/5/6: Analysis router — trigger analysis and retrieve results
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.database import get_db
from models.schemas import AnalysisOut, TriggerAnalysisRequest, JobStatusOut

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/trigger", response_model=JobStatusOut)
def trigger_analysis(payload: TriggerAnalysisRequest, db: Session = Depends(get_db)):
    """Enqueue a full GitHub analysis job for the authenticated user.

    Returns a JobStatusOut so the client can poll for completion.
    """
    return {"id": "stub-job-id", "user_id": 0, "job_type": "analysis", "status": "queued",
            "created_at": "2024-01-01T00:00:00"}


@router.get("/latest", response_model=AnalysisOut)
def get_latest_analysis(db: Session = Depends(get_db)):
    """Return the most recent Analysis for the authenticated user."""
    return {}


@router.get("/history")
def get_analysis_history(db: Session = Depends(get_db)):
    """Return all past Analysis records for the authenticated user."""
    return []
