# Task 7: Background job runner — async job execution with DB status tracking
"""
Lightweight background job infrastructure using FastAPI BackgroundTasks.

Pattern:
  1. Caller creates a Job row with status='queued' and gets back the job_id.
  2. Caller passes the job_id + a function to run_in_background().
  3. FastAPI runs the function in a thread pool (BackgroundTasks).
  4. Frontend polls GET /api/jobs/{job_id} until status is 'complete' or 'failed'.

No Redis, no Celery — Postgres is the job queue. Sufficient for this scale.
"""
from __future__ import annotations

import logging
import traceback
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from sqlalchemy.orm import Session

from models.database import Job, SessionLocal

logger = logging.getLogger(__name__)


def create_job(db: Session, user_id: int, job_type: str) -> Job:
    """Create a new Job row with status='queued' and return it.

    Args:
        db:       Active database session (caller's request session).
        user_id:  ID of the user who triggered the job.
        job_type: Short label, e.g. 'base_analysis', 'role_analysis'.

    Returns:
        The newly created and committed Job ORM instance.
    """
    job = Job(
        id=str(uuid.uuid4()),
        user_id=user_id,
        job_type=job_type,
        status="queued",
        created_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def run_in_background(
    job_id: str,
    fn: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> None:
    """Execute *fn* in a background thread with full job lifecycle management.

    Opens its own database session (separate from the request session to avoid
    cross-thread session sharing). Updates job status to 'processing' on start,
    stores the result on success, stores the error message on failure.

    This function is designed to be passed directly to FastAPI BackgroundTasks:

        background_tasks.add_task(run_in_background, job_id, my_fn, arg1, arg2)

    Args:
        job_id: UUID string of the Job row to update.
        fn:     The function to call. Must return a JSON-serialisable dict.
        *args:  Positional arguments forwarded to fn.
        **kwargs: Keyword arguments forwarded to fn.
    """
    db: Session = SessionLocal()
    try:
        # Mark as processing
        job = db.get(Job, job_id)
        if job is None:
            logger.error("Job %s not found in DB — aborting background run", job_id)
            return
        job.status = "processing"
        db.commit()

        # Execute the work function
        result = fn(*args, **kwargs)

        # Mark as complete
        job = db.get(Job, job_id)
        if job:
            job.status = "complete"
            job.result = result
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
        logger.info("Job %s completed successfully", job_id)

    except Exception as exc:
        logger.error("Job %s failed: %s", job_id, exc)
        tb = traceback.format_exc()
        try:
            job = db.get(Job, job_id)
            if job:
                job.status = "failed"
                job.error = f"{type(exc).__name__}: {exc}\n{tb}"
                job.completed_at = datetime.now(timezone.utc)
                db.commit()
        except Exception as inner:
            logger.error("Failed to update job %s error state: %s", job_id, inner)
    finally:
        db.close()
