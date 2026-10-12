"""Database connection manager for SQLite and PostgreSQL (Supabase)."""

import os
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, List, Optional, Union
from datetime import datetime, date
from urllib.parse import urlparse

from vocabmaster.config import settings


class RowWrapper(dict):
    """Row wrapper that supports both column-name access (row['term']) and integer indexing (row[0])."""

    def __init__(self, cols: List[str], vals: List[Any]):
        converted_vals = [
            v.isoformat() if isinstance(v, (datetime, date)) else v
            for v in vals
        ]
        super().__init__(zip(cols, converted_vals))
        self._vals = tuple(converted_vals)

    def __getitem__(self, key: Union[str, int]) -> Any:
        if isinstance(key, int):
            return self._vals[key]
        return super().__getitem__(key)


class PgCursorWrapper:
    """Cursor wrapper for PostgreSQL DBAPI."""

    def __init__(self, cursor: Any):
        self._cursor = cursor

    @property
    def description(self) -> Any:
        return self._cursor.description

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    def fetchone(self) -> Optional[RowWrapper]:
        row = self._cursor.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in self._cursor.description]
        return RowWrapper(cols, list(row))

    def fetchall(self) -> List[RowWrapper]:
        rows = self._cursor.fetchall()
        if not rows:
            return []
        cols = [d[0] for d in self._cursor.description]
        return [RowWrapper(cols, list(r)) for r in rows]


class PgConnWrapper:
    """Connection wrapper for PostgreSQL conforming to sqlite3 connection interface."""

    def __init__(self, raw_conn: Any):
        self._conn = raw_conn
        self.in_transaction = False

    def execute(self, sql: str, params: Optional[Union[tuple, list]] = None) -> PgCursorWrapper:
        clean_sql = sql.replace("INSERT OR IGNORE INTO", "INSERT INTO")
        if (
            clean_sql.strip().upper().startswith("INSERT")
            and "path_decks" in clean_sql
            and "ON CONFLICT" not in clean_sql
        ):
            clean_sql += " ON CONFLICT DO NOTHING"
        clean_sql = clean_sql.replace("?", "%s")

        cur = self._conn.cursor()
        try:
            if params is not None:
                cur.execute(clean_sql, params)
            else:
                cur.execute(clean_sql)
            return PgCursorWrapper(cur)
        except Exception as e:
            err_type = type(e).__name__
            if "IntegrityError" in err_type:
                raise sqlite3.IntegrityError(str(e)) from e
            raise

    def cursor(self) -> "PgConnWrapper":
        return self

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()

    def executescript(self, script: str) -> None:
        statements = [stmt.strip() for stmt in script.split(";") if stmt.strip()]
        for stmt in statements:
            self.execute(stmt)


class DatabaseManager:
    """Manages database connections (SQLite or Supabase PostgreSQL)."""

    def __init__(
        self,
        db_path: Optional[Union[str, Path]] = None,
        database_url: Optional[str] = None,
    ):
        self.is_postgres = False
        self.database_url = database_url or settings.database_url

        if db_path is not None:
            self.db_path = Path(db_path) if isinstance(db_path, str) else db_path
            if self.db_path != Path(":memory:"):
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
        elif self.database_url and (
            self.database_url.startswith("postgresql://")
            or self.database_url.startswith("postgres://")
        ):
            self.is_postgres = True
            self.db_path = None
        else:
            self.db_path = settings.db_path
            if self.db_path != Path(":memory:"):
                self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> Any:
        if self.is_postgres:
            return self._get_pg_connection()
        return self._get_sqlite_connection()

    def _get_sqlite_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=30.0,
            check_same_thread=False,
            isolation_level=None,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        if str(self.db_path) != ":memory:":
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _get_pg_connection(self) -> PgConnWrapper:
        parsed = urlparse(self.database_url)
        username = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 5432
        database = parsed.path.lstrip("/")

        try:
            import pg8000.dbapi

            raw_conn = pg8000.dbapi.connect(
                user=username,
                password=password,
                host=host,
                port=port,
                database=database,
            )
            raw_conn.autocommit = False
            return PgConnWrapper(raw_conn)
        except ImportError:
            import psycopg2

            raw_conn = psycopg2.connect(
                dbname=database,
                user=username,
                password=password,
                host=host,
                port=port,
            )
            return PgConnWrapper(raw_conn)

    @contextmanager
    def transaction(
        self, conn: Optional[Any] = None
    ) -> Generator[Any, None, None]:
        owns_conn = False
        if conn is None:
            conn = self.get_connection()
            owns_conn = True

        try:
            if not getattr(conn, "in_transaction", False):
                if not self.is_postgres:
                    conn.execute("BEGIN IMMEDIATE;")
            yield conn
            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            if owns_conn:
                conn.close()


@contextmanager
def get_db(
    db_path: Optional[Union[str, Path]] = None,
    database_url: Optional[str] = None,
) -> Generator[Any, None, None]:
    """Yield a managed connection inside an atomic transaction."""
    manager = DatabaseManager(db_path=db_path, database_url=database_url)
    with manager.transaction() as conn:
        yield conn
