# Task 2: Auth dependencies — FastAPI dependency injection helpers
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from models.database import get_db, User
from utils.security import decode_access_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency that validates the Bearer token and returns the User.

    Raises HTTP 401 if the token is missing, expired, or invalid.
    Raises HTTP 401 if the user referenced in the token no longer exists.

    Args:
        credentials: Injected by HTTPBearer from the Authorization header.
        db:          Injected database session.

    Returns:
        The authenticated User ORM instance.
    """
    pass


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
) -> User | None:
    """Like :func:`get_current_user` but returns None instead of raising on missing token.

    Used for routes that are accessible both publicly (anonymous) and
    authenticated (personalised).

    Args:
        credentials: Optional injected credentials (None when no Bearer header).
        db:          Injected database session.

    Returns:
        The authenticated User ORM instance, or None if unauthenticated.
    """
    pass
