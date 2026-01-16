/**
 * Event schemas
 * 
 * Schemas for event tracking and session management endpoints
 */

import { z } from 'zod';

// ============================================
// REQUEST SCHEMAS
// ============================================

/**
 * Session start request schema
 */
export const SessionStartRequestSchema = z.object({
  session_id: z.string().uuid(),
  anonymous_id: z.string().uuid(),
  device_type: z.enum(['mobile', 'tablet', 'desktop']).nullable().optional(),
  referrer: z.string().nullable().optional(), // Can be null or empty string
  email: z.string().email().nullable().optional(), // Can be null if not provided
});

/**
 * Single event request schema
 */
export const EventRequestSchema = z.object({
  event_type: z.string(),
  session_id: z.string().uuid(),
  anonymous_id: z.string().uuid(),
  trip_id: z.number().nullable().optional(),
  source: z.string().nullable().optional(), // Can be null if not provided
  recommendation_request_id: z.string().uuid().nullable().optional(),
  metadata: z.record(z.string(), z.any()).nullable().optional(), // Can be null or empty object
  position: z.number().nullable().optional(),
  score: z.number().nullable().optional(),
  client_timestamp: z.string().nullable().optional(),
  page_url: z.string().nullable().optional(),
  referrer: z.string().nullable().optional(), // Can be null or empty string
  email: z.string().email().nullable().optional(), // Can be null if not provided
});

/**
 * Batch events request schema
 */
export const EventBatchRequestSchema = z.object({
  events: z.array(EventRequestSchema),
});

/**
 * User identify request schema
 */
export const UserIdentifyRequestSchema = z.object({
  anonymous_id: z.string().uuid(),
  email: z.string().email().nullable().optional(), // Can be null if not provided
  name: z.string().nullable().optional(), // Can be null if not provided
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
    type: z.string().nullable().optional(), // Error type field (for events API error responses)
  }).passthrough();
}

/**
 * Session start response schema
 * Note: Backend returns data at top level, NOT wrapped in 'data' field
 * Format: { success: true, user_id: ..., session_id: ..., is_new_session: ... }
 */
export const SessionStartResponseSchema = z.object({
  success: z.boolean(),
  user_id: z.number(),
  session_id: z.string().uuid(),
  is_new_session: z.boolean(),
  error: z.string().nullable().optional(),
  type: z.string().nullable().optional(), // Error type field (for error responses)
}).passthrough();

/**
 * Single event response schema
 */
export const EventResponseSchema = createApiResponseSchema(
  z.object({
    event_id: z.number(),
  }).passthrough() // Allow additional fields from backend
);

/**
 * Batch events response schema
 */
export const EventBatchResponseSchema = createApiResponseSchema(
  z.object({
    processed: z.number(),
    total: z.number(),
    errors: z.array(z.any()).nullable().optional(), // Can be null if no errors
  })
);

/**
 * User identify response schema
 */
export const UserIdentifyResponseSchema = createApiResponseSchema(
  z.object({
    user_id: z.number(),
    is_registered: z.boolean(),
  }).passthrough() // Allow additional fields from backend
);

/**
 * Event types response schema
 * Note: Backend returns data at top level, NOT wrapped in 'data' field
 * Format: { success: true, event_types: [...], categories: {...}, valid_sources: [...] }
 */
export const EventTypesResponseSchema = z.object({
  success: z.boolean(),
  event_types: z.array(z.string()),
  categories: z.record(z.string(), z.array(z.string())),
  valid_sources: z.array(z.string()),
  error: z.string().nullable().optional(),
}).passthrough();
