"""Configuration settings for VocabMaster."""

import os
from pathlib import Path
from pydantic import BaseModel

DEFAULT_DATA_DIR = Path(os.environ.get("VOCABMASTER_DATA_DIR", Path.home() / ".vocabmaster"))
DEFAULT_DB_PATH = Path(os.environ.get("VOCABMASTER_DB_PATH", DEFAULT_DATA_DIR / "vocabmaster.db"))


class Settings(BaseModel):
    data_dir: Path = DEFAULT_DATA_DIR
    db_path: Path = DEFAULT_DB_PATH
    secret_key: str = os.environ.get("VOCABMASTER_SECRET_KEY", "vocabmaster-secret-key-change-in-production-1234567890")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    default_new_cards_per_day: int = 20
    default_reviews_per_day: int = 100
    min_ease_factor: float = 1.3
    default_ease_factor: float = 2.5


settings = Settings()
