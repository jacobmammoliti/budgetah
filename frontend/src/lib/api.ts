/**
 * Thin typed fetch wrapper for the Budgetah backend API.
 * All requests are prefixed with BASE_URL from the environment variable.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1';

/** Typed API error with HTTP status and backend detail message. */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
  ) {
    super(`API error ${status}: ${detail}`);
    this.name = 'ApiError';
  }
}

/**
 * Parses the response and throws ApiError for non-2xx status codes.
 * Returns undefined for 204 No Content.
 */
async function handleResponse<T>(res: Response): Promise<T> {
  if (res.status === 204) {
    return undefined as unknown as T;
  }

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (typeof body?.detail === 'string') {
        detail = body.detail;
      } else if (Array.isArray(body?.detail)) {
        detail = body.detail.map((d: { msg?: string }) => d.msg ?? String(d)).join('; ');
      }
    } catch {
      // ignore parse errors — use the default detail message
    }
    throw new ApiError(res.status, detail);
  }

  return res.json() as Promise<T>;
}

/** Typed API client with get, post, put, and delete methods. */
export const apiClient = {
  /**
   * Performs a GET request. Uses cache: 'no-store' to ensure Server Components
   * always receive fresh data.
   *
   * @param path - API path (e.g. '/transactions')
   * @returns Parsed JSON response body
   */
  async get<T>(path: string): Promise<T> {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      cache: 'no-store',
    });
    return handleResponse<T>(res);
  },

  /**
   * Performs a POST request with a JSON body.
   *
   * @param path - API path
   * @param body - Request body (will be JSON-serialized)
   * @returns Parsed JSON response body
   */
  async post<T>(path: string, body: unknown): Promise<T> {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return handleResponse<T>(res);
  },

  /**
   * Performs a PUT request with a JSON body.
   *
   * @param path - API path including resource ID (e.g. '/transactions/1')
   * @param body - Request body (will be JSON-serialized)
   * @returns Parsed JSON response body
   */
  async put<T>(path: string, body: unknown): Promise<T> {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return handleResponse<T>(res);
  },

  /**
   * Performs a DELETE request.
   *
   * @param path - API path including resource ID (e.g. '/transactions/1')
   * @returns undefined (expects 204 No Content)
   */
  async delete(path: string): Promise<void> {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
    });
    await handleResponse<void>(res);
  },
};
