# Task 12: Scheduler router — GitHub Actions cron trigger endpoint
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from models.database import get_db

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


@router.post("/run")
def run_scheduled_jobs(
    x_scheduler_secret: str = Header(..., alias="X-Scheduler-Secret"),
    db: Session = Depends(get_db),
):
    """Trigger the nightly scheduled job batch (re-analysis + streak updates).

    Protected by SCHEDULER_SECRET header — only callable by GitHub Actions cron.
    Returns HTTP 403 if the secret does not match.
    """
    if x_scheduler_secret != settings.SCHEDULER_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid scheduler secret")
    # Full implementation in Task 12
    return {"status": "scheduled jobs enqueued", "count": 0}
