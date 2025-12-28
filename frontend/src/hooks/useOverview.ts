import { useState, useEffect, useCallback, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { fetchOverview } from '../api/endpoints';
import { normalizeWindowThreshold, setNumberParam } from '../lib/query';
import type { OverviewResponse } from '../api/types';

export function useOverview() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { window_hours, threshold_pct } = normalizeWindowThreshold(searchParams);
  
  const [data, setData] = useState<OverviewResponse | null>(null);
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
      const result = await fetchOverview(window_hours, threshold_pct);
      setData(result);
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        setError((err as Error).message);
      }
    } finally {
      setIsLoading(false);
    }
  }, [window_hours, threshold_pct]);

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

  const setWindowHours = useCallback((value: number) => {
    const newParams = new URLSearchParams(searchParams);
    setNumberParam(newParams, 'window_hours', value);
    setSearchParams(newParams);
  }, [searchParams, setSearchParams]);

  const setThresholdPct = useCallback((value: number) => {
    const newParams = new URLSearchParams(searchParams);
    setNumberParam(newParams, 'threshold_pct', value);
    setSearchParams(newParams);
  }, [searchParams, setSearchParams]);

  return {
    data,
    isLoading,
    error,
    windowHours: window_hours,
    thresholdPct: threshold_pct,
    setWindowHours,
    setThresholdPct,
    refetch,
  };
}

