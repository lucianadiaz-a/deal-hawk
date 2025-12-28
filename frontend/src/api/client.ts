/**
 * Base fetch wrapper for API calls.
 */

// Get API base URL from environment variable, fallback to relative path for dev
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

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

  // Prepend API base URL if provided (for production)
  const fullUrl = API_BASE_URL ? `${API_BASE_URL}${url}` : url;

  const response = await fetch(fullUrl);

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

