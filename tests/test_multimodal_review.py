import uuid
import pytest
from vocabmaster.db.connection import get_db

def test_multimodal_review_data_and_submission(client, auth_headers, temp_db_path):
    # 1. Create Deck
    deck_res = client.post(
        "/api/decks",
        headers=auth_headers,
        json={"name": "English Review Deck", "target_language": "en"}
    )
    assert deck_res.status_code == 200, deck_res.text
    deck_id = deck_res.json()["id"]

    # 2. Add an English vocabulary word with IPA, root word, examples
    vocab_res = client.post(
        "/api/vocab",
        headers=auth_headers,
        json={
            "deck_id": deck_id,
            "term": "perseverance",
            "language": "en",
            "definition": "sự kiên trì, bền chí",
            "ipa": "/ˌpɜː.sɪˈvɪə.rəns/",
            "part_of_speech": "noun",
            "root_word": "persevere",
            "examples": ["His perseverance led to great success."],
        }
    )
    assert vocab_res.status_code == 200, vocab_res.text
    v_data = vocab_res.json()
    assert v_data["term"] == "perseverance"
    assert v_data["ipa"] == "/ˌpɜː.sɪˈvɪə.rəns/"
    assert v_data["root_word"] == "persevere"

    # 3. Check vocabulary listing returns proper fields for practice fallback
    vocab_list_res = client.get("/api/vocab?language=en", headers=auth_headers)
    assert vocab_list_res.status_code == 200
    vocab_items = vocab_list_res.json()
    assert len(vocab_items) >= 1
    v_item = next(v for v in vocab_items if v["term"] == "perseverance")
    assert v_item["ipa"] == "/ˌpɜː.sɪˈvɪə.rəns/"
    assert v_item["root_word"] == "persevere"

    # 4. Set the card to due state in database to test due reviews endpoint
    with get_db(temp_db_path) as conn:
        conn.execute(
            "UPDATE srs_cards SET state = 'REVIEW', due_date = '2020-01-01T00:00:00Z' WHERE vocab_id = ?",
            (v_data["id"],)
        )
        conn.commit()

    due_res = client.get("/api/reviews/due?language=en", headers=auth_headers)
    assert due_res.status_code == 200
    cards = due_res.json()
    assert len(cards) >= 1
    found = next((c for c in cards if c["term"] == "perseverance"), None)
    assert found is not None
    assert found["ipa"] == "/ˌpɜː.sɪˈvɪə.rəns/"
    assert found["root_word"] == "persevere"
    assert "His perseverance led to great success." in found["examples"]

    # 5. Test practice submission for Mode 1 (Phiên âm -> Viết từ + Nghĩa)
    sub1 = client.post(
        "/api/practice/submit",
        headers=auth_headers,
        json={
            "practice_type": "multimodal_mode1",
            "vocab_id": v_data["id"],
            "prompt": "/ˌpɜː.sɪˈvɪə.rəns/ - sự kiên trì, bền chí",
            "user_text": "Từ: perseverance | Nghĩa: sự kiên trì",
            "model_answer": "perseverance - sự kiên trì, bền chí",
            "self_assessment_score": 5
        }
    )
    assert sub1.status_code == 200
    assert sub1.json()["practice_type"] == "multimodal_mode1"

    # 6. Test practice submission for Mode 2 (Từ vựng -> Đọc chuẩn + Nghĩa)
    sub2 = client.post(
        "/api/practice/submit",
        headers=auth_headers,
        json={
            "practice_type": "multimodal_mode2",
            "vocab_id": v_data["id"],
            "prompt": "perseverance - sự kiên trì, bền chí",
            "user_text": "Từ: perseverance | Đọc: Chuẩn | Nghĩa: sự kiên trì",
            "model_answer": "perseverance - sự kiên trì, bền chí",
            "self_assessment_score": 5
        }
    )
    assert sub2.status_code == 200
    assert sub2.json()["practice_type"] == "multimodal_mode2"

    # 7. Test practice submission for Mode 3 (Nghĩa TV -> Đọc từ + Viết từ)
    sub3 = client.post(
        "/api/practice/submit",
        headers=auth_headers,
        json={
            "practice_type": "multimodal_mode3",
            "vocab_id": v_data["id"],
            "prompt": "sự kiên trì, bền chí",
            "user_text": "Từ: perseverance | Đọc: Chuẩn",
            "model_answer": "perseverance - sự kiên trì, bền chí",
            "self_assessment_score": 5
        }
    )
    assert sub3.status_code == 200
    assert sub3.json()["practice_type"] == "multimodal_mode3"

    # 8. Verify practice history
    hist = client.get("/api/practice/history", headers=auth_headers)
    assert hist.status_code == 200
    hist_items = hist.json()
    assert len(hist_items) >= 3

    # 9. Verify UI contains the 3 review modes and sub-tab elements
    ui_res = client.get("/")
    assert ui_res.status_code == 200
    html = ui_res.text
    assert "btnSubTabReviewExercises" in html
    assert "btnSubTabReviewSRS" in html
    assert "reviewSubTabExercisesContainer" in html
    assert "reviewSubTabSRSContainer" in html
    assert "btnMultiMode1" in html
    assert "btnMultiMode2" in html
    assert "btnMultiMode3" in html
    assert "Kiểu 1: Phiên âm" in html
    assert "Kiểu 2: Từ vựng" in html
    assert "Kiểu 3: Nghĩa TV" in html
    assert "startQuickReviewSession" in html


