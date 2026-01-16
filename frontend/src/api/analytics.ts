/**
 * Analytics API endpoints
 * 
 * Transport layer only - just HTTP calls with validation.
 * 
 * This file mirrors backend/app/api/analytics/routes.py
 */

import { apiFetch, camelToSnakeObject } from './client';
import {
  MetricsResponseSchema,
  DailyMetricsResponseSchema,
  TopSearchesResponseSchema,
  EvaluationRunRequestSchema,
  EvaluationRunResponseSchema,
  EvaluationScenariosResponseSchema,
} from '../schemas';
import type { ApiResponse } from './types';

// ============================================
// METRICS ENDPOINTS
// ============================================

/**
 * Get current recommendation metrics (summary)
 * Transport layer only - just makes the HTTP call
 */
export async function getMetrics(
  days?: number
): Promise<ApiResponse<Record<string, unknown>>> {
  const query = days ? `?days=${days}` : '';
  return apiFetch<Record<string, unknown>>(
    `/api/metrics${query}`,
    undefined,
    0,
    MetricsResponseSchema
  );
}

/**
 * Get daily breakdown of recommendation metrics
 * Transport layer only - just makes the HTTP call
 */
export async function getDailyMetrics(
  params?: {
    start?: string; // YYYY-MM-DD
    end?: string; // YYYY-MM-DD
  }
): Promise<ApiResponse<{
  start: string;
  end: string;
  count: number;
  data: Array<Record<string, unknown>>;
}>> {
  const queryParams = new URLSearchParams();
  if (params?.start) {
    queryParams.append('start', params.start);
  }
  if (params?.end) {
    queryParams.append('end', params.end);
  }
  const query = queryParams.toString() ? `?${queryParams.toString()}` : '';

  return apiFetch<{
    start: string;
    end: string;
    count: number;
    data: Array<Record<string, unknown>>;
  }>(
    `/api/metrics/daily${query}`,
    undefined,
    0,
    DailyMetricsResponseSchema
  );
}

/**
 * Get top search patterns (continents, types, etc.)
 * Transport layer only - just makes the HTTP call
 */
export async function getTopSearches(
  params?: {
    days?: number;
    limit?: number;
  }
): Promise<ApiResponse<Record<string, unknown[]>>> {
  const queryParams = new URLSearchParams();
  if (params?.days !== undefined) {
    queryParams.append('days', params.days.toString());
  }
  if (params?.limit !== undefined) {
    queryParams.append('limit', params.limit.toString());
  }
  const query = queryParams.toString() ? `?${queryParams.toString()}` : '';

  return apiFetch<Record<string, unknown[]>>(
    `/api/metrics/top-searches${query}`,
    undefined,
    0,
    TopSearchesResponseSchema
  );
}

// ============================================
// EVALUATION ENDPOINTS
// ============================================

/**
 * Run evaluation scenarios and get results
 * Transport layer only - just makes the HTTP call
 */
export async function runEvaluation(
  request?: {
    category?: string;
    scenarioIds?: number[];
  }
): Promise<ApiResponse<Record<string, unknown>>> {
  // Convert camelCase to snake_case for backend compatibility
  const requestBody = request
    ? camelToSnakeObject(request)
    : {};

  return apiFetch<Record<string, unknown>>(
    '/api/evaluation/run',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    },
    0,
    EvaluationRunResponseSchema
  );
}

/**
 * Get available evaluation scenarios without running them
 * Transport layer only - just makes the HTTP call
 */
export async function getEvaluationScenarios(
  category?: string
): Promise<ApiResponse<Array<{
  id: number;
  name: string;
  description: string;
  category: string;
  expectedMinResults: number;
}>>> {
  const query = category ? `?category=${category}` : '';
  return apiFetch<Array<{
    id: number;
    name: string;
    description: string;
    category: string;
    expectedMinResults: number;
  }>>(
    `/api/evaluation/scenarios${query}`,
    undefined,
    0,
    EvaluationScenariosResponseSchema
  );
}
