"""Test configuration and reusable fixtures for VocabMaster."""

import os
import tempfile
from pathlib import Path
from typing import Generator
import pytest
from fastapi.testclient import TestClient

from vocabmaster.api.app import create_app
from vocabmaster.db.connection import get_db, DatabaseManager
from vocabmaster.db.migrations import init_db
from vocabmaster.db import repository
from vocabmaster.auth.security import hash_password
from vocabmaster.auth.tokens import create_access_token


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    """Create a temporary SQLite database file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        path = tf.name
    init_db(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def test_user(temp_db_path: str):
    """Create a standard test user."""
    with get_db(temp_db_path) as conn:
        pwd_hash, salt = hash_password("secretpassword123")
        user = repository.create_user(
            conn,
            user_id="user-123-uuid",
            username="tester",
            email="tester@example.com",
            password_hash=pwd_hash,
            salt=salt,
        )
        return user


@pytest.fixture
def other_user(temp_db_path: str):
    """Create a second test user for isolation tests."""
    with get_db(temp_db_path) as conn:
        pwd_hash, salt = hash_password("otherpass123")
        user = repository.create_user(
            conn,
            user_id="user-456-uuid",
            username="otheruser",
            email="other@example.com",
            password_hash=pwd_hash,
            salt=salt,
        )
        return user


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token({"sub": test_user["id"], "username": test_user["username"]})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_auth_headers(other_user):
    token = create_access_token({"sub": other_user["id"], "username": other_user["username"]})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client(temp_db_path: str) -> Generator[TestClient, None, None]:
    app = create_app(temp_db_path)
    with TestClient(app) as test_client:
        yield test_client
