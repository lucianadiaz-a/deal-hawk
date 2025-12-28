"""Schemas for overview/dashboard endpoint."""
from __future__ import annotations

from pydantic import BaseModel


class MetricsSchema(BaseModel):
    """Aggregated metrics for dashboard overview."""
    total_products: int
    total_listings: int
    active_alerts: int
    near_misses: int


class AlertItemSchema(BaseModel):
    """Alert event for dashboard feed."""
    listing_id: int
    product_id: int
    product_name: str
    retailer_name: str
    delta_pct: float
    prev_price_cents: int
    new_price_cents: int
    triggered_at: str


class NearMissItemSchema(BaseModel):
    """Near-miss listing (price drop but not enough for alert)."""
    listing_id: int
    product_id: int
    product_name: str
    retailer_name: str
    delta_pct: float
    current_price_cents: int


class OverviewResponse(BaseModel):
    """Response for GET /api/overview."""
    metrics: MetricsSchema
    recent_alerts: list[AlertItemSchema]
    near_misses: list[NearMissItemSchema]


