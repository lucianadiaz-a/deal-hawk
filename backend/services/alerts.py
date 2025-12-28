from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Iterable, Optional

from backend.services.pricing import get_listing_price_summary


@dataclass(frozen=True)
class AlertRule:
    name: str
    threshold_pct: float  # e.g., 10.0 means trigger at <= -10%


@dataclass(frozen=True)
class AlertEvalResult:
    evaluated: int
    triggered: int


def iter_active_listing_ids(conn: sqlite3.Connection) -> Iterable[int]:
    rows = conn.execute("SELECT id FROM listings WHERE active = 1 ORDER BY id").fetchall()
    for r in rows:
        yield int(r["id"])


def _latest_alert_event(
    conn: sqlite3.Connection,
    listing_id: int,
    rule_name: str,
    threshold_pct: float,
) -> Optional[sqlite3.Row]:
    return conn.execute(
        """
        SELECT id, prev_price_cents, new_price_cents, triggered_at
        FROM alert_events
        WHERE listing_id = ?
          AND rule_name = ?
          AND threshold_pct = ?
        ORDER BY triggered_at DESC, id DESC
        LIMIT 1
        """,
        (listing_id, rule_name, float(threshold_pct)),
    ).fetchone()


def evaluate_alert_for_listing(
    conn: sqlite3.Connection,
    listing_id: int,
    window_hours: int,
    rule: AlertRule,
) -> bool:
    """
    Creates an AlertEvent if the listing's delta_pct over `window_hours`
    is <= -rule.threshold_pct.

    Dedup policy (POC):
    - If the most recent AlertEvent for this listing+rule already has the same
      (prev_price_cents, new_price_cents), do not create another.
    """
    s = get_listing_price_summary(conn, listing_id, window_hours=window_hours)

    if s.current_price_cents is None or s.window_start_price_cents is None:
        return False

    if s.delta_pct is None:
        return False

    should_trigger = s.delta_pct <= (-1.0 * float(rule.threshold_pct))
    if not should_trigger:
        return False

    latest = _latest_alert_event(conn, listing_id, rule.name, rule.threshold_pct)
    if latest is not None:
        if int(latest["prev_price_cents"]) == int(s.window_start_price_cents) and int(
            latest["new_price_cents"]
        ) == int(s.current_price_cents):
            return False

    prev_cents = int(s.window_start_price_cents)
    new_cents = int(s.current_price_cents)
    preview = (
        f"{s.product_name} at {s.retailer_name} dropped "
        f"{abs(s.delta_pct):.1f}% (${prev_cents/100:.2f} → ${new_cents/100:.2f})"
    )

    conn.execute(
        """
        INSERT INTO alert_events(
            listing_id, rule_name, threshold_pct, prev_price_cents, new_price_cents, triggered_at, message_preview
        )
        VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
        """,
        (listing_id, rule.name, float(rule.threshold_pct), prev_cents, new_cents, preview),
    )
    return True


def evaluate_alerts(
    conn: sqlite3.Connection,
    window_hours: int = 6,
    threshold_pct: float = 10.0,
    rule_name: str = "Price drop",
) -> AlertEvalResult:
    rule = AlertRule(name=rule_name, threshold_pct=float(threshold_pct))
    evaluated = 0
    triggered = 0

    for listing_id in iter_active_listing_ids(conn):
        evaluated += 1
        if evaluate_alert_for_listing(conn, listing_id, window_hours=window_hours, rule=rule):
            triggered += 1

    return AlertEvalResult(evaluated=evaluated, triggered=triggered)
