#!/usr/bin/env python3
"""
Build a frozen demo database with deterministic price snapshots.

This script creates a SQLite database with:
- All seeded products/retailers/listings
- Deterministic price snapshots for EVERY listing
- Fixed timestamps so the DB is identical on every run
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to Python path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend.db import DbConfig, db_conn, init_schema
from backend.services.seed import seed_from_json


def deterministic_price_cents(
    listing_id: int,
    retailer_name: str,
    product_id: int,
    base_price_cents: int,
    snapshot_index: int,
    snapshot_count: int,
) -> int:
    """
    Generate a deterministic price for a listing at a specific snapshot index.
    Creates realistic demo scenarios: alerts, near misses, and price changes.
    
    Args:
        listing_id: Listing ID
        retailer_name: Retailer name
        product_id: Product ID
        base_price_cents: Base price from listing
        snapshot_index: Index of snapshot (0 = oldest, snapshot_count-1 = newest)
        snapshot_count: Total number of snapshots
        
    Returns:
        Price in cents (always >= 100)
    """
    # Create deterministic scenario based on listing_id
    # This ensures same listing always has same price pattern
    scenario_seed = listing_id % 10
    
    # Different scenarios for demo - MAXIMUM ALERTS, MINIMAL MUTED:
    # 0-5: Significant drops (triggers alerts, >10% drop) - 60% of listings
    # 6-7: Moderate drops (near misses, 7-10% drop) - 20% of listings
    # 8: Small drop (ok status, 3-5% drop) - 10% of listings
    # 9: Price increase - 10% of listings (only 1 in 10)
    # NO stable prices - everything has movement!
    
    # Calculate progress: 0.0 (oldest) to 1.0 (newest)
    progress = snapshot_index / max(1, snapshot_count - 1)
    
    # For 6-hour window alerts, we need drops in the last 6 hours
    # With 24 snapshots at 1-hour intervals, last 6 hours = last 6 snapshots
    # So progress > 0.75 (last 25% of timeline) = last 6 hours
    
    if scenario_seed in [0, 1, 2, 3, 4, 5]:
        # Scenario: Significant price drop (triggers alerts, >10% drop)
        # 60% of listings will have alerts!
        if progress <= 0.75:
            # Stable at base price for first 18 hours
            price = base_price_cents
        else:
            # Drop in last 6 hours - make it dramatic!
            drop_progress = (progress - 0.75) / 0.25  # 0.0 to 1.0 over last 6 hours
            # Create varied drop amounts: 12%, 14%, 16%, 18%, 20%, 22%
            drop_pct = 0.12 + (scenario_seed * 0.02)  # 12-22% drop
            price = int(base_price_cents * (1 - drop_pct * drop_progress))
            
    elif scenario_seed in [6, 7]:
        # Scenario: Moderate drop (near miss, 7-10% drop)
        # 20% of listings - good for near misses section
        if progress <= 0.75:
            price = base_price_cents
        else:
            drop_progress = (progress - 0.75) / 0.25
            drop_pct = 0.07 + (scenario_seed - 6) * 0.015  # 7-8.5% drop
            price = int(base_price_cents * (1 - drop_pct * drop_progress))
            
    elif scenario_seed == 8:
        # Scenario: Small drop (ok status, 3-5% drop)
        # 10% of listings
        if progress <= 0.75:
            price = base_price_cents
        else:
            drop_progress = (progress - 0.75) / 0.25
            drop_pct = 0.04  # 4% drop
            price = int(base_price_cents * (1 - drop_pct * drop_progress))
            
    else:  # scenario_seed == 9
        # Scenario: Price increase in last 6 hours (ONLY 10% of listings)
        if progress <= 0.75:
            price = int(base_price_cents * 0.95)  # Start 5% lower
        else:
            increase_progress = (progress - 0.75) / 0.25
            # Increase from 95% to 103% of base (8% increase)
            price = int(base_price_cents * (0.95 + 0.08 * increase_progress))
    
    # Ensure price never goes below 100 cents ($1.00) or above 2x base
    return max(100, min(price, base_price_cents * 2))


def build_demo_db(
    seed_path: Path,
    output_path: Path,
    snapshot_count: int = 24,
    snapshot_interval_minutes: int = 60,
    base_time: str = "2025-01-15T12:00:00",
) -> None:
    """
    Build a frozen demo database with deterministic data.
    
    Args:
        seed_path: Path to seed JSON file
        output_path: Path to output SQLite database
        snapshot_count: Number of snapshots per listing
        snapshot_interval_minutes: Minutes between snapshots
        base_time: Base timestamp (newest snapshot time) in ISO format
    """
    # Parse base time (use current time if not specified)
    if base_time is None:
        base_dt = datetime.utcnow()
    else:
        base_dt = datetime.fromisoformat(base_time.replace("Z", "+00:00").replace("T", " "))
        if base_dt.tzinfo is None:
            # Assume UTC if no timezone
            base_dt = base_dt.replace(tzinfo=None)
    
    print(f"Building demo database: {output_path}")
    print(f"  Seed file: {seed_path}")
    print(f"  Snapshots per listing: {snapshot_count}")
    print(f"  Interval: {snapshot_interval_minutes} minutes")
    print(f"  Base time: {base_dt}")
    
    # Remove existing DB if it exists
    if output_path.exists():
        print(f"  Removing existing database: {output_path}")
        output_path.unlink()
    
    # Also remove WAL/SHM files if they exist
    for suffix in ["-wal", "-shm"]:
        wal_path = Path(str(output_path) + suffix)
        if wal_path.exists():
            wal_path.unlink()
    
    # Create DB and initialize schema
    cfg = DbConfig(path=output_path)
    with db_conn(cfg) as conn:
        print("  Initializing schema...")
        init_schema(conn)
        
        # Seed products/retailers/listings
        print("  Seeding products/retailers/listings...")
        seed_result = seed_from_json(conn, seed_path)
        print(f"    Seeded: {seed_result.retailers} retailers, "
              f"{seed_result.products} products, {seed_result.listings} listings")
        
        # Get all listings with their details
        listings = conn.execute(
            """
            SELECT 
                l.id AS listing_id,
                l.fixture_base_price_cents,
                r.name AS retailer_name,
                l.product_id
            FROM listings l
            JOIN retailers r ON l.retailer_id = r.id
            ORDER BY l.id
            """
        ).fetchall()
        
        print(f"  Generating {snapshot_count} snapshots for {len(listings)} listings...")
        
        # Generate snapshots for each listing
        total_snapshots = 0
        for listing_row in listings:
            listing_id = int(listing_row["listing_id"])
            base_price = int(listing_row["fixture_base_price_cents"])
            retailer_name = str(listing_row["retailer_name"])
            product_id = int(listing_row["product_id"])
            
            # Generate snapshots from oldest to newest
            for i in range(snapshot_count):
                # Calculate timestamp: base_time - (snapshot_count - 1 - i) * interval
                offset_minutes = (snapshot_count - 1 - i) * snapshot_interval_minutes
                snapshot_time = base_dt - timedelta(minutes=offset_minutes)
                timestamp_str = snapshot_time.strftime("%Y-%m-%d %H:%M:%S")
                
                # Generate deterministic price
                price_cents = deterministic_price_cents(
                    listing_id=listing_id,
                    retailer_name=retailer_name,
                    product_id=product_id,
                    base_price_cents=base_price,
                    snapshot_index=i,
                    snapshot_count=snapshot_count,
                )
                
                # Insert snapshot
                conn.execute(
                    """
                    INSERT INTO price_snapshots(
                        listing_id, price_cents, currency, captured_at
                    )
                    VALUES (?, ?, 'USD', ?)
                    """,
                    (listing_id, price_cents, timestamp_str),
                )
                total_snapshots += 1
        
        print(f"    Inserted {total_snapshots} price snapshots")
        
        # Generate alert events for listings with significant price drops
        print("  Generating alert events for significant price drops...")
        from backend.services.alerts import AlertRule
        
        alert_rule = AlertRule(name="Price drop", threshold_pct=10.0)
        alerts_created = 0
        window_hours = 6
        
        # Check each listing for price drops that would trigger alerts
        # We need to manually calculate deltas since get_listing_price_summary uses datetime('now')
        for listing_row in listings:
            listing_id = int(listing_row["listing_id"])
            retailer_name = str(listing_row["retailer_name"])
            
            # Get product name for alert message
            product_info = conn.execute(
                """
                SELECT p.name
                FROM products p
                JOIN listings l ON p.id = l.product_id
                WHERE l.id = ?
                """,
                (listing_id,)
            ).fetchone()
            product_name = str(product_info["name"]) if product_info else "Unknown Product"
            
            # Get current (newest) price
            current_snapshot = conn.execute(
                """
                SELECT price_cents, captured_at
                FROM price_snapshots
                WHERE listing_id = ?
                ORDER BY captured_at DESC, id DESC
                LIMIT 1
                """
            , (listing_id,)).fetchone()
            
            if not current_snapshot:
                continue
            
            current_price = int(current_snapshot["price_cents"])
            current_time_str = str(current_snapshot["captured_at"])
            current_time = datetime.fromisoformat(current_time_str.replace("Z", "+00:00").replace("T", " "))
            if current_time.tzinfo is None:
                current_time = current_time.replace(tzinfo=None)
            
            # Get price from 6 hours ago (window start)
            window_start_time = current_time - timedelta(hours=window_hours)
            window_start_str = window_start_time.strftime("%Y-%m-%d %H:%M:%S")
            
            window_snapshot = conn.execute(
                """
                SELECT price_cents, captured_at
                FROM price_snapshots
                WHERE listing_id = ? AND captured_at >= ?
                ORDER BY captured_at ASC, id ASC
                LIMIT 1
                """
            , (listing_id, window_start_str)).fetchone()
            
            if not window_snapshot:
                # No snapshot in window, skip
                continue
            
            window_price = int(window_snapshot["price_cents"])
            
            # Calculate delta
            if window_price == 0:
                continue
            
            delta_pct = ((current_price - window_price) / window_price) * 100.0
            
            # If there's a significant drop (>= 10%), create an alert event
            if delta_pct <= -10.0:
                # Check if alert already exists for this price change
                existing = conn.execute(
                    """
                    SELECT id FROM alert_events
                    WHERE listing_id = ? 
                      AND prev_price_cents = ?
                      AND new_price_cents = ?
                    LIMIT 1
                    """,
                    (listing_id, window_price, current_price)
                ).fetchone()
                
                if not existing:
                    # Create alert event with timestamp when drop occurred (2 hours before current)
                    alert_time = current_time - timedelta(hours=2)
                    alert_time_str = alert_time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    preview = (
                        f"{product_name} at {retailer_name} dropped "
                        f"{abs(delta_pct):.1f}% "
                        f"(${window_price/100:.2f} → ${current_price/100:.2f})"
                    )
                    
                    conn.execute(
                        """
                        INSERT INTO alert_events(
                            listing_id, rule_name, threshold_pct, 
                            prev_price_cents, new_price_cents, triggered_at, message_preview
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            listing_id,
                            alert_rule.name,
                            float(alert_rule.threshold_pct),
                            window_price,
                            current_price,
                            alert_time_str,
                            preview,
                        ),
                    )
                    alerts_created += 1
        
        print(f"    Created {alerts_created} alert events")
        
        # Validation: Ensure ALL listings have snapshots
        print("  Validating snapshot coverage...")
        listing_count = conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
        listings_with_snapshots = conn.execute(
            """
            SELECT COUNT(DISTINCT listing_id) 
            FROM price_snapshots
            """
        ).fetchone()[0]
        listings_with_zero = conn.execute(
            """
            SELECT COUNT(*) 
            FROM listings l
            LEFT JOIN price_snapshots ps ON l.id = ps.listing_id
            WHERE ps.id IS NULL
            """
        ).fetchone()[0]
        
        print(f"    Total listings: {listing_count}")
        print(f"    Listings with snapshots: {listings_with_snapshots}")
        print(f"    Listings with 0 snapshots: {listings_with_zero}")
        
        if listings_with_zero > 0:
            raise RuntimeError(
                f"VALIDATION FAILED: {listings_with_zero} listings have 0 snapshots. "
                "Every listing must have at least one snapshot."
            )
        
        if listings_with_snapshots != listing_count:
            raise RuntimeError(
                f"VALIDATION FAILED: Expected {listing_count} listings with snapshots, "
                f"but found {listings_with_snapshots}"
            )
        
        # Count snapshots per listing (should all be >= snapshot_count)
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
        
        print(f"    Minimum snapshots per listing: {min_snapshots}")
        
        if min_snapshots < snapshot_count:
            raise RuntimeError(
                f"VALIDATION FAILED: Expected at least {snapshot_count} snapshots per listing, "
                f"but minimum is {min_snapshots}"
            )
        
        # CRITICAL VALIDATION: Ensure every product has listings for ALL retailers
        print("  Validating retailer coverage per product...")
        retailer_count = conn.execute("SELECT COUNT(*) FROM retailers").fetchone()[0]
        products_with_incomplete = conn.execute(
            """
            SELECT p.id, p.name, COUNT(DISTINCT r.id) as retailer_count
            FROM products p
            LEFT JOIN listings l ON p.id = l.product_id
            LEFT JOIN retailers r ON l.retailer_id = r.id
            GROUP BY p.id, p.name
            HAVING COUNT(DISTINCT r.id) < ?
            """,
            (retailer_count,),
        ).fetchall()
        
        if products_with_incomplete:
            print(f"    ✗ FAILED: {len(products_with_incomplete)} products missing retailers:")
            for row in products_with_incomplete:
                print(f"      - {row[1]} (only {row[2]} retailers, expected {retailer_count})")
            raise RuntimeError(
                f"VALIDATION FAILED: {len(products_with_incomplete)} products do not have "
                f"listings for all {retailer_count} retailers. Every product MUST have "
                "listings for every retailer."
            )
        
        print(f"    ✓ All products have listings for all {retailer_count} retailers")
        print("  ✓ All validations passed!")
    
    print(f"\n✓ Demo database created successfully: {output_path}")
    print(f"  Total snapshots: {total_snapshots}")
    print(f"  All listings have {snapshot_count} snapshots each")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a frozen demo database with deterministic price snapshots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--seed-path",
        type=Path,
        default=REPO_ROOT / "data" / "seed_listings.json",
        help="Path to seed JSON file (default: data/seed_listings.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "data" / "demo.sqlite3",
        help="Path to output SQLite database (default: data/demo.sqlite3)",
    )
    parser.add_argument(
        "--snapshot-count",
        type=int,
        default=24,
        help="Number of snapshots per listing (default: 24)",
    )
    parser.add_argument(
        "--snapshot-interval-minutes",
        type=int,
        default=60,
        help="Minutes between snapshots (default: 60)",
    )
    parser.add_argument(
        "--base-time",
        type=str,
        default=None,  # Will use current time if not specified
        help="Base timestamp for newest snapshot in ISO format (default: current time)",
    )
    
    args = parser.parse_args()
    
    if not args.seed_path.exists():
        print(f"ERROR: Seed file not found: {args.seed_path}")
        return 1
    
    try:
        build_demo_db(
            seed_path=args.seed_path,
            output_path=args.output,
            snapshot_count=args.snapshot_count,
            snapshot_interval_minutes=args.snapshot_interval_minutes,
            base_time=args.base_time,
        )
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

