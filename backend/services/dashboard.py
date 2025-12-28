"""
View-model service layer for dashboard UI.
Provides clean, UI-ready data structures for the dashboard page.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional

from backend.services.pricing import ListingPriceSummary, get_listing_price_summary


@dataclass(frozen=True)
class OverviewMetrics:
    """Aggregated metrics for dashboard overview."""
    total_products: int
    total_listings: int
    active_alerts: int
    near_misses: int  # Listings with delta close to threshold


@dataclass(frozen=True)
class AlertFeedItem:
    """Alert event for dashboard feed."""
    listing_id: int
    product_id: int
    product_name: str
    retailer_name: str
    delta_pct: float
    prev_price_cents: int
    new_price_cents: int
    triggered_at: str


@dataclass(frozen=True)
class NearMissFeedItem:
    """Near-miss listing (price drop but not enough for alert)."""
    listing_id: int
    product_id: int
    product_name: str
    retailer_name: str
    delta_pct: float
    current_price_cents: int


@dataclass(frozen=True)
class ProductCard:
    """Product summary for dashboard card grid (product-centric view)."""
    product_id: int
    product_name: str
    brand: Optional[str]
    lowest_price_cents: Optional[int]
    lowest_price_retailer: Optional[str]
    lowest_price_listing_id: Optional[int]
    best_delta_pct: Optional[float]  # Most negative delta across retailers
    alert_status: str  # "alert", "watch", "ok", "muted"
    listing_count: int  # Number of retailers tracking this product


@dataclass(frozen=True)
class ProductListingDetail:
    """Individual listing detail for a product across retailers."""
    listing_id: int
    retailer_name: str
    current_price_cents: Optional[int]
    delta_cents: Optional[int]
    delta_pct: Optional[float]
    alert_status: str
    url: str


def get_overview(
    conn: sqlite3.Connection,
    window_hours: int = 6,
    threshold_pct: float = 10.0,
) -> tuple[OverviewMetrics, list[AlertFeedItem], list[NearMissFeedItem]]:
    """
    Get overview metrics, recent alerts, and near-miss listings.
    
    Args:
        conn: Database connection
        window_hours: Time window for price deltas
        threshold_pct: Alert threshold percentage
        
    Returns:
        Tuple of (metrics, recent_alerts, near_misses)
    """
    # Compute metrics
    total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    total_listings = conn.execute(
        "SELECT COUNT(*) FROM listings WHERE active = 1"
    ).fetchone()[0]
    
    # Active alerts: count distinct listings with alerts in last 24h
    active_alerts = conn.execute(
        """
        SELECT COUNT(DISTINCT listing_id)
        FROM alert_events
        WHERE triggered_at >= datetime('now', '-24 hours')
        """
    ).fetchone()[0]
    
    # Recent alerts feed (last 10)
    alert_rows = conn.execute(
        """
        SELECT
            ae.listing_id,
            l.product_id,
            p.name AS product_name,
            r.name AS retailer_name,
            ae.prev_price_cents,
            ae.new_price_cents,
            ae.triggered_at
        FROM alert_events ae
        JOIN listings l ON l.id = ae.listing_id
        JOIN products p ON p.id = l.product_id
        JOIN retailers r ON r.id = l.retailer_id
        ORDER BY ae.triggered_at DESC, ae.id DESC
        LIMIT 10
        """
    ).fetchall()
    
    recent_alerts = []
    for row in alert_rows:
        prev_cents = int(row["prev_price_cents"])
        new_cents = int(row["new_price_cents"])
        delta_pct = ((new_cents - prev_cents) / prev_cents * 100.0) if prev_cents != 0 else 0.0
        
        recent_alerts.append(
            AlertFeedItem(
                listing_id=int(row["listing_id"]),
                product_id=int(row["product_id"]),
                product_name=str(row["product_name"]),
                retailer_name=str(row["retailer_name"]),
                delta_pct=delta_pct,
                prev_price_cents=prev_cents,
                new_price_cents=new_cents,
                triggered_at=str(row["triggered_at"]),
            )
        )
    
    # Near-misses: listings with -5% to -threshold% delta (not quite alert-worthy)
    # TODO: Replace with real computation using list_price_summaries
    near_miss_threshold_low = threshold_pct * 0.5
    
    listing_ids = conn.execute(
        "SELECT id FROM listings WHERE active = 1 ORDER BY id"
    ).fetchall()
    
    near_misses = []
    near_miss_count = 0
    for row in listing_ids[:20]:  # Limit scan for POC performance
        listing_id = int(row["id"])
        try:
            summary = get_listing_price_summary(conn, listing_id, window_hours=window_hours)
            if (
                summary.delta_pct is not None
                and summary.current_price_cents is not None
                and -threshold_pct < summary.delta_pct <= -near_miss_threshold_low
            ):
                near_miss_count += 1
                if len(near_misses) < 10:  # Only return top 10 for feed
                    # Get product_id from listing
                    product_id_row = conn.execute(
                        "SELECT product_id FROM listings WHERE id = ?", (listing_id,)
                    ).fetchone()
                    product_id = int(product_id_row["product_id"]) if product_id_row else 0
                    
                    near_misses.append(
                        NearMissFeedItem(
                            listing_id=listing_id,
                            product_id=product_id,
                            product_name=summary.product_name,
                            retailer_name=summary.retailer_name,
                            delta_pct=summary.delta_pct,
                            current_price_cents=summary.current_price_cents,
                        )
                    )
        except ValueError:
            continue
    
    metrics = OverviewMetrics(
        total_products=total_products,
        total_listings=total_listings,
        active_alerts=active_alerts,
        near_misses=near_miss_count,
    )
    
    return metrics, recent_alerts, near_misses


def list_products(
    conn: sqlite3.Connection,
    filters: dict,
    sort: str = "delta_desc",
    page: int = 1,
    page_size: int = 20,
    window_hours: int = 6,
    threshold_pct: float = 10.0,
) -> list[ProductCard]:
    """
    Get paginated list of products (grouped by product, showing lowest price across retailers).
    
    Args:
        conn: Database connection
        filters: Filter dict with optional keys: "brand", "delta_min", "delta_max"
        sort: Sort key ("delta_desc", "delta_asc", "name", "price_asc")
        page: Page number (1-indexed)
        page_size: Items per page
        window_hours: Time window for price deltas
        threshold_pct: Alert threshold for status classification
        
    Returns:
        List of ProductCard items for the current page
    """
    # Build query with filters
    where_clauses = ["l.active = 1"]
    params = []
    
    if filters.get("brand"):
        where_clauses.append("p.brand = ?")
        params.append(filters["brand"])
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Get all products with their listings
    product_rows = conn.execute(
        f"""
        SELECT DISTINCT p.id AS product_id, p.name AS product_name, p.brand
        FROM products p
        JOIN listings l ON l.product_id = p.id
        WHERE {where_sql}
        ORDER BY p.name
        """,
        params,
    ).fetchall()
    
    # Build product cards
    cards = []
    for prod_row in product_rows:
        product_id = int(prod_row["product_id"])
        product_name = str(prod_row["product_name"])
        brand = prod_row["brand"] if prod_row["brand"] else None
        
        # Get all listings for this product
        listing_rows = conn.execute(
            """
            SELECT l.id, r.name AS retailer_name
            FROM listings l
            JOIN retailers r ON r.id = l.retailer_id
            WHERE l.product_id = ? AND l.active = 1
            ORDER BY l.id
            """,
            (product_id,),
        ).fetchall()
        
        if not listing_rows:
            continue
        
        # Collect pricing data for all listings
        listing_summaries = []
        for listing_row in listing_rows:
            listing_id = int(listing_row["id"])
            try:
                summary = get_listing_price_summary(conn, listing_id, window_hours=window_hours)
                if summary.current_price_cents is not None:
                    listing_summaries.append({
                        "listing_id": listing_id,
                        "retailer_name": str(listing_row["retailer_name"]),
                        "price_cents": summary.current_price_cents,
                        "delta_pct": summary.delta_pct,
                    })
            except ValueError:
                continue
        
        if not listing_summaries:
            continue
        
        # Find lowest price and best (most negative) delta
        lowest = min(listing_summaries, key=lambda x: x["price_cents"])
        best_delta = min(
            (ls["delta_pct"] for ls in listing_summaries if ls["delta_pct"] is not None),
            default=None,
        )
        
        # Determine alert status based on best delta
        # Price drops are GOOD (green), price increases are BAD (red)
        alert_status = "muted"
        if best_delta is not None:
            if best_delta <= -threshold_pct:
                alert_status = "ok"  # >= 10% drop = GOOD (green)
            elif best_delta <= -threshold_pct * 0.7:
                alert_status = "watch"  # 7-10% drop (near miss, yellow)
            elif best_delta >= threshold_pct:
                alert_status = "alert"  # >= 10% increase = BAD (red)
            elif best_delta < -2.0:  # Any drop > 2%
                alert_status = "ok"  # 2-7% drop (small but visible, green)
            # else: muted (small changes or moderate increases)
        
        # Apply delta filters
        if filters.get("delta_min") is not None:
            if best_delta is None or best_delta < filters["delta_min"]:
                continue
        if filters.get("delta_max") is not None:
            if best_delta is None or best_delta > filters["delta_max"]:
                continue
        
        cards.append(
            ProductCard(
                product_id=product_id,
                product_name=product_name,
                brand=brand,
                lowest_price_cents=lowest["price_cents"],
                lowest_price_retailer=lowest["retailer_name"],
                lowest_price_listing_id=lowest["listing_id"],
                best_delta_pct=best_delta,
                alert_status=alert_status,
                listing_count=len(listing_summaries),
            )
        )
    
    # Sort
    if sort == "delta_desc":
        cards.sort(key=lambda c: c.best_delta_pct if c.best_delta_pct is not None else 0.0)
    elif sort == "delta_asc":
        cards.sort(key=lambda c: c.best_delta_pct if c.best_delta_pct is not None else 0.0, reverse=True)
    elif sort == "name":
        cards.sort(key=lambda c: c.product_name.lower())
    elif sort == "price_asc":
        cards.sort(key=lambda c: c.lowest_price_cents if c.lowest_price_cents is not None else float('inf'))
    
    # Paginate
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    return cards[start_idx:end_idx]


def get_product_detail(
    conn: sqlite3.Connection,
    product_id: int,
    window_hours: int = 6,
    threshold_pct: float = 10.0,
) -> tuple[str, Optional[str], list[ProductListingDetail]]:
    """
    Get detailed product information with all retailer listings.
    
    Args:
        conn: Database connection
        product_id: Product ID
        window_hours: Time window for price deltas
        threshold_pct: Alert threshold for status classification
        
    Returns:
        Tuple of (product_name, brand, list of listing details)
    """
    # Get product info
    product_row = conn.execute(
        "SELECT name, brand FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()
    
    if not product_row:
        return ("Unknown Product", None, [])
    
    product_name = str(product_row["name"])
    brand = product_row["brand"] if product_row["brand"] else None
    
    # Get all listings for this product
    listing_rows = conn.execute(
        """
        SELECT l.id, l.url, r.name AS retailer_name
        FROM listings l
        JOIN retailers r ON r.id = l.retailer_id
        WHERE l.product_id = ? AND l.active = 1
        ORDER BY r.name
        """,
        (product_id,),
    ).fetchall()
    
    listing_details = []
    for row in listing_rows:
        listing_id = int(row["id"])
        try:
            summary = get_listing_price_summary(conn, listing_id, window_hours=window_hours)
            
            # Determine alert status
            # Price drops are GOOD (green), price increases are BAD (red)
            alert_status = "muted"
            if summary.delta_pct is not None:
                if summary.delta_pct <= -threshold_pct:
                    alert_status = "ok"  # >= 10% drop = GOOD (green)
                elif summary.delta_pct <= -threshold_pct * 0.7:
                    alert_status = "watch"  # 7-10% drop (near miss, yellow)
                elif summary.delta_pct >= threshold_pct:
                    alert_status = "alert"  # >= 10% increase = BAD (red)
                elif summary.delta_pct < -2.0:  # Any drop > 2%
                    alert_status = "ok"  # 2-7% drop (small but visible, green)
                # else: muted (small changes or moderate increases)
            
            listing_details.append(
                ProductListingDetail(
                    listing_id=listing_id,
                    retailer_name=str(row["retailer_name"]),
                    current_price_cents=summary.current_price_cents,
                    delta_cents=summary.delta_cents,
                    delta_pct=summary.delta_pct,
                    alert_status=alert_status,
                    url=str(row["url"]),
                )
            )
        except ValueError:
            continue
    
    return (product_name, brand, listing_details)

