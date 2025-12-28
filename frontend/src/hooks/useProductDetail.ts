import { useState, useEffect, useCallback, useRef } from 'react';
import {
  fetchProductDetail,
  fetchListingPriceHistory,
  fetchProductAlertHistory,
} from '../api/endpoints';
import type {
  ProductDetailResponse,
  PriceHistoryResponse,
  AlertHistoryResponse,
} from '../api/types';

export function useProductDetail(
  productId: number,
  windowHours: number = 24,
  thresholdPct: number = 10
) {
  const [detail, setDetail] = useState<ProductDetailResponse | null>(null);
  // Use string keys consistently to avoid key mismatch issues
  const [historiesByListingId, setHistoriesByListingId] = useState<
    Record<string, PriceHistoryResponse>
  >({});
  const [alertHistory, setAlertHistory] = useState<AlertHistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const requestIdRef = useRef(0);
  const abortControllerRef = useRef<AbortController | null>(null);
  const [refreshToken, setRefreshToken] = useState(0);

  useEffect(() => {
    const currentRequestId = ++requestIdRef.current;
    let cancelled = false;

    // Abort previous requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();

    setIsLoading(true);
    setError(null);

    const loadData = async () => {
      try {
        // Fetch product detail first
        const detailData = await fetchProductDetail(productId, windowHours, thresholdPct);
        
        // Check if this request is still current
        if (cancelled || currentRequestId !== requestIdRef.current) {
          return;
        }

        setDetail(detailData);

        // Extract listing IDs once from the detail response
        const listingIds = detailData.listings.map((listing) => listing.listing_id);

        // Fetch price history sequentially to avoid database locking issues
        // Sequential fetching is more reliable than parallel for SQLite
        const results: Array<PromiseSettledResult<{ listingId: number; history: PriceHistoryResponse }>> = [];
        for (const listingId of listingIds) {
          try {
            const history = await fetchListingPriceHistory(listingId, 200);
            results.push({ status: 'fulfilled', value: { listingId, history } });
            console.log(`Listing ${listingId}: loaded ${history.points.length} price points`);
          } catch (err) {
            console.error(`Failed to fetch history for listing ${listingId}:`, err);
            results.push({ 
              status: 'rejected', 
              reason: err 
            });
          }
        }

        // Check if this request is still current before setting state
        if (cancelled || currentRequestId !== requestIdRef.current) {
          return;
        }

        // Build histories map with string keys
        const historiesMap: Record<string, PriceHistoryResponse> = {};
        listingIds.forEach((listingId, index) => {
          const result = results[index];
          const key = String(listingId);
          if (result.status === 'fulfilled') {
            const { history } = result.value;
            // Debug logging
            if (!history || !history.points) {
              console.warn(`Listing ${listingId}: history missing or invalid`, history);
            } else {
              console.log(`Listing ${listingId}: loaded ${history.points.length} price points`);
            }
            historiesMap[key] = {
              listing_id: typeof history.listing_id === 'string' 
                ? parseInt(history.listing_id, 10) 
                : history.listing_id,
              points: Array.isArray(history.points) ? history.points : [],
            };
          } else {
            // Failed fetch - log error and store empty array
            console.error(`Listing ${listingId}: fetch failed:`, result.reason);
            historiesMap[key] = { listing_id: listingId, points: [] };
          }
        });
        
        console.log('Price histories loaded:', Object.keys(historiesMap).length, 'listings');
        
        // Set state ONCE with all results
        setHistoriesByListingId(historiesMap);

        // Fetch alert history
        const alertData = await fetchProductAlertHistory(productId, 100).catch(
          (err) => {
            console.warn(`Failed to fetch alert history for product ${productId}:`, err);
            return { product_id: productId, events: [] };
          }
        );
        
        // Check again before setting alert history
        if (cancelled || currentRequestId !== requestIdRef.current) {
          return;
        }
        
        setAlertHistory(alertData);
      } catch (err) {
        if (cancelled || currentRequestId !== requestIdRef.current) {
          return;
        }
        const error = err as Error;
        if (error.name !== 'AbortError') {
          setError(error.message);
        }
      } finally {
        if (!cancelled && currentRequestId === requestIdRef.current) {
          setIsLoading(false);
        }
      }
    };

    loadData();

    return () => {
      cancelled = true;
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [productId, windowHours, thresholdPct, refreshToken]);

  const refetch = useCallback(() => {
    // Trigger a new request by incrementing refresh token
    setRefreshToken((prev) => prev + 1);
  }, []);

  return {
    detail,
    historiesByListingId,
    alertHistory,
    isLoading,
    error,
    refetch,
  };
}

