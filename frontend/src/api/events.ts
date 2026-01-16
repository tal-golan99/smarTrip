/**
 * Events API endpoints
 * 
 * Transport layer only - just HTTP calls with validation.
 * NO business logic (queuing, batching, retry strategies) - that belongs in services.
 * 
 * This file mirrors backend/app/api/events/routes.py
 */

import { apiFetch, camelToSnakeObject } from './client';
import {
  SessionStartRequestSchema,
  SessionStartResponseSchema,
  EventRequestSchema,
  EventResponseSchema,
  EventBatchRequestSchema,
  EventBatchResponseSchema,
  UserIdentifyRequestSchema,
  UserIdentifyResponseSchema,
  EventTypesResponseSchema,
} from '../schemas';
import type { ApiResponse } from './types';

// ============================================
// SESSION MANAGEMENT
// ============================================

/**
 * Start or resume a session
 * Transport layer only - just makes the HTTP call
 * 
 * Service layer should handle session orchestration (when to call, retry logic, etc.)
 */
export async function startSession(
  request: {
    sessionId: string;
    anonymousId: string;
    deviceType?: 'mobile' | 'tablet' | 'desktop';
    referrer?: string;
    email?: string;
  }
): Promise<ApiResponse<{
  userId: number;
  sessionId: string;
  isNewSession: boolean;
}>> {
  // Convert camelCase to snake_case for backend compatibility
  const requestBody = {
    session_id: request.sessionId,
    anonymous_id: request.anonymousId,
    device_type: request.deviceType,
    referrer: request.referrer,
    email: request.email,
  };

  // Backend returns data at top level: { success: true, user_id: ..., session_id: ..., is_new_session: ... }
  const response = await apiFetch<any>(
    '/api/session/start',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    },
    0,
    SessionStartResponseSchema
  ) as any;

  // Map snake_case to camelCase and wrap in standard ApiResponse format
  if (!response.success) {
    return {
      success: false,
      error: response.error || 'Failed to start session',
    };
  }

  return {
    success: true,
    data: {
      userId: response.user_id,
      sessionId: response.session_id,
      isNewSession: response.is_new_session,
    },
  };
}

// ============================================
// EVENT TRACKING
// ============================================

/**
 * Track a single event
 * Transport layer only - just makes the HTTP call
 * 
 * Service layer should handle queuing, batching, retry logic, etc.
 */
export async function trackEvent(
  event: {
    eventType: string;
    sessionId: string;
    anonymousId: string;
    tripId?: number;
    source?: string;
    recommendationRequestId?: string;
    metadata?: Record<string, unknown>;
    position?: number;
    score?: number;
    clientTimestamp?: string;
    pageUrl?: string;
    referrer?: string;
    email?: string;
  }
): Promise<ApiResponse<{ eventId: number }>> {
  // Convert camelCase to snake_case for backend compatibility
  const requestBody = camelToSnakeObject(event);

  return apiFetch<{ eventId: number }>(
    '/api/events',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    },
    0,
    EventResponseSchema
  );
}

/**
 * Track multiple events in a batch
 * Transport layer only - just makes the HTTP call
 * 
 * Service layer should handle event queuing, when to flush, retry logic, etc.
 */
export async function trackEventsBatch(
  batch: {
    events: Array<{
      eventType: string;
      sessionId: string;
      anonymousId: string;
      tripId?: number;
      source?: string;
      recommendationRequestId?: string;
      metadata?: Record<string, unknown>;
      position?: number;
      score?: number;
      clientTimestamp?: string;
      pageUrl?: string;
      referrer?: string;
      email?: string;
    }>;
  }
): Promise<ApiResponse<{
  processed: number;
  total: number;
  errors?: unknown[];
}>> {
  // Convert camelCase to snake_case for backend compatibility
  const requestBody = {
    events: batch.events.map(event => camelToSnakeObject(event)),
  };

  return apiFetch<{
    processed: number;
    total: number;
    errors?: unknown[];
  }>(
    '/api/events/batch',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
      keepalive: true, // Allow completion during page unload
    },
    0,
    EventBatchResponseSchema
  );
}

// ============================================
// USER IDENTIFICATION
// ============================================

/**
 * Identify/register a user
 * Transport layer only - just makes the HTTP call
 */
export async function identifyUser(
  request: {
    anonymousId: string;
    email?: string;
    name?: string;
  }
): Promise<ApiResponse<{
  userId: number;
  isRegistered: boolean;
}>> {
  // Convert camelCase to snake_case for backend compatibility
  const requestBody = camelToSnakeObject(request);

  return apiFetch<{
    userId: number;
    isRegistered: boolean;
  }>(
    '/api/user/identify',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    },
    0,
    UserIdentifyResponseSchema
  );
}

// ============================================
// EVENT TYPES
// ============================================

/**
 * Get valid event types and categories
 * Transport layer only - just makes the HTTP call
 */
export async function getEventTypes(): Promise<ApiResponse<{
  eventTypes: string[];
  categories: Record<string, string[]>;
  validSources: string[];
}>> {
  // Backend returns data at top level: { success: true, event_types: [...], categories: {...}, valid_sources: [...] }
  const response = await apiFetch<any>(
    '/api/events/types',
    undefined,
    0,
    EventTypesResponseSchema
  ) as any;

  if (!response.success) {
    return {
      success: false,
      error: response.error || 'Failed to get event types',
    };
  }

  // Map snake_case to camelCase and wrap in standard ApiResponse format
  return {
    success: true,
    data: {
      eventTypes: response.event_types || [],
      categories: response.categories || {},
      validSources: response.valid_sources || [],
    },
  };
}
