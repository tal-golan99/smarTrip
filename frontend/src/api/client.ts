/**
 * Core API client utilities
 * Handles HTTP requests with authentication, error handling, retry logic, validation, and logging
 */

import { z, type ZodSchema } from 'zod';
import type { ApiResponse } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Warn if using localhost in production
if (typeof window !== 'undefined' && API_BASE_URL.includes('localhost') && process.env.NODE_ENV === 'production') {
  console.error('[API] WARNING: Using localhost API URL in production! Set NEXT_PUBLIC_API_URL in Vercel.');
}

// Use V2 API endpoints
export const API_VERSION = '/api/v2';

const IS_DEVELOPMENT = process.env.NODE_ENV === 'development';

/**
 * Log API call (development only)
 */
function logApiCall(endpoint: string, method: string, status: number, duration: number): void {
  if (!IS_DEVELOPMENT) return;
  
  console.log(`[API] ${method} ${endpoint} - ${status} (${duration}ms)`);
}

/**
 * Log API error (development only)
 */
function logApiError(endpoint: string, error: Error, retryAttempt: number): void {
  if (!IS_DEVELOPMENT) return;
  
  console.error(`[API] Error on ${endpoint} (attempt ${retryAttempt + 1}):`, error);
}

/**
 * Log API warning (development only)
 */
export function logApiWarning(message: string, data?: any): void {
  if (!IS_DEVELOPMENT) return;
  
  console.warn(`[API] ${message}`, data || '');
}

/**
 * Get authentication headers (includes Supabase JWT if user is logged in)
 */
async function getAuthHeaders(): Promise<Record<string, string>> {
  try {
    // Only try to get auth token if we're in the browser (client-side)
    if (typeof window === 'undefined') {
      return {}; // Server-side rendering - no auth
    }
    
    // Dynamically import to avoid SSR issues
    const { getAccessToken } = await import('../lib/supabaseClient');
    const token = await getAccessToken();
    
    if (token) {
      return {
        'Authorization': `Bearer ${token}`,
      };
    }
  } catch (error) {
    // Supabase not configured or not available - continue without auth
    // Don't log warnings for missing Supabase config (it's optional)
    if (error instanceof Error && !error.message.includes('Supabase not configured')) {
      logApiWarning('Could not get auth token', error);
    }
  }
  
  return {};
}

/**
 * Validate API response using Zod schema
 * In production: Lightweight validation with error tracking
 * In development: Full validation with detailed logging
 */
function validateResponse<T>(
  data: any,
  schema?: ZodSchema<T>,
  endpoint?: string
): { isValid: boolean; errors?: z.ZodIssue[]; data?: T } {
  // If no schema provided, skip validation
  if (!schema) {
    return { isValid: true, data: data as T };
  }
  
  try {
    // Use safeParse to avoid throwing errors
    const result = schema.safeParse(data);
    
    if (!result.success) {
      // Log validation failure
      if (IS_DEVELOPMENT) {
        // Development: Detailed logging
        logApiWarning(`Response validation failed (${result.error.issues.length} errors)`);
        console.error('Validation errors:', result.error.issues);
      } else {
        // Production: Log to error tracking service (Sentry, etc.)
        if (typeof window !== 'undefined' && (window as any).Sentry) {
          (window as any).Sentry.captureException(
            new Error('API validation failed'),
            {
              extra: {
                endpoint,
                errorCount: result.error.issues.length,
                errors: result.error.issues.slice(0, 5), // Only send first 5 errors
              }
            }
          );
        }
      }
      
      // Return data anyway (graceful degradation)
      return { isValid: false, errors: result.error.issues, data: data as T };
    }
    
    return { isValid: true, data: result.data };
  } catch (error) {
    // Fallback error handling
    if (error instanceof z.ZodError) {
      if (IS_DEVELOPMENT) {
        logApiWarning(`Response validation error (${error.issues.length} errors)`);
      }
      return { isValid: false, errors: error.issues, data: data as T };
    }
    
    // Non-Zod errors - log but don't fail
    if (IS_DEVELOPMENT) {
      logApiWarning('Unexpected validation error', error);
    }
    
    return { isValid: true, data: data as T };
  }
}

/**
 * Generic API fetch wrapper with error handling, authentication, timeout, retry logic, validation, and logging
 * Retries network errors (cold starts, timeouts) automatically
 */
