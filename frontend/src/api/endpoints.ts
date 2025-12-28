/**
 * API endpoint functions for calling FastAPI backend.
 */

import { getJSON } from './client';
import type {
  OverviewResponse,
  ProductsListResponse,
  ProductDetailResponse,
  PriceHistoryResponse,
  AlertHistoryResponse,
} from './types';

/**
 * Fetch overview/dashboard data.
 * @param window_hours - Optional time window for price deltas
 * @param threshold_pct - Optional threshold for near-misses
 */
export async function fetchOverview(
  window_hours?: number,
  threshold_pct?: number
): Promise<OverviewResponse> {
  return getJSON<OverviewResponse>('/api/overview', {
    window_hours,
    threshold_pct,
  });
}

/**
 * Fetch products list with pagination and filters.
 */
export async function fetchProducts(params?: {
  page?: number;
  page_size?: number;
  alert_status?: string;
  brand?: string;
  delta_min?: number;
  delta_max?: number;
  sort?: string;
  window_hours?: number;
  threshold_pct?: number;
}): Promise<ProductsListResponse> {
  return getJSON<ProductsListResponse>('/api/products', params);
}

/**
 * Fetch product detail by ID.
 * @param product_id - Product ID
 * @param window_hours - Optional time window for price deltas
 * @param threshold_pct - Optional threshold for alerts
 */
export async function fetchProductDetail(
  product_id: number,
  window_hours?: number,
  threshold_pct?: number
): Promise<ProductDetailResponse> {
  return getJSON<ProductDetailResponse>(`/api/products/${product_id}`, {
    window_hours,
    threshold_pct,
  });
}

/**
 * Fetch price history for a specific listing.
 * @param listing_id - Listing ID
 * @param limit - Optional limit on number of points
 */
export async function fetchListingPriceHistory(
  listing_id: number,
  limit?: number
): Promise<PriceHistoryResponse> {
  return getJSON<PriceHistoryResponse>(`/api/listings/${listing_id}/price-history`, {
    limit,
  });
}

/**
 * Fetch alert history for a product.
 * @param product_id - Product ID
 * @param limit - Optional limit on number of events
 */
export async function fetchProductAlertHistory(
  product_id: number,
  limit?: number
): Promise<AlertHistoryResponse> {
  return getJSON<AlertHistoryResponse>(`/api/products/${product_id}/alert-history`, {
    limit,
  });
}

