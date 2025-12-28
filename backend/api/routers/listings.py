"""Listings endpoints."""
from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from backend.api.dependencies import get_db_conn
from backend.api.schemas.listings import PriceHistoryResponse, PricePoint
from backend.db import init_schema

router = APIRouter()


@router.get("/api/listings/{listing_id}/price-history", response_model=PriceHistoryResponse)
def get_listing_price_history(
    listing_id: int = Path(..., ge=1),
    limit: int = Query(default=200, ge=1, le=500),
    conn: sqlite3.Connection = Depends(get_db_conn),
) -> PriceHistoryResponse:
    """
    Get price history for a specific listing.
    
    Args:
        listing_id: Listing ID
        limit: Maximum number of points to return (1-500)
        conn: Database connection (injected)
        
    Returns:
        Price history with timestamps and prices
        
    Raises:
        HTTPException: 404 if listing not found
    """
    try:
        # Skip init_schema for read-only demo DB - schema is already initialized
        # This avoids potential locking issues with concurrent requests
        # init_schema(conn)
        
        # Check if listing exists
        cursor = conn.execute("SELECT id FROM listings WHERE id = ?", (listing_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Listing not found")
        
        # Fetch price snapshots ordered by timestamp
        cursor = conn.execute(
            """
            SELECT captured_at, price_cents
            FROM price_snapshots
            WHERE listing_id = ?
            ORDER BY captured_at ASC
            LIMIT ?
            """,
            (listing_id, limit),
        )
        
        rows = cursor.fetchall()
        
        # Build points list with explicit type conversion to ensure Pydantic validation succeeds
        points = [
            PricePoint(
                ts=str(row["captured_at"]),
                price_cents=int(row["price_cents"])
            )
            for row in rows
        ]
        
        return PriceHistoryResponse(listing_id=listing_id, points=points)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"ERROR in get_listing_price_history for listing {listing_id}: {e}"
        print(error_msg)
        traceback.print_exc()
        # Return a more detailed error in development
        import os
        if os.getenv("DEBUG", "false").lower() == "true":
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
        else:
            raise HTTPException(status_code=500, detail="Internal server error")

