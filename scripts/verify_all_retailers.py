#!/usr/bin/env python3
"""Verify that every product has listings for all retailers with price history."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend.db import DbConfig, db_conn


def verify_all_retailers(db_path: Path) -> bool:
    """Verify every product has all retailers with price history."""
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    cfg = DbConfig(path=db_path)
    with db_conn(cfg) as conn:
        # Get retailer count
        retailer_count = conn.execute("SELECT COUNT(*) FROM retailers").fetchone()[0]
        print(f"📊 Total retailers: {retailer_count}")
        
        # Check each product
        products = conn.execute(
            """
            SELECT p.id, p.name
            FROM products p
            ORDER BY p.id
            """
        ).fetchall()
        
        all_good = True
        for product_row in products:
            product_id = int(product_row["id"])
            product_name = str(product_row["name"])
            
            # Get retailers for this product
            retailers = conn.execute(
                """
                SELECT r.id, r.name, l.id as listing_id, COUNT(ps.id) as snapshot_count
                FROM retailers r
                LEFT JOIN listings l ON l.retailer_id = r.id AND l.product_id = ?
                LEFT JOIN price_snapshots ps ON ps.listing_id = l.id
                GROUP BY r.id, r.name, l.id
                ORDER BY r.name
                """
            , (product_id,)).fetchall()
            
            missing_retailers = []
            retailers_without_snapshots = []
            
            for retailer_row in retailers:
                retailer_name = str(retailer_row["name"])
                listing_id = retailer_row["listing_id"]
                snapshot_count = retailer_row["snapshot_count"] or 0
                
                if listing_id is None:
                    missing_retailers.append(retailer_name)
                elif snapshot_count == 0:
                    retailers_without_snapshots.append(retailer_name)
            
            if missing_retailers or retailers_without_snapshots:
                all_good = False
                print(f"\n❌ {product_name} (ID: {product_id}):")
                if missing_retailers:
                    print(f"   Missing retailers: {', '.join(missing_retailers)}")
                if retailers_without_snapshots:
                    print(f"   Retailers without snapshots: {', '.join(retailers_without_snapshots)}")
            else:
                retailer_names = [str(r["name"]) for r in retailers]
                print(f"✅ {product_name}: {len(retailer_names)} retailers ({', '.join(retailer_names)})")
        
        if all_good:
            print(f"\n✅ SUCCESS: All {len(products)} products have listings for all {retailer_count} retailers with price history!")
        else:
            print(f"\n❌ FAILED: Some products are missing retailers or price history")
        
        return all_good


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db-path",
        type=Path,
        default=REPO_ROOT / "data" / "demo.sqlite3",
        help="Path to database"
    )
    args = parser.parse_args()
    
    success = verify_all_retailers(args.db_path)
    sys.exit(0 if success else 1)

