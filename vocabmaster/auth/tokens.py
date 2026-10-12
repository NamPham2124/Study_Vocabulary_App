"""JWT token creation, validation, and error classes."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from vocabmaster.config import settings


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Encode payload into signed JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "iat": now})
    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return token


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and verify JWT token. Raises AuthenticationError on failure."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")
