/**
 * Query parameter utilities for managing URL state.
 */

/**
 * Get a number parameter from URLSearchParams with default value.
 */
export function getNumberParam(
  searchParams: URLSearchParams,
  key: string,
  defaultValue: number
): number {
  const value = searchParams.get(key);
  if (value === null) {
    return defaultValue;
  }
  const parsed = Number(value);
  return isNaN(parsed) ? defaultValue : parsed;
}

/**
 * Set a number parameter in URLSearchParams (or remove if undefined/null).
 */
export function setNumberParam(
  searchParams: URLSearchParams,
  key: string,
  value: number | undefined | null
): void {
  if (value === undefined || value === null) {
    searchParams.delete(key);
  } else {
    searchParams.set(key, String(value));
  }
}

/**
 * Normalize and clamp window_hours and threshold_pct to valid ranges.
 * Returns normalized values with defaults.
 */
export function normalizeWindowThreshold(searchParams: URLSearchParams): {
  window_hours: number;
  threshold_pct: number;
} {
  let window_hours = getNumberParam(searchParams, 'window_hours', 24);
  let threshold_pct = getNumberParam(searchParams, 'threshold_pct', 10);

  // Clamp to valid ranges
  window_hours = Math.max(1, Math.min(168, window_hours));
  threshold_pct = Math.max(1, Math.min(80, threshold_pct));

  return { window_hours, threshold_pct };
}

/**
 * Create a new URLSearchParams with window/threshold params preserved.
 */
export function withWindowThreshold(
  searchParams: URLSearchParams,
  window_hours: number,
  threshold_pct: number
): URLSearchParams {
  const newParams = new URLSearchParams(searchParams);
  setNumberParam(newParams, 'window_hours', window_hours);
  setNumberParam(newParams, 'threshold_pct', threshold_pct);
  return newParams;
}

