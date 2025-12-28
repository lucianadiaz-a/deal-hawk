from __future__ import annotations

import sqlite3


def get_fixture_price_cents(conn: sqlite3.Connection, listing_id: int) -> int:
    """
    Deterministic "price movement" without network access.

    Price is computed from listing fixture params + existing snapshot count:
      price = base + step * (n % period)

    If step is negative, prices trend downward in a loop (good for demo/alerts).
    """
    listing = conn.execute(
        """
        SELECT fixture_base_price_cents, fixture_step_cents, fixture_period
        FROM listings
        WHERE id = ?
        """,
        (listing_id,),
    ).fetchone()
    if listing is None:
        raise ValueError(f"listing not found: {listing_id}")

    base = int(listing["fixture_base_price_cents"])
    step = int(listing["fixture_step_cents"])
    period = max(1, int(listing["fixture_period"]))

    n = conn.execute(
        "SELECT COUNT(1) AS c FROM price_snapshots WHERE listing_id = ?",
        (listing_id,),
    ).fetchone()
    count = int(n["c"]) if n is not None else 0

    return base + step * (count % period)
