"""Unit tests for authentication, password hashing, JWT tokens, and access control."""

from datetime import timedelta
import pytest
from vocabmaster.auth.security import hash_password, verify_password
from vocabmaster.auth.tokens import (
    create_access_token,
    decode_access_token,
    AuthenticationError,
)
from vocabmaster.auth.access_control import enforce_ownership, AccessDeniedError


def test_password_hashing_and_verification():
    raw_pass = "SuperSecurePassword999!"
    pwd_hash, salt = hash_password(raw_pass)

    assert pwd_hash is not None
    assert salt is not None
    assert len(salt) == 32  # 16 bytes hex

    assert verify_password(raw_pass, pwd_hash, salt) is True
    assert verify_password("wrong_password", pwd_hash, salt) is False


def test_jwt_token_lifecycle():
    payload = {"sub": "user-uuid-1", "username": "alice"}
    token = create_access_token(payload, expires_delta=timedelta(minutes=5))
    decoded = decode_access_token(token)

    assert decoded["sub"] == "user-uuid-1"
    assert decoded["username"] == "alice"
    assert "exp" in decoded


def test_jwt_expired_token():
    payload = {"sub": "user-uuid-1", "username": "alice"}
    token = create_access_token(payload, expires_delta=timedelta(seconds=-10))

    with pytest.raises(AuthenticationError, match="Token has expired"):
        decode_access_token(token)


def test_jwt_invalid_token():
    with pytest.raises(AuthenticationError, match="Invalid token"):
        decode_access_token("corrupted.token.value")


def test_enforce_resource_ownership():
    resource = {"id": "res-1", "user_id": "user-alice"}

    # Alice accessing her own resource should pass
    enforce_ownership(resource, "user-alice", "deck")

    # Bob attempting to access Alice's resource must raise AccessDeniedError
    with pytest.raises(AccessDeniedError, match="Access denied"):
        enforce_ownership(resource, "user-bob", "deck")
