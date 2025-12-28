"""Regression tests for frozen demo database.

These tests verify that the demo database is truly frozen:
- API responses are identical across multiple calls
- All listings have price history
- No mutations occur during normal API reads
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

# Add project root to Python path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.db import DbConfig, db_conn, init_schema
from backend.services.seed import seed_from_json

# Import the build script function
# We need to import it as a module, so add scripts to path
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from build_demo_db import build_demo_db


@pytest.fixture
def demo_db_path():
    """Create a temporary demo database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as f:
        db_path = Path(f.name)
    
    # Build demo DB
    seed_path = REPO_ROOT / "data" / "seed_listings.json"
    build_demo_db(
        seed_path=seed_path,
        output_path=db_path,
        snapshot_count=24,
        snapshot_interval_minutes=60,
        base_time="2025-01-15T12:00:00",
    )
    
    yield db_path
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()
    for suffix in ["-wal", "-shm"]:
        wal_path = Path(str(db_path) + suffix)
        if wal_path.exists():
            wal_path.unlink()


@pytest.fixture
def demo_client(demo_db_path, monkeypatch):
    """Create a test client using the demo database."""
    # Set environment variable to use demo DB
    monkeypatch.setenv("DEAL_HAWK_DB_PATH", str(demo_db_path))
    
    # Create test client
    client = TestClient(app)
    return client


def test_products_endpoint_identical_responses(demo_client):
    """Test that GET /api/products returns identical responses on multiple calls."""
    # Call endpoint twice
    response1 = demo_client.get("/api/products")
    response2 = demo_client.get("/api/products")
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Parse JSON responses
    data1 = response1.json()
    data2 = response2.json()
    
    # Responses should be byte-for-byte identical
    # Compare as JSON strings (sorted keys) for deterministic comparison
    json1 = json.dumps(data1, sort_keys=True)
    json2 = json.dumps(data2, sort_keys=True)
    
    assert json1 == json2, "API responses must be identical across calls"
    
    # Also verify structure
    assert "products" in data1
    assert "pagination" in data1


def test_product_detail_identical_responses(demo_client):
    """Test that GET /api/products/{id} returns identical responses on multiple calls."""
    # Get a product ID first
    products_response = demo_client.get("/api/products?page_size=1")
    assert products_response.status_code == 200
    products = products_response.json()["products"]
    
    if len(products) == 0:
        pytest.skip("No products in database")
    
    product_id = products[0]["product_id"]
    
    # Call detail endpoint twice
    response1 = demo_client.get(f"/api/products/{product_id}")
    response2 = demo_client.get(f"/api/products/{product_id}")
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Parse JSON responses
    data1 = response1.json()
    data2 = response2.json()
    
    # Responses should be identical
    json1 = json.dumps(data1, sort_keys=True)
    json2 = json.dumps(data2, sort_keys=True)
    
    assert json1 == json2, "Product detail responses must be identical across calls"


def test_all_listings_have_price_history(demo_client, demo_db_path):
    """Test that every listing returned in product detail has price history."""
    # Get all products
    products_response = demo_client.get("/api/products?page_size=100")
    assert products_response.status_code == 200
    products = products_response.json()["products"]
    
    assert len(products) > 0, "Test requires at least one product"
    
    # For each product, check that all listings have price history
    for product in products:
        product_id = product["product_id"]
        
        # Get product detail
        detail_response = demo_client.get(f"/api/products/{product_id}")
        assert detail_response.status_code == 200
        detail_data = detail_response.json()
        
        listings = detail_data["listings"]
        assert len(listings) > 0, f"Product {product_id} should have listings"
        
        # Check each listing has price history points
        for listing in listings:
            listing_id = listing["listing_id"]
            
            # Get price history
            history_response = demo_client.get(f"/api/listings/{listing_id}/price-history")
            assert history_response.status_code == 200
            history_data = history_response.json()
            
            # Every listing must have at least 1 price snapshot
            assert len(history_data["points"]) >= 1, (
                f"Listing {listing_id} (retailer: {listing.get('retailer_name')}) "
                f"must have at least 1 price snapshot, but has {len(history_data['points'])}"
            )


def test_no_listings_with_zero_snapshots(demo_db_path):
    """Test that the demo database has zero listings with 0 snapshots."""
    cfg = DbConfig(path=demo_db_path)
    with db_conn(cfg) as conn:
        # Count listings with zero snapshots
        result = conn.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM listings l
            LEFT JOIN price_snapshots ps ON l.id = ps.listing_id
            WHERE ps.id IS NULL
            """
        ).fetchone()
        
        listings_with_zero = int(result["cnt"])
        
        assert listings_with_zero == 0, (
            f"Demo database must have 0 listings with 0 snapshots, "
            f"but found {listings_with_zero}"
        )


def test_all_listings_have_minimum_snapshots(demo_db_path):
    """Test that all listings have at least the expected number of snapshots."""
    expected_min = 24  # Default snapshot_count
    
    cfg = DbConfig(path=demo_db_path)
    with db_conn(cfg) as conn:
        # Get minimum snapshot count per listing
        result = conn.execute(
            """
            SELECT MIN(cnt) AS min_cnt
            FROM (
                SELECT listing_id, COUNT(*) AS cnt
                FROM price_snapshots
                GROUP BY listing_id
            )
            """
        ).fetchone()
        
        min_snapshots = int(result["min_cnt"])
        
        assert min_snapshots >= expected_min, (
            f"All listings must have at least {expected_min} snapshots, "
            f"but minimum is {min_snapshots}"
        )


def test_overview_endpoint_identical_responses(demo_client):
    """Test that GET /api/overview returns identical responses on multiple calls."""
    # Call endpoint twice
    response1 = demo_client.get("/api/overview")
    response2 = demo_client.get("/api/overview")
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Parse JSON responses
    data1 = response1.json()
    data2 = response2.json()
    
    # Responses should be identical
    json1 = json.dumps(data1, sort_keys=True)
    json2 = json.dumps(data2, sort_keys=True)
    
    assert json1 == json2, "Overview responses must be identical across calls"


def test_listing_price_history_identical_responses(demo_client):
    """Test that GET /api/listings/{id}/price-history returns identical responses."""
    # Get a listing ID
    products_response = demo_client.get("/api/products?page_size=1")
    assert products_response.status_code == 200
    products = products_response.json()["products"]
    
    if len(products) == 0:
        pytest.skip("No products in database")
    
    product_id = products[0]["product_id"]
    detail_response = demo_client.get(f"/api/products/{product_id}")
    listings = detail_response.json()["listings"]
    
    if len(listings) == 0:
        pytest.skip("No listings for product")
    
    listing_id = listings[0]["listing_id"]
    
    # Call price history endpoint twice
    response1 = demo_client.get(f"/api/listings/{listing_id}/price-history")
    response2 = demo_client.get(f"/api/listings/{listing_id}/price-history")
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Parse JSON responses
    data1 = response1.json()
    data2 = response2.json()
    
    # Responses should be identical
    json1 = json.dumps(data1, sort_keys=True)
    json2 = json.dumps(data2, sort_keys=True)
    
    assert json1 == json2, "Price history responses must be identical across calls"

