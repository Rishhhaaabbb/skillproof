# Task 3 (prerequisite): Jobs router — poll async background job status
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, get_db
from models.database import Job, User
from models.schemas import JobStatusOut

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusOut)
def get_job_status(
    job_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the current status and result of a background job.

    Only the job's owner can query it — returns 404 for jobs belonging to
    other users (intentionally indistinguishable from a missing job to avoid
    leaking the existence of other users' jobs).

    Args:
        job_id: UUID string of the job to query.
        user:   Authenticated user from Bearer token.
        db:     Database session.
    """
    job = db.get(Job, job_id)
    if job is None or job.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
