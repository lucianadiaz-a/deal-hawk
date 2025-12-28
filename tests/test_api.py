"""Tests for FastAPI endpoints."""
from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient

from backend.api.main import app
from backend.db import db_conn, init_schema
from backend.services.seed import seed_from_json

# Create test client
client = TestClient(app)

# Ensure test database is seeded
SEED_PATH = Path(__file__).parent.parent / "data" / "seed_listings.json"


def setup_test_data() -> None:
    """Ensure test database has seed data."""
    with db_conn() as conn:
        init_schema(conn)
        # Check if data exists
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            # Seed if empty
            seed_from_json(conn, SEED_PATH)


# Run setup once at module load
setup_test_data()


def test_health_check():
    """Test GET /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_root_endpoint():
    """Test GET / root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_overview_endpoint():
    """Test GET /api/overview endpoint."""
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    
    # Validate structure
    assert "metrics" in data
    assert "recent_alerts" in data
    assert "near_misses" in data
    
    # Validate metrics keys
    metrics = data["metrics"]
    assert "total_products" in metrics
    assert "total_listings" in metrics
    assert "active_alerts" in metrics
    assert "near_misses" in metrics
    
    # Validate types
    assert isinstance(metrics["total_products"], int)
    assert isinstance(data["recent_alerts"], list)
    assert isinstance(data["near_misses"], list)


def test_overview_with_params():
    """Test GET /api/overview with query parameters."""
    response = client.get("/api/overview?window_hours=12&threshold_pct=15.0")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data


def test_products_list_endpoint():
    """Test GET /api/products endpoint."""
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    
    # Validate structure
    assert "products" in data
    assert "pagination" in data
    
    # Validate pagination
    pagination = data["pagination"]
    assert "page" in pagination
    assert "page_size" in pagination
    assert "total" in pagination
    assert pagination["page"] == 1
    assert pagination["page_size"] == 50
    
    # Validate products
    products = data["products"]
    assert isinstance(products, list)
    if len(products) > 0:
        product = products[0]
        assert "product_id" in product
        assert "product_name" in product
        assert "alert_status" in product
        assert "listing_count" in product


def test_products_with_filters():
    """Test GET /api/products with filter parameters."""
    response = client.get(
        "/api/products?brand=Apple&sort=name&page=1&page_size=10"
    )
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert data["pagination"]["page_size"] == 10


def test_products_pagination():
    """Test GET /api/products pagination."""
    # Get first page
    response1 = client.get("/api/products?page=1&page_size=5")
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Get second page
    response2 = client.get("/api/products?page=2&page_size=5")
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Validate different results (if enough products exist)
    if data1["pagination"]["total"] > 5:
        assert data1["products"] != data2["products"]


def test_product_detail_endpoint():
    """Test GET /api/products/{product_id} endpoint."""
    # First, get a valid product ID
    response = client.get("/api/products?page_size=1")
    assert response.status_code == 200
    products = response.json()["products"]
    
    if len(products) > 0:
        product_id = products[0]["product_id"]
        
        # Get product detail
        detail_response = client.get(f"/api/products/{product_id}")
        assert detail_response.status_code == 200
        data = detail_response.json()
        
        # Validate structure
        assert "product_id" in data
        assert "product_name" in data
        assert "brand" in data
        assert "listings" in data
        assert data["product_id"] == product_id
        
        # Validate listings
        assert isinstance(data["listings"], list)
        if len(data["listings"]) > 0:
            listing = data["listings"][0]
            assert "listing_id" in listing
            assert "retailer_name" in listing
            assert "alert_status" in listing
            assert "url" in listing


