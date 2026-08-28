# Task 3: Security utilities — password hashing and JWT token management
# Note: passlib removed — incompatible with bcrypt 5.x on Python 3.14.
# Using bcrypt directly instead.
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from config import settings


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt directly.

    Args:
        plain_password: The raw password supplied by the user.

    Returns:
        A bcrypt hash string safe to store in the database.
    """
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain_password:   The raw password to check.
        hashed_password:  The bcrypt hash stored in the database.

    Returns:
        True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(data: dict) -> str:
    """Create a short-lived JWT access token signed with JWT_SECRET.

    Args:
        data: Payload to encode — must include ``sub`` (user id as string).

    Returns:
        Signed JWT string.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a long-lived JWT refresh token signed with JWT_REFRESH_SECRET.

    Args:
        data: Payload to encode — must include ``sub`` (user id as string).

    Returns:
        Signed JWT string.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, settings.JWT_REFRESH_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token.

    Args:
        token: JWT string from the Authorization header.

    Returns:
        The decoded payload dict, or None if invalid / expired / wrong type.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT refresh token.

    Args:
        token: JWT string from the refresh request body.

    Returns:
        The decoded payload dict, or None if invalid / expired / wrong type.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_REFRESH_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None
