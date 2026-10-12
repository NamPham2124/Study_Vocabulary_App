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


def test_api_manual_vocab_creation_and_language_isolation(client, auth_headers):
    # 1. Create English Deck
    en_deck_res = client.post(
        "/api/decks",
        json={"name": "English Core Vocabulary", "description": "English essentials", "target_language": "en"},
        headers=auth_headers,
    )
    assert en_deck_res.status_code == 200
    en_deck_id = en_deck_res.json()["id"]

    # 2. Create Chinese Deck
    zh_deck_res = client.post(
        "/api/decks",
        json={"name": "HSK 1 Mandarin", "description": "Mandarin basics", "target_language": "zh"},
        headers=auth_headers,
    )
    assert zh_deck_res.status_code == 200
    zh_deck_id = zh_deck_res.json()["id"]

    # 3. Manually Add English Vocabulary via POST /api/vocab
    en_vocab_payload = {
        "deck_id": en_deck_id,
        "term": "resilient",
        "definition": "kiên cường, có khả năng phục hồi nhanh",
        "language": "en",
        "ipa": "/rɪˈzɪl.jənt/",
        "part_of_speech": "adjective",
        "examples": ["He is a resilient competitor who never gives up."],
        "mnemonics": "re (lại) + silire (bật nhảy) -> nảy lại sau vấp ngã = kiên cường",
        "root_word": "",
    }
    en_res = client.post("/api/vocab", json=en_vocab_payload, headers=auth_headers)
    assert en_res.status_code == 200
    en_vocab = en_res.json()
    assert en_vocab["term"] == "resilient"
    assert en_vocab["ipa"] == "/rɪˈzɪl.jənt/"
    assert en_vocab["part_of_speech"] == "adjective"
    assert en_vocab["language"] == "en"

    # 4. Manually Add Chinese Vocabulary via POST /api/vocab
    zh_vocab_payload = {
        "deck_id": zh_deck_id,
        "term": "苹果",
        "definition": "quả táo",
        "language": "zh",
        "ipa": "píngguǒ",
        "part_of_speech": "noun",
        "examples": ["我喜欢吃苹果。"],
        "language_specific_fields": {"pinyin": "píngguǒ", "tones": [2, 3]},
    }
    zh_res = client.post("/api/vocab", json=zh_vocab_payload, headers=auth_headers)
    assert zh_res.status_code == 200
    zh_vocab = zh_res.json()
    assert zh_vocab["term"] == "苹果"
    assert zh_vocab["language"] == "zh"

    # 5. Strict Language Isolation Verification
    # English query should return ONLY English words
    en_list = client.get("/api/vocab?language=en", headers=auth_headers).json()
    en_terms = [item["term"] for item in en_list]
    assert "resilient" in en_terms
    assert "苹果" not in en_terms

    # Chinese query should return ONLY Chinese words
    zh_list = client.get("/api/vocab?language=zh", headers=auth_headers).json()
    zh_terms = [item["term"] for item in zh_list]
    assert "苹果" in zh_terms
    assert "resilient" not in zh_terms

    # 6. Verify Due Reviews endpoint
    due_res = client.get("/api/reviews/due?language=en", headers=auth_headers)
    assert due_res.status_code == 200
    assert isinstance(due_res.json(), list)

    # 7. Verify Practice Submit & Practice History endpoint
    prac_res = client.post(
        "/api/practice/submit",
        json={
            "vocab_id": en_vocab["id"],
            "practice_type": "writing",
            "prompt": "Write a sentence with 'resilient'",
            "user_text": "She showed a resilient attitude during difficult times.",
            "model_answer": "He is resilient.",
            "self_assessment_score": 5,
        },
        headers=auth_headers,
    )
    assert prac_res.status_code == 200

    hist_res = client.get("/api/practice/history", headers=auth_headers)
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) >= 1
    assert any(h["user_text"] == "She showed a resilient attitude during difficult times." for h in history)

    # 8. Verify Streak endpoint
    streak_res = client.get("/api/progress/streak?language=en", headers=auth_headers)
    assert streak_res.status_code == 200
    streak_data = streak_res.json()
    assert "current_streak" in streak_data
    assert "longest_streak" in streak_data