export async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit,
  retryAttempt = 0,
  schema?: ZodSchema<any>
): Promise<ApiResponse<T>> {
  const MAX_RETRIES = 1; // Retry once
  const RETRY_DELAY = 2500; // 2.5 seconds (gives server time to wake up from cold start)
  const TIMEOUT_MS = 30000; // 30 second timeout
  
  let timeoutId: NodeJS.Timeout | null = null;
  let controller: AbortController | null = null;
  const startTime = Date.now();
  
  try {
    // Get auth headers (if user is logged in)
    const authHeaders = await getAuthHeaders();
    
    // Create abort controller for timeout
    controller = new AbortController();
    timeoutId = setTimeout(() => {
      controller?.abort();
    }, TIMEOUT_MS);
    
    if (IS_DEVELOPMENT) {
      logApiCall(endpoint, options?.method || 'GET', 0, 0);
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
        ...options?.headers,
      },
    });

    // Clear timeout on successful response
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }

    const duration = Date.now() - startTime;
    
    if (IS_DEVELOPMENT) {
      logApiCall(endpoint, options?.method || 'GET', response.status, duration);
    }

    let data;
    try {
      data = await response.json();
    } catch (jsonError) {
      // If response is not JSON, return error
      throw new Error('Invalid JSON response from server');
    }

    if (!response.ok) {
      // Return user-friendly error message from backend, or generic message
      const errorMessage = data.error || 'שגיאה בשרת. אנא נסה שוב מאוחר יותר.';
      throw new Error(errorMessage);
    }

    // Validate response structure (runs in both dev and production)
    if (schema) {
      validateResponse(data, schema, endpoint);
    }

    // Backend returns data in various formats:
    // - Standard: { success: true, data: {...} }
    // - Non-standard: { success: true, countries: [...], continents: [...] }
    // apiFetch returns the raw response, so we preserve it
    return data;
  } catch (error) {
    // Clear timeout if it wasn't cleared
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
    
    if (IS_DEVELOPMENT) {
      logApiError(endpoint, error as Error, retryAttempt);
    }
    
    // Determine if error is retryable (network error, timeout, connection refused)
    const isRetryableError = 
      error instanceof Error && (
        error.name === 'AbortError' || // Timeout
        error.message.includes('fetch') || // Network error
        error.message.includes('Failed to fetch') || // Chrome/Firefox network error
        error.message.includes('NetworkError') || // Firefox network error
        error.message.includes('Network request failed') || // React Native
        error.message.toLowerCase().includes('connection') || // Connection errors
        error.message.toLowerCase().includes('refused') || // Connection refused
        error.message.toLowerCase().includes('timeout') // Timeout errors
      );
    
    // If it's a retryable error AND we haven't exceeded max retries, retry
    if (isRetryableError && retryAttempt < MAX_RETRIES) {
      if (IS_DEVELOPMENT) {
        console.log(`[API] Network error detected, retrying in ${RETRY_DELAY}ms... (attempt ${retryAttempt + 1}/${MAX_RETRIES + 1})`);
      }
      
      // Wait before retrying (gives server time to wake up from cold start)
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
      
      // Retry the request
      return apiFetch<T>(endpoint, options, retryAttempt + 1, schema);
    }
    
    // Not retryable, or max retries exceeded - return error
    // Only log errors in development (production uses error tracking service)
    if (IS_DEVELOPMENT) {
      console.error('API Error:', error);
    }
    
    // Provide user-friendly error message
    let errorMessage = 'Unknown error occurred';
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        errorMessage = 'Request timeout - server is taking too long to respond';
      } else if (isRetryableError) {
        errorMessage = 'Cannot connect to server - please try again in a moment';
      } else {
        errorMessage = error.message;
      }
    }
    
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Helper function to convert camelCase to snake_case for query parameters
 */
export function camelToSnake(str: string): string {
  return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
}

/**
 * Helper function to convert camelCase to snake_case for request body
 */
export function camelToSnakeObject(obj: any): any {
  if (obj === null || obj === undefined) {
    return obj;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => camelToSnakeObject(item));
  }
  
  if (typeof obj === 'object') {
    const result: any = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        const snakeKey = camelToSnake(key);
        result[snakeKey] = camelToSnakeObject(obj[key]);
      }
    }
    return result;
  }
  
  return obj;
}
