# Task 1: Security utility stubs — JWT and password helpers
from typing import Optional


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt.

    Args:
        plain_password: The raw password supplied by the user.

    Returns:
        A bcrypt hash string safe to store in the database.
    """
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain_password:   The raw password to check.
        hashed_password:  The bcrypt hash stored in the database.

    Returns:
        True if the password matches, False otherwise.
    """
    pass


def create_access_token(data: dict) -> str:
    """Create a short-lived JWT access token.

    Encodes *data* with the configured JWT_SECRET and an expiry derived from
    ``settings.JWT_EXPIRE_MINUTES``.

    Args:
        data: Payload to encode (must include ``sub`` — the user's id or email).

    Returns:
        Signed JWT string.
    """
    pass


def create_refresh_token(data: dict) -> str:
    """Create a long-lived JWT refresh token.

    Encodes *data* with the configured JWT_REFRESH_SECRET and an expiry
    derived from ``settings.JWT_REFRESH_EXPIRE_DAYS``.

    Args:
        data: Payload to encode (must include ``sub``).

    Returns:
        Signed JWT string.
    """
    pass


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token.

    Args:
        token: JWT string from the Authorization header.

    Returns:
        The decoded payload dict, or None if the token is invalid / expired.
    """
    pass


def decode_refresh_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT refresh token.

    Args:
        token: JWT string from the refresh request body.

    Returns:
        The decoded payload dict, or None if the token is invalid / expired.
    """
    pass
