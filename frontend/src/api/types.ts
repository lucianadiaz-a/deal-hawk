/**
 * TypeScript types matching the FastAPI response schemas from PR1.
 */

export interface MetricsSchema {
  total_products: number;
  total_listings: number;
  active_alerts: number;
  near_misses: number;
}

export interface AlertItemSchema {
  listing_id: number;
  product_id: number;
  product_name: string;
  retailer_name: string;
  delta_pct: number;
  prev_price_cents: number;
  new_price_cents: number;
  triggered_at: string;
}

export interface NearMissItemSchema {
  listing_id: number;
  product_id: number;
  product_name: string;
  retailer_name: string;
  delta_pct: number;
  current_price_cents: number;
}

export interface OverviewResponse {
  metrics: MetricsSchema;
  recent_alerts: AlertItemSchema[];
  near_misses: NearMissItemSchema[];
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
}

export interface ProductCardSchema {
  product_id: number;
  product_name: string;
  brand: string | null;
  lowest_price_cents: number | null;
  lowest_price_retailer: string | null;
  lowest_price_listing_id: number | null;
  best_delta_pct: number | null;
  alert_status: string;
  listing_count: number;
}

export interface ProductsListResponse {
  products: ProductCardSchema[];
  pagination: PaginationMeta;
}

export interface ProductListingDetailSchema {
  listing_id: number;
  retailer_name: string;
  current_price_cents: number | null;
  delta_cents: number | null;
  delta_pct: number | null;
  alert_status: string;
  url: string;
}

export interface ProductDetailResponse {
  product_id: number;
  product_name: string;
  brand: string | null;
  listings: ProductListingDetailSchema[];
}

export interface PricePoint {
  ts: string;  // ISO 8601 timestamp
  price_cents: number;
}

export interface PriceHistoryResponse {
  listing_id: number;
  points: PricePoint[];
}

export interface AlertEventItem {
  alert_event_id: number;
  listing_id: number;
  retailer_name: string;
  delta_pct: number;
  prev_price_cents: number;
  new_price_cents: number;
  triggered_at: string;  // ISO 8601 timestamp
  rule_name: string;
}

export interface AlertHistoryResponse {
  product_id: number;
  events: AlertEventItem[];
}

