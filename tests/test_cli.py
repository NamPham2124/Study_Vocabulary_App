"""Tests for VocabMaster CLI commands."""

import subprocess
import sys
import pytest


def test_cli_help():
    res = subprocess.run(
        [sys.executable, "-m", "vocabmaster.cli.main", "--help"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "VocabMaster CLI" in res.stdout
    assert "deck-create" in res.stdout
    assert "study" in res.stdout


def test_cli_init_db(tmp_path, monkeypatch):
    test_db = tmp_path / "cli_test.db"
    monkeypatch.setenv("VOCABMASTER_DB_PATH", str(test_db))
    monkeypatch.setenv("VOCABMASTER_DATA_DIR", str(tmp_path))

    env = {"VOCABMASTER_DB_PATH": str(test_db), "VOCABMASTER_DATA_DIR": str(tmp_path)}

    # 1. Init DB
    res = subprocess.run(
        [sys.executable, "-m", "vocabmaster.cli.main", "init-db"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode == 0
    assert "initialized" in res.stdout.lower()

    # 2. Register
    reg = subprocess.run(
        [
            sys.executable,
            "-m",
            "vocabmaster.cli.main",
            "register",
            "--username",
            "clitester",
            "--email",
            "clitester@example.com",
            "--password",
            "password123",
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert reg.returncode == 0
    assert "Registered user" in reg.stdout

    # 3. Create Deck
    deck_cmd = subprocess.run(
        [
            sys.executable,
            "-m",
            "vocabmaster.cli.main",
            "deck-create",
            "--name",
            "CLI Vocabulary Deck",
            "--lang",
            "en",
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert deck_cmd.returncode == 0
    assert "Deck 'CLI Vocabulary Deck' created" in deck_cmd.stdout

    # Extract deck ID
    # Output line: Success: Deck 'CLI Vocabulary Deck' created (ID: <deck_id>, Language: en).
    deck_id = deck_cmd.stdout.split("ID: ")[1].split(",")[0].strip()

    # 4. Import CSV file
    csv_file = tmp_path / "cli_words.csv"
    csv_file.write_text("term,definition\nvelocity,speed in a given direction\nmomentum,mass times velocity\n")

    imp_cmd = subprocess.run(
        [
            sys.executable,
            "-m",
            "vocabmaster.cli.main",
            "import",
            "--deck",
            deck_id,
            "--file",
            str(csv_file),
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert imp_cmd.returncode == 0
    assert "Imported Items: 2" in imp_cmd.stdout

    # 5. List Decks
    list_cmd = subprocess.run(
        [sys.executable, "-m", "vocabmaster.cli.main", "deck-list"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert list_cmd.returncode == 0
    assert "CLI Vocabulary Deck" in list_cmd.stdout

    # 6. Stats
    stats_cmd = subprocess.run(
        [sys.executable, "-m", "vocabmaster.cli.main", "stats"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert stats_cmd.returncode == 0
    assert "Total Flashcards:  2" in stats_cmd.stdout
