/**
 * Analytics schemas
 * 
 * Schemas for metrics and evaluation endpoints
 */

import { z } from 'zod';

// ============================================
// REQUEST SCHEMAS
// ============================================

/**
 * Evaluation run request schema
 */
export const EvaluationRunRequestSchema = z.object({
  category: z.string().nullable().optional(), // Can be null if not provided
  scenario_ids: z.array(z.number()).nullable().optional(), // Can be null if not provided
});

// ============================================
// RESPONSE SCHEMAS
// ============================================

/**
 * Generic ApiResponse schema factory
 */
function createApiResponseSchema<T extends z.ZodTypeAny>(dataSchema: T) {
  return z.object({
    success: z.boolean(),
    data: dataSchema.optional(),
    count: z.number().nullable().optional(),
    total: z.number().nullable().optional(),
    error: z.string().nullable().optional(), // Can be null or undefined
    message: z.string().nullable().optional(), // Can be null or undefined
    api_version: z.string().nullable().optional(),
  }).passthrough();
}

/**
 * Metrics response schema (flexible structure from backend)
 */
export const MetricsResponseSchema = createApiResponseSchema(
  z.record(z.string(), z.any()) // Flexible metrics structure
);

/**
 * Daily metrics response schema
 */
export const DailyMetricsResponseSchema = z.object({
  success: z.boolean(),
  start: z.string(),
  end: z.string(),
  count: z.number(),
  data: z.array(z.record(z.string(), z.any())), // Flexible daily metrics structure
  error: z.string().nullable().optional(), // Can be null or undefined
}).passthrough();

/**
 * Top searches response schema
 */
export const TopSearchesResponseSchema = createApiResponseSchema(
  z.record(z.string(), z.array(z.any())) // Flexible top searches structure
);

/**
 * Evaluation run response schema (flexible structure)
 * Note: Backend returns a flexible report structure, so we use passthrough on an object
 */
export const EvaluationRunResponseSchema = z.object({}).passthrough();

/**
 * Evaluation scenario schema
 */
export const EvaluationScenarioSchema = z.object({
  id: z.number(),
  name: z.string().nullable().optional(), // Can be null if not provided
  description: z.string().nullable().optional(), // Can be null if not provided
  category: z.string().nullable().optional(), // Can be null if not provided
  expected_min_results: z.number().nullable().optional(), // Can be null if not provided
}).passthrough(); // Allow additional fields from backend

/**
 * Evaluation scenarios response schema
 */
export const EvaluationScenariosResponseSchema = createApiResponseSchema(
  z.array(EvaluationScenarioSchema)
);
