/**
 * System API endpoints
 * Health checks and system operations
 */

import { apiFetch } from './client';
import { HealthCheckResponseSchema } from '../schemas';
import type { ApiResponse } from './types';

/**
 * Health check
 */
export async function healthCheck(): Promise<ApiResponse> {
  return apiFetch('/api/health', undefined, 0, HealthCheckResponseSchema);
}
