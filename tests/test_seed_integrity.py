#!/usr/bin/env python3
"""
Seed/Ingest Integrity Test Harness

Verifies that seeding is truly idempotent and does not delete price history.
"""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


# Locate DB path using the same rule as the app
DEFAULT_DB_PATH = "data/deal_hawk.sqlite3"


def get_db_path() -> Path:
    """Get DB path from env var or default."""
    raw = os.getenv("DEAL_HAWK_DB_PATH", DEFAULT_DB_PATH)
    return Path(raw)


class Counts(NamedTuple):
    """Database table counts."""

    products: int
    retailers: int
    listings: int
    price_snapshots: int
    alert_events: int


def get_counts(conn: sqlite3.Connection) -> Counts:
    """Get counts for all relevant tables."""
    return Counts(
        products=conn.execute("SELECT COUNT(*) FROM products").fetchone()[0],
        retailers=conn.execute("SELECT COUNT(*) FROM retailers").fetchone()[0],
        listings=conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0],
        price_snapshots=conn.execute("SELECT COUNT(*) FROM price_snapshots").fetchone()[0],
        alert_events=conn.execute("SELECT COUNT(*) FROM alert_events").fetchone()[0],
    )


def get_listing_ids(conn: sqlite3.Connection, limit: int = 10) -> list[int]:
    """Get first N listing IDs, ordered by id."""
    rows = conn.execute(
        "SELECT id FROM listings ORDER BY id LIMIT ?", (limit,)
    ).fetchall()
    return [int(row[0]) for row in rows]


def check_products_uniqueness(conn: sqlite3.Connection) -> tuple[bool, list[tuple]]:
    """
    Check for unique index on products and detect duplicates.
    Returns (has_unique_index, list_of_duplicates).
    """
    # Check for unique indexes
    index_rows = conn.execute("PRAGMA index_list('products')").fetchall()
    has_unique = False
    for row in index_rows:
        # row[1] is the index name, row[2] is 1 if unique
        if row[2] == 1:  # unique index
            has_unique = True
            break

    # Check for duplicates by name+brand+model
    duplicate_rows = conn.execute(
        """
        SELECT name, brand, model, COUNT(*) as cnt
        FROM products
        GROUP BY name, brand, model
        HAVING COUNT(*) > 1
        """
    ).fetchall()

    duplicates = [(row[0], row[1], row[2], row[3]) for row in duplicate_rows]

    return has_unique, duplicates


def run_script(script_name: str) -> tuple[int, str, str]:
    """Run a Python script and return (exit_code, stdout, stderr)."""
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / script_name

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )

    return result.returncode, result.stdout, result.stderr


def print_counts_table(
    label: str,
    counts: Counts,
    active_listings: int | None = None,
):
    """Print a compact summary table of counts."""
    print(f"\n{label}")
    print("=" * 60)
    print(f"  products:        {counts.products:>6}")
    print(f"  retailers:       {counts.retailers:>6}")
    print(f"  listings:        {counts.listings:>6}")
    if active_listings is not None:
        print(f"  active_listings: {active_listings:>6}")
    print(f"  price_snapshots: {counts.price_snapshots:>6}")
    print(f"  alert_events:    {counts.alert_events:>6}")
    print()