def test_product_detail_not_found():
    """Test GET /api/products/{product_id} with non-existent ID."""
    response = client.get("/api/products/999999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_product_detail_with_params():
    """Test GET /api/products/{product_id} with query parameters."""
    # Get a valid product ID
    response = client.get("/api/products?page_size=1")
    products = response.json()["products"]
    
    if len(products) > 0:
        product_id = products[0]["product_id"]
        
        # Get detail with custom params
        detail_response = client.get(
            f"/api/products/{product_id}?window_hours=12&threshold_pct=15.0"
        )
        assert detail_response.status_code == 200


def test_invalid_query_params():
    """Test endpoints with invalid query parameters."""
    # Invalid page (< 1)
    response = client.get("/api/products?page=0")
    assert response.status_code == 422  # Validation error
    
    # Invalid page_size (> 200)
    response = client.get("/api/products?page_size=999")
    assert response.status_code == 422
    
    # Invalid window_hours (> 168)
    response = client.get("/api/overview?window_hours=200")
    assert response.status_code == 422


def test_listing_price_history():
    """Test GET /api/listings/{listing_id}/price-history endpoint."""
    # Get a valid listing ID from a product
    response = client.get("/api/products?page_size=1")
    assert response.status_code == 200
    products = response.json()["products"]
    
    if len(products) > 0:
        product_id = products[0]["product_id"]
        
        # Get product detail to get listing ID
        detail_response = client.get(f"/api/products/{product_id}")
        listings = detail_response.json()["listings"]
        
        if len(listings) > 0:
            listing_id = listings[0]["listing_id"]
            
            # Get price history
            history_response = client.get(f"/api/listings/{listing_id}/price-history")
            assert history_response.status_code == 200
            data = history_response.json()
            
            # Validate structure
            assert "listing_id" in data
            assert "points" in data
            assert data["listing_id"] == listing_id
            assert isinstance(data["points"], list)
            
            # Validate points structure if any exist
            if len(data["points"]) > 0:
                point = data["points"][0]
                assert "ts" in point
                assert "price_cents" in point
                assert isinstance(point["price_cents"], int)


def test_listing_price_history_with_limit():
    """Test GET /api/listings/{listing_id}/price-history with limit parameter."""
    # Get a valid listing ID
    response = client.get("/api/products?page_size=1")
    products = response.json()["products"]
    
    if len(products) > 0:
        product_id = products[0]["product_id"]
        detail_response = client.get(f"/api/products/{product_id}")
        listings = detail_response.json()["listings"]
        
        if len(listings) > 0:
            listing_id = listings[0]["listing_id"]
            
            # Get history with limit
            history_response = client.get(f"/api/listings/{listing_id}/price-history?limit=10")
            assert history_response.status_code == 200
            data = history_response.json()
            assert len(data["points"]) <= 10


def test_listing_price_history_not_found():
    """Test GET /api/listings/{listing_id}/price-history with non-existent listing."""
    response = client.get("/api/listings/999999/price-history")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_product_alert_history():
    """Test GET /api/products/{product_id}/alert-history endpoint."""
    # Get a valid product ID
    response = client.get("/api/products?page_size=1")
    assert response.status_code == 200
    products = response.json()["products"]
    
    if len(products) > 0:
        product_id = products[0]["product_id"]
        
        # Get alert history
        history_response = client.get(f"/api/products/{product_id}/alert-history")
        assert history_response.status_code == 200
        data = history_response.json()
        
        # Validate structure
        assert "product_id" in data
        assert "events" in data
        assert data["product_id"] == product_id
        assert isinstance(data["events"], list)
        
        # Validate event structure if any exist
        if len(data["events"]) > 0:
            event = data["events"][0]
            assert "alert_event_id" in event
            assert "listing_id" in event
            assert "retailer_name" in event
            assert "delta_pct" in event
            assert "prev_price_cents" in event
            assert "new_price_cents" in event
            assert "triggered_at" in event
            assert "rule_name" in event


def test_product_alert_history_with_limit():
    """Test GET /api/products/{product_id}/alert-history with limit parameter."""
    # Get a valid product ID
    response = client.get("/api/products?page_size=1")
    products = response.json()["products"]
    
    if len(products) > 0:
        product_id = products[0]["product_id"]
        
        # Get history with limit
        history_response = client.get(f"/api/products/{product_id}/alert-history?limit=5")
        assert history_response.status_code == 200
        data = history_response.json()
        assert len(data["events"]) <= 5


def test_product_alert_history_not_found():
    """Test GET /api/products/{product_id}/alert-history with non-existent product."""
    response = client.get("/api/products/999999/alert-history")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_listing_price_history_no_500_regression():
    """
    Regression test: Ensure listing price-history endpoint never returns 500.
    
    This test verifies that for all listings returned by /api/products/{id},
    the price-history endpoint returns 200 (or 404 if listing doesn't exist),
    with a valid response structure, never a 500 error.
    """
    from backend.db import db_conn
    from backend.services.ingest import run_ingest_cycle
    
    # Ensure we have some price snapshots by running ingest if needed
    with db_conn() as conn:
        init_schema(conn)
        # Run ingest once to ensure we have price snapshots
        run_ingest_cycle(conn)
    
    # Get a product that has listings
    response = client.get("/api/products?page_size=10")
    assert response.status_code == 200
    products = response.json()["products"]
    
    assert len(products) > 0, "Test requires at least one product in database"
    
    # Test the first product that has listings
    for product in products:
        product_id = product["product_id"]
        
        # Get product detail to get all listings
        detail_response = client.get(f"/api/products/{product_id}")
        assert detail_response.status_code == 200
        detail_data = detail_response.json()
        listings = detail_data["listings"]
        
        if len(listings) == 0:
            continue  # Skip products with no listings
        
        # For each listing, test price-history endpoint
        for listing in listings:
            listing_id = listing["listing_id"]
            
            # This should NEVER return 500
            history_response = client.get(f"/api/listings/{listing_id}/price-history")
            
            # Should return either 200 (success) or 404 (listing not found in history table)
            # But NEVER 500
            assert history_response.status_code in (200, 404), (
                f"Expected 200 or 404, got {history_response.status_code} "
                f"for listing_id={listing_id}, product_id={product_id}. "
                f"Response: {history_response.text}"
            )
            
            if history_response.status_code == 200:
                data = history_response.json()
                # Validate response structure
                assert "listing_id" in data
                assert "points" in data
                assert data["listing_id"] == listing_id
                assert isinstance(data["points"], list)
                # Points can be empty (listing exists but has no snapshots)
        
        # Test at least one product with listings
        break

