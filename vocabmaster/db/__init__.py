"""Database module for VocabMaster."""

from vocabmaster.db.connection import get_db, DatabaseManager
from vocabmaster.db.migrations import init_db

__all__ = ["get_db", "DatabaseManager", "init_db"]
