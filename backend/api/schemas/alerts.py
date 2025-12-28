"""Schemas for alerts endpoints."""
from __future__ import annotations

from pydantic import BaseModel


class AlertEventItem(BaseModel):
    """Single alert event item."""
    alert_event_id: int
    listing_id: int
    retailer_name: str
    delta_pct: float
    prev_price_cents: int
    new_price_cents: int
    triggered_at: str  # ISO 8601 timestamp
    rule_name: str


class AlertHistoryResponse(BaseModel):
    """Response for GET /api/products/{product_id}/alert-history."""
    product_id: int
    events: list[AlertEventItem]

