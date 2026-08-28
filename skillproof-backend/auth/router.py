# Task 3: Auth router — signup, login, token refresh, and me endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from auth.dependencies import get_current_user, get_db
from models.database import Milestone, User
from models.schemas import (
    LoginRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
    UserOut,
)
from utils.cache import TTLCache
from utils.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# Module-level cache instance for login rate limiting.
# Tracks failed attempt counts per email with a 60-second rolling window.
_login_attempt_cache = TTLCache(default_ttl=60)

_MAX_LOGIN_ATTEMPTS = 10
_LOGIN_WINDOW_SECONDS = 60


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _issue_tokens(user_id: int) -> TokenResponse:
    """Issue a fresh access + refresh token pair for the given user id."""
    token_data = {"sub": str(user_id)}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user account.

    - Validates password length (minimum 8 characters).
    - Returns HTTP 409 if the email is already registered.
    - Awards the 'account_created' milestone on success.
    - Returns both access and refresh tokens so the client is immediately
      authenticated after signup.
    """
    # Password length validation
    if len(payload.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters",
        )

    # Email uniqueness check
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Create user
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        github_username=payload.github_username,
        full_name=payload.full_name,
    )
    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Award welcome milestone — use merge so duplicate inserts are silently ignored
    milestone = Milestone(
        user_id=user.id,
        milestone_key="account_created",
        milestone_label="Account Created",
    )
    db.add(milestone)
    try:
        db.commit()
    except IntegrityError:
        # Milestone already exists — safe to ignore
        db.rollback()

    return _issue_tokens(user.id)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email and password.

    - Rate-limited to 10 failed attempts per email per 60-second window.
    - Returns HTTP 429 when the rate limit is exceeded.
    - Returns HTTP 401 for invalid credentials (same message for wrong email
      and wrong password — never reveal which field is incorrect).
    - Clears the failure counter on successful login.
    """
    rate_key = f"login_attempts:{payload.email}"

    # Rate limit check
    attempts: int = _login_attempt_cache.get(rate_key) or 0
    if attempts >= _MAX_LOGIN_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        )

    # Credential validation — intentionally identical error for both cases
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        # Increment failure counter
        _login_attempt_cache.set(
            rate_key,
            attempts + 1,
            ttl=_LOGIN_WINDOW_SECONDS,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Successful login — clear failure counter
    _login_attempt_cache.invalidate(rate_key)

    return _issue_tokens(user.id)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access + refresh token pair.

    Tokens are rotated on use — the submitted refresh token is invalidated
    (by virtue of expiry / signature; no server-side denylist at this scale)
    and a fresh pair is returned.

    Returns HTTP 401 if the refresh token is invalid or expired.
    """
    token_payload = decode_refresh_token(payload.refresh_token)
    if token_payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id_str = token_payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed refresh token",
        )

    # Confirm user still exists
    user = db.get(User, int(user_id_str))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return _issue_tokens(user.id)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    """Return the authenticated user's profile.

    Protected by JWT Bearer auth via the get_current_user dependency.
    """
    return user
