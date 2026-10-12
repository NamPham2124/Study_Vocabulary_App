"""Interactive and automated Command-Line Interface (CLI) for VocabMaster."""

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Optional

from vocabmaster.config import settings
from vocabmaster.db.connection import get_db
from vocabmaster.db.migrations import init_db
from vocabmaster.db import repository
from vocabmaster.auth.security import hash_password, verify_password
from vocabmaster.auth.tokens import create_access_token, decode_access_token
from vocabmaster.models.base import Language
from vocabmaster.importer.processor import import_vocabulary_file
from vocabmaster.session import manager as session_manager


TOKEN_FILE = settings.data_dir / ".session_token"


def save_token(token: str) -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(token.strip())


def load_token() -> Optional[str]:
    if not TOKEN_FILE.exists():
        return None
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def get_current_user_from_cli():
    token = load_token()
    if not token:
        print("Error: Not logged in. Please run 'vocabmaster login' first.")
        sys.exit(1)
    try:
        payload = decode_access_token(token)
    except Exception as e:
        print(f"Error: Session expired or invalid: {e}. Please log in again.")
        sys.exit(1)

    user_id = payload.get("sub")
    with get_db() as conn:
        user = repository.get_user_by_id(conn, user_id)
        if not user:
            print("Error: User record not found.")
            sys.exit(1)
        return user


def cmd_register(args):
    init_db()
    with get_db() as conn:
        if repository.get_user_by_email(conn, args.email):
            print(f"Error: Email {args.email} is already registered.")
            sys.exit(1)
        if repository.get_user_by_username(conn, args.username):
            print(f"Error: Username {args.username} is already taken.")
            sys.exit(1)

        user_id = str(uuid.uuid4())
        pwd_hash, salt = hash_password(args.password)
        user = repository.create_user(
            conn, user_id, args.username, args.email, pwd_hash, salt
        )
        token = create_access_token({"sub": user["id"], "username": user["username"]})
        save_token(token)
        print(f"Success: Registered user '{args.username}' (ID: {user['id']}).")
        print(f"Logged in automatically.")


def cmd_login(args):
    init_db()
    with get_db() as conn:
        user = repository.get_user_by_email(conn, args.email)
        if not user or not verify_password(args.password, user["password_hash"], user["salt"]):
            print("Error: Invalid email or password.")
            sys.exit(1)

        token = create_access_token({"sub": user["id"], "username": user["username"]})
        save_token(token)
        print(f"Success: Logged in as '{user['username']}'.")


def cmd_deck_create(args):
    user = get_current_user_from_cli()
    deck_id = str(uuid.uuid4())
    with get_db() as conn:
        deck = repository.create_deck(
            conn,
            deck_id=deck_id,
            user_id=user["id"],
            name=args.name,
            description=args.description or "",
            target_language=args.lang or "en",
        )
        print(f"Success: Deck '{deck['name']}' created (ID: {deck['id']}, Language: {deck['target_language']}).")


def cmd_deck_list(args):
    user = get_current_user_from_cli()
    with get_db() as conn:
        decks = repository.list_decks_for_user(conn, user["id"])
        if not decks:
            print("No decks found. Create one with 'vocabmaster deck-create'.")
            return

        print(f"{'ID':<38} {'NAME':<25} {'LANG':<6} {'TOTAL':<7} {'DUE':<6} {'NEW':<6}")
        print("-" * 90)
        for d in decks:
            print(
                f"{d['id']:<38} {d['name'][:24]:<25} {d['target_language']:<6} "
                f"{d['total_cards']:<7} {d['due_reviews'] or 0:<6} {d['new_cards'] or 0:<6}"
            )


def cmd_import(args):
    user = get_current_user_from_cli()
    path = Path(args.file)
    if not path.exists():
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)

    file_bytes = path.read_bytes()
    with get_db() as conn:
        res = import_vocabulary_file(
            conn=conn,
            user_id=user["id"],
            deck_id=args.deck,
            file_bytes=file_bytes,
            filename=path.name,
            dedup_strategy=args.dedup,
        )
        print(f"--- Import Summary ({res.filename}) ---")
        print(f"Total Rows:     {res.total_rows}")
        print(f"Imported Items: {res.imported_count}")
        print(f"Skipped Items:  {res.skipped_count}")
        print(f"Errors:         {res.error_count}")
        if res.errors:
            print("Sample Errors:")
            for err in res.errors[:5]:
                print(f"  Row {err.get('row', '?')}: {err.get('error', 'Unknown error')}")


