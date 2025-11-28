/**
 * API utilities with retry logic and error handling
 */

interface RetryOptions {
  maxRetries?: number;
  retryDelay?: number;
  backoff?: boolean;
}

/**
 * Fetch with automatic retry logic
 */
export async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retryOptions: RetryOptions = {}
): Promise<Response> {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    backoff = true,
  } = retryOptions;

  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);

      // Don't retry on 4xx errors (client errors)
      if (response.status >= 400 && response.status < 500) {
        return response;
      }

      // Retry on 5xx errors (server errors)
      if (response.ok || attempt === maxRetries) {
        return response;
      }

      lastError = new Error(`HTTP ${response.status}: ${response.statusText}`);
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error');

      // Don't retry on the last attempt
      if (attempt === maxRetries) {
        throw lastError;
      }
    }

    // Wait before retrying
    const delay = backoff ? retryDelay * Math.pow(2, attempt) : retryDelay;
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  throw lastError || new Error('Max retries exceeded');
}

/**
 * Fetch JSON with retry and type safety
 */
export async function fetchJSON<T>(
  url: string,
  options: RequestInit = {},
  retryOptions?: RetryOptions
): Promise<T> {
  const response = await fetchWithRetry(url, options, retryOptions);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.message || `HTTP ${response.status}: ${response.statusText}`
    );
  }

  return response.json();
}

/**
 * API error class with additional context
 */
export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'APIError';
  }
}
