"""Integration and unit tests for Language Workspaces, Bounded Limits, and Deck Isolation."""

import tempfile
import uuid
import pytest
from fastapi.testclient import TestClient

from vocabmaster.api.app import create_app
from vocabmaster.db.connection import get_db
from vocabmaster.db import repository
from vocabmaster.session import manager as session_manager


@pytest.fixture
def test_app_and_client():
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        app = create_app(db_path=tmp.name)
        client = TestClient(app)
        yield app, client, tmp.name


def register_and_login(client: TestClient, username: str, email: str, language: str = "en") -> str:
    res = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "Password123!",
            "interface_language": "vi",
            "active_learning_language": language,
            "script_preference": "hans",
        },
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def test_post_login_workspace_onboarding_and_switching(test_app_and_client):
    app, client, db_path = test_app_and_client
    token = register_and_login(client, "user_workspace", "ws@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Check me: initially has_selected_language should be False
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["has_selected_language"] is False

    # 2. Select Chinese Workspace
    ws_res = client.post(
        "/api/users/workspace",
        headers=headers,
        json={"language": "zh", "script_preference": "hant"},
    )
    assert ws_res.status_code == 200
    assert ws_res.json()["active_learning_language"] == "zh"
    assert ws_res.json()["has_selected_language"] is True

    # 3. Verify me reflects the change
    me_res2 = client.get("/api/auth/me", headers=headers)
    assert me_res2.status_code == 200
    assert me_res2.json()["active_learning_language"] == "zh"
    assert me_res2.json()["has_selected_language"] is True
    assert me_res2.json()["script_preference"] == "hant"

    # 4. Switch back to English Workspace
    ws_res2 = client.post(
        "/api/users/workspace",
        headers=headers,
        json={"language": "en"},
    )
    assert ws_res2.status_code == 200
    assert ws_res2.json()["active_learning_language"] == "en"


def test_strict_language_isolation(test_app_and_client):
    app, client, db_path = test_app_and_client
    token = register_and_login(client, "isolation_user", "iso@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create English Deck and Chinese Deck
    en_deck = client.post(
        "/api/decks",
        headers=headers,
        json={"name": "English Deck", "target_language": "en", "tags": ["ielts"]},
    ).json()

    zh_deck = client.post(
        "/api/decks",
        headers=headers,
        json={"name": "Chinese Deck", "target_language": "zh", "tags": ["hsk3"]},
    ).json()

    # Add English Vocab
    en_vocab = client.post(
        f"/api/decks/{en_deck['id']}/vocab",
        headers=headers,
        json={
            "deck_id": en_deck["id"],
            "language": "en",
            "term": "ubiquitous",
            "definition": "phổ biến ở mọi nơi",
            "ipa": "/juːˈbɪk.wɪ.təs/",
            "tags": ["ielts", "advanced"],
            "language_specific_fields": {},
        },
    ).json()

    # Add Chinese Vocab
    zh_vocab = client.post(
        f"/api/decks/{zh_deck['id']}/vocab",
        headers=headers,
        json={
            "deck_id": zh_deck["id"],
            "language": "zh",
            "term": "你好",
            "definition": "xin chào",
            "tags": ["hsk1"],
            "language_specific_fields": {
                "simplified": "你好",
                "traditional": "你好",
                "pinyin": "nǐ hǎo",
                "hsk_level": "HSK 1",
            },
        },
    ).json()

    # Query decks filtering by language
    en_decks_res = client.get("/api/decks?language=en", headers=headers).json()
    assert len(en_decks_res) == 1
    assert en_decks_res[0]["id"] == en_deck["id"]

    zh_decks_res = client.get("/api/decks?language=zh", headers=headers).json()
    assert len(zh_decks_res) == 1
    assert zh_decks_res[0]["id"] == zh_deck["id"]

    # Query vocab items filtering by language
    en_vocab_res = client.get("/api/vocab?language=en", headers=headers).json()
    assert len(en_vocab_res) == 1
    assert en_vocab_res[0]["term"] == "ubiquitous"

    zh_vocab_res = client.get("/api/vocab?language=zh", headers=headers).json()
    assert len(zh_vocab_res) == 1
    assert zh_vocab_res[0]["term"] == "你好"

    # Query tags filtering by language
    en_tags = client.get("/api/tags?language=en", headers=headers).json()
    assert "ielts" in en_tags
    assert "hsk1" not in en_tags

    zh_tags = client.get("/api/tags?language=zh", headers=headers).json()
    assert "hsk1" in zh_tags
    assert "ielts" not in zh_tags


def test_bounded_daily_limits_enforcement(test_app_and_client):
    app, client, db_path = test_app_and_client
    token = register_and_login(client, "bounded_user", "bounded@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create deck with limit: max 2 new cards per day
    deck = client.post(
        "/api/decks",
        headers=headers,
        json={
            "name": "Strict Daily Limit Deck",
            "target_language": "en",
            "max_new_cards_per_day": 2,
            "max_reviews_per_day": 10,
        },
    ).json()

    # Add 4 words
    for word in ["apple", "banana", "cherry", "date"]:
        client.post(
            f"/api/decks/{deck['id']}/vocab",
            headers=headers,
            json={
                "deck_id": deck["id"],
                "language": "en",
                "term": word,
                "definition": f"meaning of {word}",
                "ipa": "/test/",
                "language_specific_fields": {},
            },
        )

    # 1. Start bounded session: should strictly pick only 2 new cards (daily limit)
    sess_res = client.post(
        "/api/sessions/start",
        headers=headers,
        json={"deck_id": deck["id"], "unlimited": False},
    )
    assert sess_res.status_code == 200
    sess_data = sess_res.json()["session"]
    assert sess_data["total_cards"] == 2
    session_id = sess_data["id"]

    # Answer the 2 cards
    ans1 = client.post(
        f"/api/sessions/{session_id}/answer",
        headers=headers,
        json={"rating": 4, "time_spent_seconds": 5},
    ).json()
    ans2 = client.post(
        f"/api/sessions/{session_id}/answer",
        headers=headers,
        json={"rating": 5, "time_spent_seconds": 5},
    ).json()
    assert ans2["is_completed"] is True

    # 2. Start another session today without unlimited: daily limit of 2 was reached, so queue is empty!
    sess_res2 = client.post(
        "/api/sessions/start",
        headers=headers,
        json={"deck_id": deck["id"], "unlimited": False},
    )
    assert sess_res2.status_code == 200
    sess_data2 = sess_res2.json()["session"]
    assert sess_data2["total_cards"] == 0
    assert sess_data2["status"] == "COMPLETED"

    # 3. Start session with unlimited=True: should fetch remaining new cards!
    sess_res_unlimited = client.post(
        "/api/sessions/start",
        headers=headers,
        json={"deck_id": deck["id"], "unlimited": True},
    )
    assert sess_res_unlimited.status_code == 200
    sess_data_unl = sess_res_unlimited.json()["session"]
    assert sess_data_unl["total_cards"] == 2  # cherry and date


def test_safe_deck_deletion_with_fallback(test_app_and_client):
    app, client, db_path = test_app_and_client
    token = register_and_login(client, "safe_del_user", "del@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create Deck A
    deck_a = client.post(
        "/api/decks",
        headers=headers,
        json={"name": "Temporary Deck", "target_language": "en"},
    ).json()

    # Add 2 words to Deck A
    v1 = client.post(
        f"/api/decks/{deck_a['id']}/vocab",
        headers=headers,
        json={
            "deck_id": deck_a["id"],
            "language": "en",
            "term": "preserve",
            "definition": "bảo tồn",
            "ipa": "/prɪˈzɜːv/",
            "language_specific_fields": {},
        },
    ).json()

    # Delete Deck A with delete_vocabulary=False (default safe mode)
    del_res = client.delete(f"/api/decks/{deck_a['id']}?delete_vocabulary=false", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["vocabulary_deleted"] is False

    # Check that vocabulary item is still intact and reassigned to fallback deck
    v1_check = client.get(f"/api/vocab/{v1['id']}", headers=headers)
    assert v1_check.status_code == 200
    updated_v1 = v1_check.json()
    assert updated_v1["term"] == "preserve"
    assert updated_v1["deck_id"] != deck_a["id"]

    # Verify fallback deck exists in deck list
    decks = client.get("/api/decks?language=en", headers=headers).json()
    assert any("Từ Vựng Chung" in d["name"] for d in decks)

    # Now create Deck B and delete with delete_vocabulary=True
    deck_b = client.post(
        "/api/decks",
        headers=headers,
        json={"name": "Disposable Deck", "target_language": "en"},
    ).json()
    v2 = client.post(
        f"/api/decks/{deck_b['id']}/vocab",
        headers=headers,
        json={
            "deck_id": deck_b["id"],
            "language": "en",
            "term": "ephemeral",
            "definition": "phù du",
            "ipa": "/ɪˈfem.ər.əl/",
            "language_specific_fields": {},
        },
    ).json()

    del_b = client.delete(f"/api/decks/{deck_b['id']}?delete_vocabulary=true", headers=headers)
    assert del_b.status_code == 200
    assert del_b.json()["vocabulary_deleted"] is True

    # Word should be permanently deleted
    v2_check = client.get(f"/api/vocab/{v2['id']}", headers=headers)
    assert v2_check.status_code == 404


def test_idempotent_srs_card_creation(test_app_and_client):
    app, client, db_path = test_app_and_client
    with get_db(db_path) as conn:
        user = repository.create_user(
            conn,
            user_id="idemp_user",
            username="idemp_user",
            email="idemp@example.com",
            password_hash="hash",
            salt="salt",
        )
        deck = repository.create_deck(conn, deck_id="deck_idemp", user_id="idemp_user", name="Idemp")
        vocab = repository.create_vocab_item(
            conn,
            {
                "id": "v_idemp",
                "deck_id": "deck_idemp",
                "user_id": "idemp_user",
                "language": "en",
                "term": "test",
                "definition": "test def",
                "ipa": "/t/",
            },
        )
        # First creation
        c1 = repository.create_srs_card(
            conn,
            {
                "id": "card_1",
                "vocab_id": "v_idemp",
                "deck_id": "deck_idemp",
                "user_id": "idemp_user",
                "state": "NEW",
            },
        )
        # Second creation with different ID for same vocab_id
        c2 = repository.create_srs_card(
            conn,
            {
                "id": "card_2",
                "vocab_id": "v_idemp",
                "deck_id": "deck_idemp",
                "user_id": "idemp_user",
                "state": "NEW",
            },
        )
        # Should return existing card idempotently
        assert c1["id"] == c2["id"] == "card_1"
