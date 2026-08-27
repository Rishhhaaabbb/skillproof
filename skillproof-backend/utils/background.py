# Task 1: Background job runner stub
from typing import Any, Callable


def run_in_background(job_id: str, db_session_factory: Any, fn: Callable, *args: Any) -> None:
    """Enqueue *fn* to run asynchronously in a background thread.

    This stub will be fully implemented in Task 13 (job queue).

    Args:
        job_id:             UUID string identifying the Job row in the database.
        db_session_factory: A callable (e.g. ``SessionLocal``) that returns a
                            new SQLAlchemy session for the background thread to
                            use.  The worker is responsible for committing and
                            closing this session.
        fn:                 The function to invoke in the background.  Must
                            accept a live database session as its first
                            positional argument, followed by ``*args``.
        *args:              Additional positional arguments forwarded to *fn*
                            after the session.

    Returns:
        None.  The caller should monitor progress via the Job table.
    """
    pass
