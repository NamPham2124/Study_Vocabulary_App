"""End-to-end integration tests for REST API workflows and multi-tenant security."""

import pytest


def test_api_auth_and_user_flows(client):
    # 1. Register
    reg_payload = {
        "username": "api_user",
        "email": "api_user@example.com",
        "password": "Password123!",
    }
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 200
    token_data = res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 2. Duplicate registration fails
    dup_res = client.post("/api/auth/register", json=reg_payload)
    assert dup_res.status_code == 400

    # 3. Login
    login_res = client.post(
        "/api/auth/login",
        json={"email": "api_user@example.com", "password": "Password123!"},
    )
    assert login_res.status_code == 200

    # 4. /api/auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "api_user"


def test_api_deck_and_vocabulary_crud(client, auth_headers):
    # 1. Create Deck
    deck_res = client.post(
        "/api/decks",
        json={"name": "German B1", "description": "Core B1 vocab", "target_language": "de"},
        headers=auth_headers,
    )
    assert deck_res.status_code == 200
    deck = deck_res.json()
    deck_id = deck["id"]
    assert deck["target_language"] == "de"

    # 2. Add Vocabulary Item
    vocab_payload = {
        "deck_id": deck_id,
        "term": "die Herausforderung",
        "definition": "challenge",
        "language": "de",
        "ipa": "/hɛˈʁaʊ̯sˌfɔʁdəʁʊŋ/",
        "part_of_speech": "noun",
        "examples": ["Das ist eine große Herausforderung."],
        "language_specific_fields": {
            "article": "die",
            "gender": "feminine",
            "plural_form": "die Herausforderungen",
            "cefr_level": "B1",
        },
    }
    vocab_res = client.post(f"/api/decks/{deck_id}/vocab", json=vocab_payload, headers=auth_headers)
    assert vocab_res.status_code == 200
    vocab = vocab_res.json()
    vocab_id = vocab["id"]
    assert vocab["term"] == "die Herausforderung"
    assert vocab["language_specific_fields"]["article"] == "die"

    # 3. List Vocabulary
    list_res = client.get(f"/api/decks/{deck_id}/vocab", headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 4. Update Vocabulary
    update_res = client.put(
        f"/api/vocab/{vocab_id}",
        json={"definition": "a big challenge"},
        headers=auth_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["definition"] == "a big challenge"


def test_api_multi_tenant_isolation(client, auth_headers, other_auth_headers):
    # User 1 creates a deck
    d_res = client.post(
        "/api/decks",
        json={"name": "User 1 Secret Deck", "target_language": "en"},
        headers=auth_headers,
    )
    deck_id = d_res.json()["id"]

    # User 2 attempts to get User 1's deck -> should receive 404
    u2_res = client.get(f"/api/decks/{deck_id}", headers=other_auth_headers)
    assert u2_res.status_code == 404

    # User 2 attempts to delete User 1's deck -> 404
    u2_del = client.delete(f"/api/decks/{deck_id}", headers=other_auth_headers)
    assert u2_del.status_code == 404


def test_api_study_session_e2e(client, auth_headers):
    # Create deck
    d_res = client.post(
        "/api/decks",
        json={"name": "API Study Deck", "target_language": "en"},
        headers=auth_headers,
    )
    deck_id = d_res.json()["id"]

    # Upload CSV
    csv_data = "term,definition\nserendipity,finding good things without looking\nepiphany,a sudden striking realization\n"
    files = {"file": ("words.csv", csv_data.encode("utf-8"), "text/csv")}
    imp_res = client.post(f"/api/decks/{deck_id}/import", files=files, headers=auth_headers)
    assert imp_res.status_code == 200
    assert imp_res.json()["imported_count"] == 2

    # Start Session
    start_res = client.post("/api/sessions/start", json={"deck_id": deck_id}, headers=auth_headers)
    assert start_res.status_code == 200
    sess_data = start_res.json()
    session_id = sess_data["session"]["id"]
    assert sess_data["session"]["total_cards"] == 2

    # Answer card 1
    ans_res = client.post(
        f"/api/sessions/{session_id}/answer",
        json={"rating": 4, "time_spent_seconds": 2.1},
        headers=auth_headers,
    )
    assert ans_res.status_code == 200
    assert ans_res.json()["completed_cards"] == 1

    # Pause Session
    pause_res = client.post(f"/api/sessions/{session_id}/pause", headers=auth_headers)
    assert pause_res.status_code == 200
    assert pause_res.json()["status"] == "PAUSED"

    # Verify /api/sessions/active returns the paused session
    active_res = client.get("/api/sessions/active", headers=auth_headers)
    assert active_res.status_code == 200
    assert active_res.json()["active"] is True
    assert active_res.json()["session"]["id"] == session_id

    # Resume Session
    resume_res = client.post(f"/api/sessions/{session_id}/resume", headers=auth_headers)
    assert resume_res.status_code == 200
    assert resume_res.json()["session"]["status"] == "ACTIVE"

    # Answer second card
    ans2_res = client.post(
        f"/api/sessions/{session_id}/answer",
        json={"rating": 5, "time_spent_seconds": 1.5},
        headers=auth_headers,
    )
    assert ans2_res.status_code == 200
    assert ans2_res.json()["is_completed"] is True

    # Summary
    summary_res = client.get(f"/api/sessions/{session_id}/summary", headers=auth_headers)
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["status"] == "COMPLETED"
    assert summary["completed_cards"] == 2
    assert summary["accuracy_percentage"] == 100.0
