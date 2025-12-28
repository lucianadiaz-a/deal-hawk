"""Schemas for products endpoints."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from backend.api.schemas.common import PaginationMeta


class ProductCardSchema(BaseModel):
    """Product summary card for grid view."""
    product_id: int
    product_name: str
    brand: Optional[str]
    lowest_price_cents: Optional[int]
    lowest_price_retailer: Optional[str]
    lowest_price_listing_id: Optional[int]
    best_delta_pct: Optional[float]
    alert_status: str
    listing_count: int


class ProductsListResponse(BaseModel):
    """Response for GET /api/products."""
    products: list[ProductCardSchema]
    pagination: PaginationMeta


class ProductListingDetailSchema(BaseModel):
    """Individual listing detail for a product across retailers."""
    listing_id: int
    retailer_name: str
    current_price_cents: Optional[int]
    delta_cents: Optional[int]
    delta_pct: Optional[float]
    alert_status: str
    url: str


class ProductDetailResponse(BaseModel):
    """Response for GET /api/products/{product_id}."""
    product_id: int
    product_name: str
    brand: Optional[str]
    listings: list[ProductListingDetailSchema]


