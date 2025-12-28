/**
 * Base fetch wrapper for API calls.
 */

/**
 * Generic GET request with query params support.
 * @param path - API path (e.g., "/api/overview")
 * @param params - Optional query parameters
 * @returns Promise with typed JSON response
 */
export async function getJSON<T>(
  path: string,
  params?: Record<string, string | number | boolean | undefined>
): Promise<T> {
  // Build query string from params, filtering out undefined values
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, String(value));
      }
    });
  }

  const url = searchParams.toString()
    ? `${path}?${searchParams.toString()}`
    : path;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

