#!/usr/bin/env python3
"""Verify that the demo database is properly populated and static."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend.db import DbConfig, db_conn


def verify_demo_db(db_path: Path) -> bool:
    """Verify demo DB has complete, static data."""
    if not db_path.exists():
        print(f"❌ Demo database not found: {db_path}")
        return False
    
    cfg = DbConfig(path=db_path)
    with db_conn(cfg) as conn:
        # Check listings count
        listing_count = conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
        
        # Check snapshots count
        snapshot_count = conn.execute("SELECT COUNT(*) FROM price_snapshots").fetchone()[0]
        
        # Check listings with zero snapshots
        listings_with_zero = conn.execute(
            """
            SELECT COUNT(*) 
            FROM listings l
            LEFT JOIN price_snapshots ps ON l.id = ps.listing_id
            WHERE ps.id IS NULL
            """
        ).fetchone()[0]
        
        # Check products with incomplete retailer coverage
        products_with_incomplete = conn.execute(
            """
            SELECT p.id, p.name, COUNT(DISTINCT r.id) as retailer_count
            FROM products p
            JOIN listings l ON p.id = l.product_id
            JOIN retailers r ON l.retailer_id = r.id
            GROUP BY p.id, p.name
            HAVING COUNT(DISTINCT r.id) < 3
            """
        ).fetchall()
        
        # Check snapshots per listing
        min_snapshots = conn.execute(
            """
            SELECT MIN(cnt) 
            FROM (
                SELECT listing_id, COUNT(*) AS cnt
                FROM price_snapshots
                GROUP BY listing_id
            )
            """
        ).fetchone()[0]
        
        print(f"📊 Demo Database Verification: {db_path}")
        print(f"   Listings: {listing_count}")
        print(f"   Total snapshots: {snapshot_count}")
        print(f"   Listings with 0 snapshots: {listings_with_zero}")
        print(f"   Minimum snapshots per listing: {min_snapshots}")
        
        if listings_with_zero > 0:
            print(f"❌ FAILED: {listings_with_zero} listings have 0 snapshots")
            return False
        
        if min_snapshots < 24:
            print(f"❌ FAILED: Some listings have fewer than 24 snapshots (min: {min_snapshots})")
            return False
        
        if products_with_incomplete:
            print(f"⚠️  WARNING: {len(products_with_incomplete)} products don't have all 3 retailers:")
            for row in products_with_incomplete[:5]:
                print(f"   - {row[1]} (only {row[2]} retailers)")
        
        print("✅ Demo database is properly populated and static!")
        return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db-path",
        type=Path,
        default=REPO_ROOT / "data" / "demo.sqlite3",
        help="Path to demo database"
    )
    args = parser.parse_args()
    
    success = verify_demo_db(args.db_path)
    sys.exit(0 if success else 1)

