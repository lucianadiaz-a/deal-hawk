from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Iterable

from backend.connectors.fixtures import get_fixture_price_cents


@dataclass(frozen=True)
class IngestResult:
    snapshots_written: int


def iter_active_listing_ids(conn: sqlite3.Connection) -> Iterable[int]:
    rows = conn.execute("SELECT id FROM listings WHERE active = 1 ORDER BY id").fetchall()
    for r in rows:
        yield int(r["id"])


def run_ingest_cycle(conn: sqlite3.Connection) -> IngestResult:
    written = 0
    for listing_id in iter_active_listing_ids(conn):
        price_cents = get_fixture_price_cents(conn, listing_id)
        currency = conn.execute("SELECT currency FROM listings WHERE id = ?", (listing_id,)).fetchone()
        cur = "USD" if currency is None else str(currency["currency"])

        conn.execute(
            """
            INSERT INTO price_snapshots(listing_id, price_cents, currency, captured_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (listing_id, price_cents, cur),
        )
        written += 1

    return IngestResult(snapshots_written=written)
