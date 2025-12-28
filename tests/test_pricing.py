from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

# Add project root to Python path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend.db import init_schema
from backend.services.pricing import get_listing_price_summary


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _seed_minimal(conn: sqlite3.Connection) -> int:
    init_schema(conn)

    conn.execute("INSERT INTO retailers(name) VALUES ('Amazon')")
    retailer_id = int(conn.execute("SELECT id FROM retailers WHERE name='Amazon'").fetchone()["id"])

    conn.execute("INSERT INTO products(name, brand, model) VALUES ('AirPods Pro', 'Apple', '2')")
    product_id = int(conn.execute("SELECT id FROM products WHERE name='AirPods Pro'").fetchone()["id"])

    conn.execute(
        """
        INSERT INTO listings(
          product_id, retailer_id, url, currency, active,
          fixture_base_price_cents, fixture_step_cents, fixture_period
        ) VALUES (?, ?, ?, 'USD', 1, 10000, -100, 5)
        """,
        (product_id, retailer_id, "https://example.com/airpods"),
    )
    listing_id = int(conn.execute("SELECT id FROM listings").fetchone()["id"])
    return listing_id


def test_delta_computation_within_window():
    conn = _conn()
    listing_id = _seed_minimal(conn)

    # Insert an "older" snapshot outside the window (8 hours ago)
    conn.execute(
        """
        INSERT INTO price_snapshots(listing_id, price_cents, currency, captured_at)
        VALUES (?, ?, 'USD', datetime('now', '-8 hours'))
        """,
        (listing_id, 12000),
    )
    # Insert a snapshot at the start of window (5 hours ago, window=6)
    conn.execute(
        """
        INSERT INTO price_snapshots(listing_id, price_cents, currency, captured_at)
        VALUES (?, ?, 'USD', datetime('now', '-5 hours'))
        """,
        (listing_id, 10000),
    )
    # Insert current snapshot (now)
    conn.execute(
        """
        INSERT INTO price_snapshots(listing_id, price_cents, currency, captured_at)
        VALUES (?, ?, 'USD', datetime('now'))
        """,
        (listing_id, 9000),
    )

    summary = get_listing_price_summary(conn, listing_id, window_hours=6)
    assert summary.current_price_cents == 9000
    assert summary.window_start_price_cents == 10000
    assert summary.delta_cents == -1000
    assert summary.delta_pct is not None
    assert abs(summary.delta_pct - (-10.0)) < 1e-9


def test_no_snapshots_returns_none_prices():
    conn = _conn()
    listing_id = _seed_minimal(conn)

    summary = get_listing_price_summary(conn, listing_id, window_hours=6)
    assert summary.current_price_cents is None
    assert summary.window_start_price_cents is None
    assert summary.delta_cents is None
    assert summary.delta_pct is None
