# Task 13: Jobs router — polling endpoint for async background job status
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.database import get_db
from models.schemas import JobStatusOut

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusOut)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Return the current status and result of a background job.

    Returns HTTP 404 if the job does not exist or does not belong to the
    authenticated user.
    """
    # Full implementation in Task 13
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
