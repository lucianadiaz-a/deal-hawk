import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchProducts } from '../api/endpoints';
import type { ProductsListResponse } from '../api/types';

interface UseProductsParams {
  brand?: string;
  delta_min?: number;
  delta_max?: number;
  sort?: string;
  page?: number;
  page_size?: number;
  window_hours?: number;
  threshold_pct?: number;
}

export function useProducts(params: UseProductsParams) {
  const [data, setData] = useState<ProductsListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const abortControllerRef = useRef<AbortController | null>(null);

  const loadData = useCallback(async () => {
    // Abort previous request if still pending
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    
    setIsLoading(true);
    setError(null);

    try {
      const result = await fetchProducts({
        brand: params.brand,
        delta_min: params.delta_min,
        delta_max: params.delta_max,
        sort: params.sort,
        page: params.page,
        page_size: params.page_size,
        window_hours: params.window_hours,
        threshold_pct: params.threshold_pct,
      });
      setData(result);
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        setError((err as Error).message);
      }
    } finally {
      setIsLoading(false);
    }
  }, [params.brand, params.delta_min, params.delta_max, params.sort, params.page, params.page_size, params.window_hours, params.threshold_pct]);

  useEffect(() => {
    loadData();
    
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [loadData]);

  const refetch = useCallback(() => {
    loadData();
  }, [loadData]);

  return {
    data,
    isLoading,
    error,
    refetch,
  };
}

