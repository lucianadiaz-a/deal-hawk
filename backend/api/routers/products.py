"""Products endpoints."""
from __future__ import annotations

import sqlite3
from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from backend.api.dependencies import get_db_conn
from backend.api.schemas.alerts import AlertEventItem, AlertHistoryResponse
from backend.api.schemas.products import (
    ProductDetailResponse,
    ProductsListResponse,
)
from backend.db import init_schema
from backend.services.dashboard import get_product_detail, list_products

router = APIRouter()


@router.get("/api/products", response_model=ProductsListResponse)
def get_products(
    window_hours: int = Query(default=6, ge=1, le=168),
    threshold_pct: float = Query(default=10.0, ge=0.0, le=100.0),
    brand: Optional[str] = Query(default=None),
    delta_min: Optional[float] = Query(default=None),
    delta_max: Optional[float] = Query(default=None),
    sort: str = Query(default="delta_desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    conn: sqlite3.Connection = Depends(get_db_conn),
) -> ProductsListResponse:
    """
    Get paginated list of products with filters and sorting.
    
    Args:
        window_hours: Time window for price deltas (1-168 hours)
        threshold_pct: Alert threshold percentage (0-100)
        brand: Filter by brand (optional)
        delta_min: Minimum delta percentage (optional)
        delta_max: Maximum delta percentage (optional)
        sort: Sort key (delta_desc, delta_asc, name, price_asc)
        page: Page number (1-indexed)
        page_size: Items per page (1-200)
        conn: Database connection (injected)
        
    Returns:
        Paginated product list with metadata
    """
    init_schema(conn)
    
    # Build filters dict as expected by service
    filters = {
        "brand": brand,
        "delta_min": delta_min,
        "delta_max": delta_max,
    }
    
    # Get paginated results
    products = list_products(
        conn,
        filters=filters,
        sort=sort,
        page=page,
        page_size=page_size,
        window_hours=window_hours,
        threshold_pct=threshold_pct,
    )
    
    # Compute total count by fetching all matching products
    # (POC scale: acceptable for small dataset, optimize later if needed)
    all_products = list_products(
        conn,
        filters=filters,
        sort=sort,
        page=1,
        page_size=10000,  # Large enough to get all results
        window_hours=window_hours,
        threshold_pct=threshold_pct,
    )
    total = len(all_products)
    
    return ProductsListResponse(
        products=[asdict(p) for p in products],
        pagination={
            "page": page,
            "page_size": page_size,
            "total": total,
        },
    )


@router.get("/api/products/{product_id}", response_model=ProductDetailResponse)
def get_product_by_id(
    product_id: int = Path(..., ge=1),
    window_hours: int = Query(default=6, ge=1, le=168),
    threshold_pct: float = Query(default=10.0, ge=0.0, le=100.0),
    conn: sqlite3.Connection = Depends(get_db_conn),
) -> ProductDetailResponse:
    """
    Get detailed product information with all retailer listings.
    
    Args:
        product_id: Product ID
        window_hours: Time window for price deltas (1-168 hours)
        threshold_pct: Alert threshold percentage (0-100)
        conn: Database connection (injected)
        
    Returns:
        Product detail with listings across retailers
        
    Raises:
        HTTPException: 404 if product not found
    """
    init_schema(conn)
    
    product_name, brand, listings = get_product_detail(
        conn,
        product_id=product_id,
        window_hours=window_hours,
        threshold_pct=threshold_pct,
    )
    
    # Check if product exists (service returns "Unknown Product" for missing)
    if product_name == "Unknown Product":
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductDetailResponse(
        product_id=product_id,
        product_name=product_name,
        brand=brand,
        listings=[asdict(listing) for listing in listings],
    )


@router.get("/api/products/{product_id}/alert-history", response_model=AlertHistoryResponse)
def get_product_alert_history(
    product_id: int = Path(..., ge=1),
    limit: int = Query(default=100, ge=1, le=500),
    conn: sqlite3.Connection = Depends(get_db_conn),
) -> AlertHistoryResponse:
    """
    Get alert history for a specific product across all retailers.
    
    Args:
        product_id: Product ID
        limit: Maximum number of events to return (1-500)
        conn: Database connection (injected)
        
    Returns:
        Alert history with event details
        
    Raises:
        HTTPException: 404 if product not found
    """
    init_schema(conn)
    
    # Check if product exists
    cursor = conn.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Fetch alert events for this product across all retailers
    cursor = conn.execute(
        """
        SELECT 
            ae.id as alert_event_id,
            ae.listing_id,
            r.name as retailer_name,
            CAST((ae.new_price_cents - ae.prev_price_cents) * 100.0 / ae.prev_price_cents AS REAL) as delta_pct,
            ae.prev_price_cents,
            ae.new_price_cents,
            ae.triggered_at,
            ae.rule_name
        FROM alert_events ae
        JOIN listings l ON ae.listing_id = l.id
        JOIN retailers r ON l.retailer_id = r.id
        WHERE l.product_id = ?
        ORDER BY ae.triggered_at DESC
        LIMIT ?
        """,
        (product_id, limit),
    )
    
    events = [
        AlertEventItem(
            alert_event_id=row[0],
            listing_id=row[1],
            retailer_name=row[2],
            delta_pct=row[3],
            prev_price_cents=row[4],
            new_price_cents=row[5],
            triggered_at=row[6],
            rule_name=row[7],
        )
        for row in cursor.fetchall()
    ]
    
    return AlertHistoryResponse(product_id=product_id, events=events)
