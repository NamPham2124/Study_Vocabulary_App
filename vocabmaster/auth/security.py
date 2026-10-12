"""Password hashing and cryptographic security utilities."""

import hashlib
import hmac
import secrets
from typing import Tuple


PBKDF2_ITERATIONS = 120_000
HASH_ALGORITHM = "sha256"


def hash_password(password: str, salt: str = "") -> Tuple[str, str]:
    """
    Hash a password with PBKDF2-HMAC-SHA256.
    Returns (hex_hash, hex_salt).
    """
    if not salt:
        salt = secrets.token_hex(16)

    key = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM,
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return key.hex(), salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verify password against salt and expected hash using constant-time check."""
    computed_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(computed_hash, password_hash)
