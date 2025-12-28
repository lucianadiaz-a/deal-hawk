from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ListingPriceSummary:
    listing_id: int
    product_name: str
    retailer_name: str
    url: str
    currency: str

    current_price_cents: Optional[int]
    current_captured_at: Optional[str]

    window_start_price_cents: Optional[int]
    window_start_captured_at: Optional[str]

    delta_cents: Optional[int]
    delta_pct: Optional[float]


def _now_utc_iso() -> str:
    # SQLite stores captured_at via datetime('now'), which is UTC.
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def get_listing_price_summary(
    conn: sqlite3.Connection,
    listing_id: int,
    window_hours: int = 6,
) -> ListingPriceSummary:
    """
    Returns current price and delta over the last `window_hours`.
    Delta is computed as: current - earliest snapshot within the window.
    If there are no snapshots, returns None fields for prices/deltas.
    """
    base = conn.execute(
        """
        SELECT
            l.id AS listing_id,
            p.name AS product_name,
            r.name AS retailer_name,
            l.url AS url,
            l.currency AS currency
        FROM listings l
        JOIN products p ON p.id = l.product_id
        JOIN retailers r ON r.id = l.retailer_id
        WHERE l.id = ?
        """,
        (listing_id,),
    ).fetchone()
    if base is None:
        raise ValueError(f"listing not found: {listing_id}")

    current = conn.execute(
        """
        SELECT price_cents, captured_at
        FROM price_snapshots
        WHERE listing_id = ?
        ORDER BY captured_at DESC, id DESC
        LIMIT 1
        """,
        (listing_id,),
    ).fetchone()

    # Earliest snapshot within the window (inclusive)
    window = conn.execute(
        """
        SELECT price_cents, captured_at
        FROM price_snapshots
        WHERE listing_id = ?
          AND captured_at >= datetime('now', ?)
        ORDER BY captured_at ASC, id ASC
        LIMIT 1
        """,
        (listing_id, f"-{int(window_hours)} hours"),
    ).fetchone()

    current_price = int(current["price_cents"]) if current is not None else None
    current_at = str(current["captured_at"]) if current is not None else None

    window_price = int(window["price_cents"]) if window is not None else None
    window_at = str(window["captured_at"]) if window is not None else None

    delta_cents: Optional[int] = None
    delta_pct: Optional[float] = None
    if current_price is not None and window_price is not None:
        delta_cents = current_price - window_price
        if window_price != 0:
            delta_pct = (delta_cents / window_price) * 100.0

    return ListingPriceSummary(
        listing_id=int(base["listing_id"]),
        product_name=str(base["product_name"]),
        retailer_name=str(base["retailer_name"]),
        url=str(base["url"]),
        currency=str(base["currency"]),
        current_price_cents=current_price,
        current_captured_at=current_at,
        window_start_price_cents=window_price,
        window_start_captured_at=window_at,
        delta_cents=delta_cents,
        delta_pct=delta_pct,
    )


def list_price_summaries(
    conn: sqlite3.Connection,
    window_hours: int = 6,
    active_only: bool = True,
) -> list[ListingPriceSummary]:
    """
    Returns a summary per listing, suitable for an overview table.

    Uses per-listing subqueries for clarity (POC). If performance becomes an issue,
    we can optimize with CTEs/window functions later.
    """
    where = "WHERE l.active = 1" if active_only else ""
    listing_rows = conn.execute(
        f"""
        SELECT
            l.id AS listing_id
        FROM listings l
        {where}
        ORDER BY l.id
        """
    ).fetchall()

    return [
        get_listing_price_summary(conn, int(r["listing_id"]), window_hours=window_hours)
        for r in listing_rows
    ]
