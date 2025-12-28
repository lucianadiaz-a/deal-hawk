from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to Python path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend.db import db_conn, init_schema
SEED_PATH = REPO_ROOT / "data" / "seed_listings.json"


def main() -> int:
    if not SEED_PATH.exists():
        raise FileNotFoundError(f"Seed file not found: {SEED_PATH}")

    payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))

    retailers: list[str] = payload["retailers"]
    products: list[dict] = payload["products"]
    listings: list[dict] = payload["listings"]

    with db_conn() as conn:
        init_schema(conn)

        # Retailers
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

    print("Seeded DB with retailers, products, listings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
