"""Schemas for listings endpoints."""
from __future__ import annotations

from pydantic import BaseModel


class PricePoint(BaseModel):
    """Single price snapshot point."""
    ts: str  # ISO 8601 timestamp
    price_cents: int


class PriceHistoryResponse(BaseModel):
    """Response for GET /api/listings/{listing_id}/price-history."""
    listing_id: int
    points: list[PricePoint]

