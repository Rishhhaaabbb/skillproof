# Task 2: Auth router — signup, login, refresh, and me endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.database import get_db
from models.schemas import LoginRequest, SignupRequest, TokenResponse, RefreshRequest, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user account.

    Creates a User row with a hashed password, then returns access and refresh
    tokens so the client is immediately authenticated.

    Returns HTTP 409 if the email is already registered.
    """
    return {"access_token": "stub", "refresh_token": "stub", "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email and password.

    Returns HTTP 401 if the credentials are incorrect.
    """
    return {"access_token": "stub", "refresh_token": "stub", "token_type": "bearer"}


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access token.

    Returns HTTP 401 if the refresh token is invalid or expired.
    """
    return {"access_token": "stub", "refresh_token": "stub", "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def me(db: Session = Depends(get_db)):
    """Return the authenticated user's profile.

    Protected by JWT Bearer auth (added in Task 2 implementation).
    """
    return {}
