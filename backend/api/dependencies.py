"""FastAPI dependencies for database connections and shared logic."""
from __future__ import annotations

import sqlite3
from typing import Iterator

from backend.db import DbConfig, db_conn


def get_db_conn() -> Iterator[sqlite3.Connection]:
    """
    Dependency that provides a database connection for a request.
    Automatically commits on success, rolls back on error.
    """
    try:
        cfg = DbConfig.from_env()
        with db_conn(cfg) as conn:
            yield conn
    except Exception as e:
        import traceback
        print(f"ERROR in get_db_conn: {e}")
        traceback.print_exc()
        raise