def cmd_study(args):
    user = get_current_user_from_cli()
    with get_db() as conn:
        session_info = session_manager.start_or_resume_session(
            conn,
            user_id=user["id"],
            deck_id=args.deck,
            new_card_limit=args.new_limit,
            review_limit=args.review_limit,
        )

    session = session_info["session"]
    if session_info["recovered"]:
        print(f"Resuming active session: {session['title']} (Card {session['current_index'] + 1} of {session['total_cards']})")
    else:
        print(f"Started new session: {session['title']} ({session['total_cards']} cards in queue)")

    if session["status"] == "COMPLETED" or not session_info.get("current_card"):
        print("No cards due or queue already completed! Great job!")
        return

    session_id = session["id"]

    while True:
        with get_db() as conn:
            card = session_manager.get_current_card(conn, session_id, user["id"])

        if not card:
            with get_db() as conn:
                summary = session_manager.get_session_summary(conn, session_id, user["id"])
            print("\n🎉 Session Completed!")
            print(f"Cards Studied: {summary['completed_cards']}")
            print(f"Accuracy:      {summary['accuracy_percentage']}%")
            return

        print("\n" + "=" * 60)
        print(f"Card {card['current_index'] + 1}/{card['total_cards']} [{card['language'].upper()}] - State: {card['state']}")
        print(f"Term: {card['term']}")
        if card.get("ipa"):
            print(f"IPA:  {card['ipa']}")

        # Language specific fields
        lang_fields = card.get("language_specific_fields", {})
        if lang_fields:
            if "reading" in lang_fields:
                print(f"Reading: {lang_fields['reading']}")
            if "article" in lang_fields:
                print(f"Article: {lang_fields['article']}")
            if "gender" in lang_fields:
                print(f"Gender:  {lang_fields['gender']}")

        input("\n[Press ENTER to reveal definition]")
        print(f"\nDefinition: {card['definition']}")
        if card.get("part_of_speech"):
            print(f"Part of Speech: {card['part_of_speech']}")
        if card.get("examples"):
            print("Examples:")
            for ex in card["examples"]:
                print(f"  • {ex}")

        print("\nRate recall (0-5) or 'p' to pause, 'q' to quit:")
        print("0: Blackout | 1: Fail | 2: Hard struggle | 3: Difficult pass | 4: Good | 5: Perfect")

        while True:
            choice = input("Rating [0-5, p, q]: ").strip().lower()
            if choice in ("p", "pause"):
                with get_db() as conn:
                    session_manager.pause_session(conn, session_id, user["id"])
                print("Session paused. You can resume later with 'vocabmaster resume'.")
                return
            elif choice in ("q", "quit"):
                print("Session suspended in place. Progress is safely saved.")
                return
            elif choice.isdigit() and 0 <= int(choice) <= 5:
                rating = int(choice)
                with get_db() as conn:
                    res = session_manager.submit_card_answer(
                        conn=conn,
                        session_id=session_id,
                        user_id=user["id"],
                        rating=rating,
                    )
                break
            else:
                print("Invalid input. Please enter 0-5, 'p' to pause, or 'q' to quit.")


def cmd_resume(args):
    cmd_study(args)


def cmd_stats(args):
    user = get_current_user_from_cli()
    with get_db() as conn:
        counts = repository.get_due_and_new_counts(conn, user["id"])
        decks = repository.list_decks_for_user(conn, user["id"])
        total_cards = sum(d.get("total_cards", 0) for d in decks)

        print("\n--- VocabMaster Statistics ---")
        print(f"Total Decks:       {len(decks)}")
        print(f"Total Flashcards:  {total_cards}")
        print(f"Due Reviews Today: {counts['due_count']}")
        print(f"New Cards Ready:   {counts['new_count']}")


def cli_entrypoint():
    parser = argparse.ArgumentParser(
        prog="vocabmaster",
        description="VocabMaster CLI - Spaced Repetition Vocabulary Learning System",
    )
    subparsers = parser.add_subparsers(dest="command")

    # init-db
    subparsers.add_parser("init-db", help="Initialize the database schema")

    # register
    reg_parser = subparsers.add_parser("register", help="Register a new user account")
    reg_parser.add_argument("--username", required=True, help="Username")
    reg_parser.add_argument("--email", required=True, help="Email address")
    reg_parser.add_argument("--password", required=True, help="Password")

    # login
    login_parser = subparsers.add_parser("login", help="Log in to account")
    login_parser.add_argument("--email", required=True, help="Email address")
    login_parser.add_argument("--password", required=True, help="Password")

    # deck-create
    dc_parser = subparsers.add_parser("deck-create", help="Create a vocabulary deck")
    dc_parser.add_argument("--name", required=True, help="Deck name")
    dc_parser.add_argument("--description", default="", help="Deck description")
    dc_parser.add_argument("--lang", default="en", help="Target language (en, ja, de, es, fr, vi)")

    # deck-list
    subparsers.add_parser("deck-list", help="List all decks with statistics")

    # import
    imp_parser = subparsers.add_parser("import", help="Import vocabulary from CSV or XLSX")
    imp_parser.add_argument("--deck", required=True, help="Target deck ID")
    imp_parser.add_argument("--file", required=True, help="Path to CSV or XLSX file")
    imp_parser.add_argument(
        "--dedup",
        choices=["skip", "overwrite", "allow_duplicates"],
        default="skip",
        help="Deduplication strategy",
    )

    # study
    study_parser = subparsers.add_parser("study", help="Start or resume a study session")
    study_parser.add_argument("--deck", default=None, help="Target deck ID (default: all)")
    study_parser.add_argument("--new-limit", type=int, default=None, help="Max new cards")
    study_parser.add_argument("--review-limit", type=int, default=None, help="Max reviews")

    # resume
    res_parser = subparsers.add_parser("resume", help="Resume an active/paused session")
    res_parser.add_argument("--deck", default=None, help="Target deck ID")
    res_parser.add_argument("--new-limit", type=int, default=None)
    res_parser.add_argument("--review-limit", type=int, default=None)

    # stats
    subparsers.add_parser("stats", help="Display overall learning stats")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "init-db":
        init_db()
        print("Database schema successfully initialized.")
    elif args.command == "register":
        cmd_register(args)
    elif args.command == "login":
        cmd_login(args)
    elif args.command == "deck-create":
        cmd_deck_create(args)
    elif args.command == "deck-list":
        cmd_deck_list(args)
    elif args.command == "import":
        cmd_import(args)
    elif args.command == "study":
        cmd_study(args)
    elif args.command == "resume":
        cmd_resume(args)
    elif args.command == "stats":
        cmd_stats(args)


if __name__ == "__main__":
    cli_entrypoint()
