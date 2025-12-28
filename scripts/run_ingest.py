from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend.db import db_conn, init_schema
from backend.services.ingest import run_ingest_cycle


def main() -> int:
    with db_conn() as conn:
        init_schema(conn)
        result = run_ingest_cycle(conn)

    print(f"Ingest cycle complete. Snapshots written: {result.snapshots_written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
