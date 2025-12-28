from __future__ import annotations

import argparse
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional


DEFAULT_DB_PATH = "data/deal_hawk.sqlite3"


@dataclass(frozen=True)
class DbConfig:
    path: Path

    @staticmethod
    def from_env() -> "DbConfig":
        raw = os.getenv("DEAL_HAWK_DB_PATH", DEFAULT_DB_PATH)
        return DbConfig(path=Path(raw))


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path.as_posix())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


@contextmanager
def db_conn(cfg: Optional[DbConfig] = None) -> Iterator[sqlite3.Connection]:
    cfg = cfg or DbConfig.from_env()
    conn = _connect(cfg.path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_schema(conn: sqlite3.Connection) -> None:
    # Minimal schema for the POC vertical slice.
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT,
            model TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS retailers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            retailer_id INTEGER NOT NULL REFERENCES retailers(id) ON DELETE CASCADE,
            url TEXT NOT NULL,
            external_sku TEXT,
            currency TEXT NOT NULL DEFAULT 'USD',
            active INTEGER NOT NULL DEFAULT 1,

            -- fixture params (POC connector)
            fixture_base_price_cents INTEGER NOT NULL DEFAULT 9999,
            fixture_step_cents INTEGER NOT NULL DEFAULT 0,
            fixture_period INTEGER NOT NULL DEFAULT 5,

            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(product_id, retailer_id)
        );

        CREATE TABLE IF NOT EXISTS price_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
            price_cents INTEGER NOT NULL,
            currency TEXT NOT NULL DEFAULT 'USD',
            captured_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_price_snapshots_listing_time
        ON price_snapshots(listing_id, captured_at);

        CREATE TABLE IF NOT EXISTS alert_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
            rule_name TEXT NOT NULL,
            threshold_pct REAL NOT NULL,
            prev_price_cents INTEGER NOT NULL,
            new_price_cents INTEGER NOT NULL,
            triggered_at TEXT NOT NULL DEFAULT (datetime('now')),
            message_preview TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_alert_events_listing_time
        ON alert_events(listing_id, triggered_at);
        """
    )

    # Handle unique index creation with duplicate migration
    # Check if index already exists
    index_rows = conn.execute("PRAGMA index_list('products')").fetchall()
    index_exists = any(row[1] == "idx_products_identity" for row in index_rows)

    if not index_exists:
        # Check for duplicates before creating unique index
        duplicate_rows = conn.execute(
            """
            SELECT name, brand, model, COUNT(*) as cnt, MIN(id) as keep_id
            FROM products
            GROUP BY name, brand, model
            HAVING COUNT(*) > 1
            """
        ).fetchall()

        if duplicate_rows:
            # Deduplicate: keep the first (lowest ID) of each duplicate group
            # Update foreign keys in listings to point to the kept product
            for dup in duplicate_rows:
                keep_id = dup[4]  # MIN(id)
                name, brand, model = dup[0], dup[1], dup[2]

                # Find all duplicate product IDs (except the one we're keeping)
                dup_ids = conn.execute(
                    """
                    SELECT id FROM products
                    WHERE name = ? AND
                          COALESCE(brand, '') = COALESCE(?, '') AND
                          COALESCE(model, '') = COALESCE(?, '')
                    AND id != ?
                    """,
                    (name, brand, model, keep_id),
                ).fetchall()

                # Update listings to point to the kept product
                for dup_id_row in dup_ids:
                    dup_id = dup_id_row[0]
                    # Get listings that reference the duplicate product
                    dup_listings = conn.execute(
                        """
                        SELECT id, retailer_id FROM listings
                        WHERE product_id = ?
                        """,
                        (dup_id,),
                    ).fetchall()

                    for listing_row in dup_listings:
                        listing_id, retailer_id = listing_row[0], listing_row[1]
                        # Check if a listing already exists for keep_id + retailer_id
                        existing = conn.execute(
                            """
                            SELECT id FROM listings
                            WHERE product_id = ? AND retailer_id = ?
                            """,
                            (keep_id, retailer_id),
                        ).fetchone()

                        if existing:
                            # Listing already exists for kept product + retailer
                            # Merge price_snapshots and alert_events from duplicate to existing
                            existing_id = existing[0]
                            # Move price_snapshots
                            conn.execute(
                                """
                                UPDATE price_snapshots
                                SET listing_id = ?
                                WHERE listing_id = ?
                                """,
                                (existing_id, listing_id),
                            )
                            # Move alert_events
                            conn.execute(
                                """
                                UPDATE alert_events
                                SET listing_id = ?
                                WHERE listing_id = ?
                                """,
                                (existing_id, listing_id),
                            )
                            # Now safe to delete the duplicate listing
                            conn.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
                        else:
                            # No conflict, update the listing to point to kept product
                            conn.execute(
                                """
                                UPDATE listings
                                SET product_id = ?
                                WHERE id = ?
                                """,
                                (keep_id, listing_id),
                            )

                    # Delete the duplicate product (CASCADE will handle any remaining related data)
                    conn.execute("DELETE FROM products WHERE id = ?", (dup_id,))

        # Now create the unique index
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_products_identity
            ON products(name || COALESCE('|' || brand, '') || COALESCE('|' || model, ''))
            """
        )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m backend.db")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="Initialize SQLite schema")

    args = parser.parse_args(argv)
    if args.cmd == "init":
        cfg = DbConfig.from_env()
        with db_conn(cfg) as conn:
            init_schema(conn)
        print(f"Initialized DB schema at {cfg.path}")
        return 0

    raise RuntimeError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