def test_seed_and_ingest_integrity():
    """Test that seeding is idempotent and does not delete price history."""
    db_path = get_db_path()

    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found at {db_path}. "
            "Please initialize the database first: python -m backend.db init"
        )

    print("=" * 60)
    print("SEED/INGEST INTEGRITY TEST HARNESS")
    print("=" * 60)
    print(f"Database: {db_path}")

    # Connect to database
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    try:
        # BEFORE: Get initial state
        print("\n[1] Capturing BEFORE state...")
        counts_before = get_counts(conn)
        listing_ids_before = get_listing_ids(conn, limit=10)
        active_listings_before = conn.execute(
            "SELECT COUNT(*) FROM listings WHERE active = 1"
        ).fetchone()[0]

        print_counts_table("BEFORE seed", counts_before, active_listings_before)
        print(f"First 10 listing IDs: {listing_ids_before}")

        # Check products uniqueness enforcement
        print("\n[2] Checking products uniqueness enforcement...")
        has_unique_index, duplicates = check_products_uniqueness(conn)

        # Get index list for printing
        index_rows = conn.execute("PRAGMA index_list('products')").fetchall()
        print("PRAGMA index_list('products'):")
        for row in index_rows:
            unique_flag = "UNIQUE" if row[2] == 1 else "NON-UNIQUE"
            print(f"  - {row[1]} ({unique_flag})")

        if duplicates:
            print("\nERROR: Duplicate products detected:")
            for name, brand, model, cnt in duplicates:
                print(f"  - name='{name}', brand='{brand}', model='{model}': {cnt} rows")
        else:
            print("No duplicate products found.")

        # Run seed
        print("\n[3] Running seed_db.py...")
        seed_exit, seed_stdout, seed_stderr = run_script("scripts/seed_db.py")
        if seed_exit != 0:
            raise RuntimeError(
                f"seed_db.py failed with exit code {seed_exit}\n"
                f"stdout: {seed_stdout}\n"
                f"stderr: {seed_stderr}"
            )

        print("Seed completed successfully.")

        # AFTER SEED: Get state after seed
        print("\n[4] Capturing AFTER seed state...")
        counts_after_seed = get_counts(conn)
        listing_ids_after_seed = get_listing_ids(conn, limit=10)
        active_listings_after_seed = conn.execute(
            "SELECT COUNT(*) FROM listings WHERE active = 1"
        ).fetchone()[0]

        print_counts_table("AFTER seed", counts_after_seed, active_listings_after_seed)
        print(f"First 10 listing IDs: {listing_ids_after_seed}")

        # Re-check products uniqueness after seed
        print("\n[4a] Re-checking products uniqueness after seed...")
        has_unique_index_after, duplicates_after = check_products_uniqueness(conn)
        if duplicates_after:
            print("WARNING: Duplicate products still detected after seed:")
            for name, brand, model, cnt in duplicates_after:
                print(f"  - name='{name}', brand='{brand}', model='{model}': {cnt} rows")
        else:
            print("No duplicate products found after seed.")

        # Run ingest
        print("\n[5] Running run_ingest.py...")
        ingest_exit, ingest_stdout, ingest_stderr = run_script("scripts/run_ingest.py")
        if ingest_exit != 0:
            raise RuntimeError(
                f"run_ingest.py failed with exit code {ingest_exit}\n"
                f"stdout: {ingest_stdout}\n"
                f"stderr: {ingest_stderr}"
            )

        print("Ingest completed successfully.")

        # AFTER INGEST: Get state after ingest
        print("\n[6] Capturing AFTER ingest state...")
        counts_after_ingest = get_counts(conn)
        active_listings_after_ingest = conn.execute(
            "SELECT COUNT(*) FROM listings WHERE active = 1"
        ).fetchone()[0]

        print_counts_table("AFTER ingest", counts_after_ingest, active_listings_after_ingest)

        # Verify invariants
        print("\n[7] Verifying invariants...")
        print("=" * 60)

        # Invariant A: Running seed does NOT decrease counts for price_snapshots or alert_events
        print("\n[A] price_snapshots and alert_events must not decrease after seed")
        price_snapshots_ok = counts_after_seed.price_snapshots >= counts_before.price_snapshots
        alert_events_ok = counts_after_seed.alert_events >= counts_before.alert_events

        if price_snapshots_ok and alert_events_ok:
            print("  PASS: price_snapshots and alert_events preserved")
        else:
            print("  FAIL:")
            if not price_snapshots_ok:
                print(
                    f"    price_snapshots decreased: {counts_before.price_snapshots} -> {counts_after_seed.price_snapshots}"
                )
            if not alert_events_ok:
                print(
                    f"    alert_events decreased: {counts_before.alert_events} -> {counts_after_seed.alert_events}"
                )
        assert price_snapshots_ok, f"price_snapshots decreased: {counts_before.price_snapshots} -> {counts_after_seed.price_snapshots}"
        assert alert_events_ok, f"alert_events decreased: {counts_before.alert_events} -> {counts_after_seed.alert_events}"

        # Invariant B: Running seed does NOT increase counts for products, retailers, or listings
        print("\n[B] products, retailers, listings must not increase after seed")
        products_ok = counts_after_seed.products <= counts_before.products
        retailers_ok = counts_after_seed.retailers <= counts_before.retailers
        listings_ok = counts_after_seed.listings <= counts_before.listings

        if products_ok and retailers_ok and listings_ok:
            if (
                counts_after_seed.products == counts_before.products
                and counts_after_seed.retailers == counts_before.retailers
                and counts_after_seed.listings == counts_before.listings
            ):
                print("  PASS: products, retailers, listings unchanged (idempotent)")
            else:
                print("  PASS: products, retailers, listings decreased (one-time deduplication)")
        else:
            print("  FAIL:")
            if not products_ok:
                print(
                    f"    products increased: {counts_before.products} -> {counts_after_seed.products}"
                )
            if not retailers_ok:
                print(
                    f"    retailers increased: {counts_before.retailers} -> {counts_after_seed.retailers}"
                )
            if not listings_ok:
                print(
                    f"    listings increased: {counts_before.listings} -> {counts_after_seed.listings}"
                )
        assert products_ok, f"products increased: {counts_before.products} -> {counts_after_seed.products}"
        assert retailers_ok, f"retailers increased: {counts_before.retailers} -> {counts_after_seed.retailers}"
        assert listings_ok, f"listings increased: {counts_before.listings} -> {counts_after_seed.listings}"

        # Invariant C: Listing IDs are stable
        print("\n[C] Listing IDs must be stable (first 10 must match)")
        listing_ids_ok = listing_ids_before == listing_ids_after_seed

        if listing_ids_ok:
            print("  PASS: Listing IDs stable")
        else:
            print("  FAIL:")
            print(f"    Before:  {listing_ids_before}")
            print(f"    After:   {listing_ids_after_seed}")
        assert listing_ids_ok, f"Listing IDs changed: {listing_ids_before} -> {listing_ids_after_seed}"

        # Invariant D: After running ingest once, price_snapshots increases by exactly the number of active listings
        print("\n[D] price_snapshots must increase by exactly active_listings after ingest")
        expected_increase = active_listings_after_seed
        actual_increase = counts_after_ingest.price_snapshots - counts_after_seed.price_snapshots
        ingest_ok = actual_increase == expected_increase

        if ingest_ok:
            print(f"  PASS: price_snapshots increased by {actual_increase} (expected {expected_increase})")
        else:
            print("  FAIL:")
            print(
                f"    Expected increase: {expected_increase} (active_listings)"
            )
            print(
                f"    Actual increase: {actual_increase}"
            )
        assert ingest_ok, f"price_snapshots increased by {actual_increase}, expected {expected_increase}"

        # Invariant E: Verify products uniqueness enforcement exists (check AFTER seed)
        print("\n[E] Products table must have at least one UNIQUE index")
        if has_unique_index_after:
            print("  PASS: UNIQUE index detected on products table")
        else:
            print("  FAIL: No UNIQUE index found on products table")
        assert has_unique_index_after, "No UNIQUE index found on products table"

        # Invariant F: No duplicates in products (check AFTER seed)
        print("\n[F] Products must have no duplicates (by name+brand+model)")
        if not duplicates_after:
            print("  PASS: No duplicate products found")
        else:
            print("  FAIL: Duplicate products detected after seed (see above)")
            for name, brand, model, cnt in duplicates_after:
                print(f"    - name='{name}', brand='{brand}', model='{model}': {cnt} rows")
        assert not duplicates_after, f"Duplicate products detected: {duplicates_after}"

        # Final summary
        print("\n" + "=" * 60)
        print("RESULT: ALL INVARIANTS PASSED ✓")

    finally:
        conn.close()


if __name__ == "__main__":
    try:
        test_seed_and_ingest_integrity()
    except (AssertionError, FileNotFoundError, RuntimeError) as e:
        print("\n" + "=" * 60)
        print("RESULT: ONE OR MORE INVARIANTS FAILED ✗")
        print(f"Error: {e}")
        raise SystemExit(1)

