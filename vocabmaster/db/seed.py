"""Seed demo data for quick interactive testing."""

import uuid
from vocabmaster.db.connection import get_db
from vocabmaster.db.migrations import init_db
from vocabmaster.db import repository
from vocabmaster.auth.security import hash_password
from vocabmaster.importer.processor import import_vocabulary_file


def seed_demo_data():
    init_db()
    with get_db() as conn:
        # Check if user already exists
        demo_user = repository.get_user_by_email(conn, "learner@example.com")
        if not demo_user:
            user_id = str(uuid.uuid4())
            pwd_hash, salt = hash_password("Password123!")
            demo_user = repository.create_user(
                conn, user_id, "learner", "learner@example.com", pwd_hash, salt
            )

        # 1. English Deck
        decks = repository.list_decks_for_user(conn, demo_user["id"])
        deck_names = {d["name"] for d in decks}

        if "English Tech & Advanced" not in deck_names:
            en_deck = repository.create_deck(
                conn,
                deck_id=str(uuid.uuid4()),
                user_id=demo_user["id"],
                name="English Tech & Advanced",
                description="Essential computer science and engineering vocabulary",
                target_language="en",
            )
            csv_en = (
                "term,definition,ipa,part_of_speech,examples,tags\n"
                "concurrency,the ability of different parts of a program to be executed out-of-order,/kənˈkʌr.ən.si/,noun,Modern databases rely on concurrency control.,system;programming\n"
                "resilience,the capacity to withstand and recover quickly from difficulties,/rɪˈzɪl.jəns/,noun,The distributed cluster exhibited great resilience during network partitioning.,psychology;engineering\n"
                "epiphany,an illuminating discovery or sudden realization,/ɪˈpɪf.ən.i/,noun,She experienced an epiphany while refactoring the query optimizer.,cognitive\n"
                "heuristic,a practical approach to problem-solving that is not guaranteed to be optimal,/hjʊəˈrɪs.tɪk/,adjective,A greedy heuristic was used for the graph traversal.,algorithm\n"
                "serendipity,the occurrence of finding valuable things by chance,/ˌser.ənˈdɪp.ə.ti/,noun,The discovery of the cache bug was pure serendipity.,mindset\n"
            ).encode("utf-8")
            import_vocabulary_file(conn, demo_user["id"], en_deck["id"], csv_en, "english_tech.csv")

        # 2. Japanese Deck
        if "Japanese JLPT N5-N4" not in deck_names:
            ja_deck = repository.create_deck(
                conn,
                deck_id=str(uuid.uuid4()),
                user_id=demo_user["id"],
                name="Japanese JLPT N5-N4",
                description="Core everyday words with kanji, furigana readings, and JLPT levels",
                target_language="ja",
            )
            csv_ja = (
                "term,definition,reading,jlpt_level,part_of_speech,examples\n"
                "食べる,to eat,たべる,N5,verb,毎日朝ご飯を食べます。\n"
                "飲む,to drink,のむ,N5,verb,水をたくさん飲みます。\n"
                "勉強,study / diligence,べんきょう,N5,noun,毎日日本語を勉強しています。\n"
                "時間,time / hours,じかん,N5,noun,時間はあっという間に過ぎる。\n"
                "約束,promise / appointment,やくそく,N4,noun,友達と約束があります。\n"
            ).encode("utf-8")
            import_vocabulary_file(conn, demo_user["id"], ja_deck["id"], csv_ja, "japanese_jlpt.csv")

        # 3. German Deck
        if "German B1 Core" not in deck_names:
            de_deck = repository.create_deck(
                conn,
                deck_id=str(uuid.uuid4()),
                user_id=demo_user["id"],
                name="German B1 Core",
                description="German nouns with articles (der/die/das), plurals, and CEFR levels",
                target_language="de",
            )
            csv_de = (
                "term,definition,article,gender,plural_form,cefr_level\n"
                "Herausforderung,challenge,die,feminine,die Herausforderungen,B1\n"
                "Erfolg,success,der,masculine,die Erfolge,B1\n"
                "Ergebnis,result,das,neuter,die Ergebnisse,A2\n"
                "Entscheidung,decision,die,feminine,die Entscheidungen,B1\n"
            ).encode("utf-8")
            import_vocabulary_file(conn, demo_user["id"], de_deck["id"], csv_de, "german_b1.csv")


if __name__ == "__main__":
    seed_demo_data()
    print("Demo data seeded successfully.")
