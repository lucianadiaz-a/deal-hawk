from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SeedResult:
    """Result of seed operation."""
    products: int
    retailers: int
    listings: int


def seed_from_json(conn: sqlite3.Connection, seed_path: Path) -> SeedResult:
    """
    Seed database from JSON file (idempotent).
    
    Inserts or updates retailers, products, and listings from the seed file.
    Uses INSERT OR IGNORE for retailers and products, and ON CONFLICT DO UPDATE
    for listings to preserve existing price history.
    
    Args:
        conn: SQLite connection
        seed_path: Path to seed JSON file
    
    Returns:
        SeedResult with counts of seeded entities
    """
    if not seed_path.exists():
        raise FileNotFoundError(f"Seed file not found: {seed_path}")

    payload = json.loads(seed_path.read_text(encoding="utf-8"))

    retailers: list[str] = payload["retailers"]
    products: list[dict] = payload["products"]
    listings: list[dict] = payload["listings"]

    # Retailers (idempotent: INSERT OR IGNORE)
    retailer_id_by_name: dict[str, int] = {}
    for name in retailers:
        conn.execute("INSERT OR IGNORE INTO retailers(name) VALUES (?)", (name,))
    rows = conn.execute("SELECT id, name FROM retailers").fetchall()
    for r in rows:
        retailer_id_by_name[str(r["name"])] = int(r["id"])

    # Products (idempotent: INSERT OR IGNORE, then fetch IDs)
    product_ids: list[int] = []
    for p in products:
        conn.execute(
            """
            INSERT OR IGNORE INTO products(name, brand, model)
            VALUES (?, ?, ?)
            """,
            (p["name"], p.get("brand"), p.get("model")),
        )
        # Fetch the ID (either newly inserted or existing) using identity key
        # Match the index: name || COALESCE('|' || brand, '') || COALESCE('|' || model, '')
        identity_key = p["name"] + (f"|{p['brand']}" if p.get("brand") else "") + (f"|{p['model']}" if p.get("model") else "")
        row = conn.execute(
            """
            SELECT id FROM products
            WHERE name || COALESCE('|' || brand, '') || COALESCE('|' || model, '') = ?
            """,
            (identity_key,),
        ).fetchone()
        if row is None:
            raise RuntimeError(f"Failed to get product ID for: {p['name']}")
        product_ids.append(int(row["id"]))

    # Listings (idempotent: ON CONFLICT DO UPDATE to preserve history)
    for l in listings:
        product_id = product_ids[int(l["product_index"])]
        retailer_name = str(l["retailer"])
        retailer_id = retailer_id_by_name[retailer_name]

        conn.execute(
            """
            INSERT INTO listings(
                product_id, retailer_id, url, external_sku, currency, active,
                fixture_base_price_cents, fixture_step_cents, fixture_period
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(product_id, retailer_id) DO UPDATE SET
                url = excluded.url,
                external_sku = excluded.external_sku,
                currency = excluded.currency,
                active = excluded.active,
                fixture_base_price_cents = excluded.fixture_base_price_cents,
                fixture_step_cents = excluded.fixture_step_cents,
                fixture_period = excluded.fixture_period
            """,
            (
                product_id,
                retailer_id,
                l["url"],
                l.get("external_sku"),
                l.get("currency", "USD"),
                1,
                int(l["base_price_cents"]),
                int(l.get("step_cents", 0)),
                int(l.get("period", 5)),
            ),
        )

    return SeedResult(
        products=len(products),
        retailers=len(retailers),
        listings=len(listings),
    )


def reset_db(conn: sqlite3.Connection) -> None:
    """
    Reset database by deleting all rows (demo/dev use only).
    
    Deletes rows from tables in dependency order (children first) to respect
    foreign key constraints. Schema remains intact.
    
    DANGER: This deletes all data including price history and alerts.
    Not intended for production use.
    
    Args:
        conn: SQLite connection
    """
    # Delete in dependency order (children first):
    # alert_events → price_snapshots → listings → products + retailers
    conn.execute("DELETE FROM alert_events")
    conn.execute("DELETE FROM price_snapshots")
    conn.execute("DELETE FROM listings")
    conn.execute("DELETE FROM products")
    conn.execute("DELETE FROM retailers")