def test_chinese_multimodal_review_workflow(client, auth_headers, temp_db_path):
    # 1. Create Chinese Deck
    zh_deck_res = client.post(
        "/api/decks",
        headers=auth_headers,
        json={"name": "Chinese Review Deck", "target_language": "zh"}
    )
    assert zh_deck_res.status_code == 200
    zh_deck_id = zh_deck_res.json()["id"]

    # 2. Add Chinese Vocab Item
    zh_vocab_res = client.post(
        "/api/vocab",
        headers=auth_headers,
        json={
            "deck_id": zh_deck_id,
            "term": "努力",
            "language": "zh",
            "definition": "nỗ lực, cố gắng",
            "part_of_speech": "verb",
            "language_specific_fields": {
                "pinyin": "nǔ lì",
                "hsk_level": "3"
            },
            "examples": ["我们要努力学习汉语。"]
        }
    )
    assert zh_vocab_res.status_code == 200
    zh_v = zh_vocab_res.json()
    assert zh_v["term"] == "努力"
    assert zh_v["language_specific_fields"]["pinyin"] == "nǔ lì"

    # 3. Set to due state in SRS
    with get_db(temp_db_path) as conn:
        conn.execute(
            "UPDATE srs_cards SET state = 'REVIEW', due_date = '2020-01-01T00:00:00Z' WHERE vocab_id = ?",
            (zh_v["id"],)
        )
        conn.commit()

    # 4. Check due reviews for Chinese
    due_res = client.get("/api/reviews/due?language=zh", headers=auth_headers)
    assert due_res.status_code == 200
    cards = due_res.json()
    assert len(cards) >= 1
    c = next(card for card in cards if card["term"] == "努力")
    assert c["language_specific_fields"]["pinyin"] == "nǔ lì"
    assert c["definition"] == "nỗ lực, cố gắng"
    assert "我们要努力学习汉语。" in c["examples"]

    # 5. Practice submission in Chinese mode
    sub = client.post(
        "/api/practice/submit",
        headers=auth_headers,
        json={
            "practice_type": "multimodal_mode1",
            "vocab_id": zh_v["id"],
            "prompt": "nǔ lì - nỗ lực, cố gắng",
            "user_text": "Từ: 努力 | Nghĩa: cố gắng",
            "model_answer": "努力 - nỗ lực, cố gắng",
            "self_assessment_score": 5
        }
    )
    assert sub.status_code == 200
    assert sub.json()["practice_type"] == "multimodal_mode1"


def test_deck_rename_and_seed_template(client, auth_headers):
    # 1. Seed template deck
    seed_res = client.post("/api/decks/seed-template?language=en", headers=auth_headers)
    assert seed_res.status_code == 200
    deck = seed_res.json()
    deck_id = deck["id"]
    assert "Bộ Từ Vựng Mẫu" in deck["name"]

    # 2. Rename deck
    new_name = "Bộ Từ Vựng Cốt Lõi Của Tôi"
    new_desc = "Tên bộ từ vựng đã được đổi mới thành công"
    update_res = client.put(
        f"/api/decks/{deck_id}",
        headers=auth_headers,
        json={"name": new_name, "description": new_desc}
    )
    assert update_res.status_code == 200
    updated_deck = update_res.json()
    assert updated_deck["name"] == new_name
    assert updated_deck["description"] == new_desc

    # 3. Verify in deck listing
    list_res = client.get("/api/decks?language=en", headers=auth_headers)
    assert list_res.status_code == 200
    decks = list_res.json()
    renamed = next(d for d in decks if d["id"] == deck_id)
    assert renamed["name"] == new_name
    assert renamed["stats"]["total_cards"] >= 5

    # 4. Test reset-all endpoint
    reset_res = client.post("/api/decks/reset-all?language=en", headers=auth_headers)
    assert reset_res.status_code == 200
    reset_data = reset_res.json()
    assert reset_data["status"] == "ok"
    assert "Bộ Từ Vựng Mẫu" in reset_data["deck"]["name"]

