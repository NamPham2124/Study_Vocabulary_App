"""Authentication and security module."""

from vocabmaster.auth.security import hash_password, verify_password
from vocabmaster.auth.tokens import create_access_token, decode_access_token
from vocabmaster.auth.access_control import enforce_ownership, AccessDeniedError

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "enforce_ownership",
    "AccessDeniedError",
]
