from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend.db import db_conn, init_schema
from backend.services.seed import seed_from_json

SEED_PATH = REPO_ROOT / "data" / "seed_listings.json"


def main() -> int:
    with db_conn() as conn:
        init_schema(conn)
        result = seed_from_json(conn, SEED_PATH)

    print(
        f"Seeded DB with {result.retailers} retailers, "
        f"{result.products} products, {result.listings} listings."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
