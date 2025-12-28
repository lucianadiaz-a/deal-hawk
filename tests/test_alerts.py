from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

# Add project root to Python path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend.db import init_schema
from backend.services.alerts import AlertRule, evaluate_alert_for_listing


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
    return int(conn.execute("SELECT id FROM listings").fetchone()["id"])


def test_alert_triggers_and_dedupes():
    conn = _conn()
    listing_id = _seed_minimal(conn)

    # Window start snapshot within 6 hours
    conn.execute(
        """
        INSERT INTO price_snapshots(listing_id, price_cents, currency, captured_at)
        VALUES (?, ?, 'USD', datetime('now', '-5 hours'))
        """,
        (listing_id, 10000),
    )
    # Current snapshot now (15% drop)
    conn.execute(
        """
        INSERT INTO price_snapshots(listing_id, price_cents, currency, captured_at)
        VALUES (?, ?, 'USD', datetime('now'))
        """,
        (listing_id, 8500),
    )

    rule = AlertRule(name="Price drop", threshold_pct=10.0)

    created_1 = evaluate_alert_for_listing(conn, listing_id, window_hours=6, rule=rule)
    assert created_1 is True
    n1 = int(conn.execute("SELECT COUNT(*) AS c FROM alert_events").fetchone()["c"])
    assert n1 == 1

    # Run again with same data: should NOT duplicate
    created_2 = evaluate_alert_for_listing(conn, listing_id, window_hours=6, rule=rule)
    assert created_2 is False
    n2 = int(conn.execute("SELECT COUNT(*) AS c FROM alert_events").fetchone()["c"])
    assert n2 == 1


def test_alert_does_not_trigger_when_above_threshold():
    conn = _conn()
    listing_id = _seed_minimal(conn)

    conn.execute(
        """
        INSERT INTO price_snapshots(listing_id, price_cents, currency, captured_at)
        VALUES (?, ?, 'USD', datetime('now', '-5 hours'))
        """,
        (listing_id, 10000),
    )
    # Only 5% drop
    conn.execute(
        """
        INSERT INTO price_snapshots(listing_id, price_cents, currency, captured_at)
        VALUES (?, ?, 'USD', datetime('now'))
        """,
        (listing_id, 9500),
    )

    rule = AlertRule(name="Price drop", threshold_pct=10.0)
    created = evaluate_alert_for_listing(conn, listing_id, window_hours=6, rule=rule)
    assert created is False
    n = int(conn.execute("SELECT COUNT(*) AS c FROM alert_events").fetchone()["c"])
    assert n == 0
