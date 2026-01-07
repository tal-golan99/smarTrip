/**
 * User Tracking Module (Phase 1)
 * ==============================
 * 
 * Handles user event tracking with:
 * - Anonymous user ID (localStorage)
 * - Session management (30-minute timeout)
 * - Device detection from window.innerWidth (not user-agent)
 * - Event batching for efficiency
 * - Page unload handling via sendBeacon
 * 
 * @module tracking
 */

import { v4 as uuidv4 } from 'uuid';

// ============================================
// CONSTANTS
// ============================================

// Storage keys
const ANONYMOUS_ID_KEY = 'smartrip_anonymous_id';
const SESSION_ID_KEY = 'smartrip_session_id';
const SESSION_EXPIRY_KEY = 'smartrip_session_expiry';

// Session timeout (30 minutes in milliseconds)
const SESSION_TIMEOUT_MS = 30 * 60 * 1000;

// Event batching configuration
const BATCH_SIZE = 10;
const BATCH_INTERVAL_MS = 5000;

// API configuration
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// ============================================
// TYPE DEFINITIONS
// ============================================

/**
 * Valid event types for tracking
 */
export type EventType =
  | 'page_view'
  | 'search_submit'
  | 'results_view'
  | 'impression'
  | 'click_trip'
  | 'trip_view'
  | 'trip_dwell_time'  // NEW: Time spent on trip page
  | 'scroll_depth'
  | 'save_trip'
  | 'unsave_trip'
  | 'contact_whatsapp'
  | 'contact_phone'
  | 'booking_start'
  | 'share_trip'
  | 'filter_change'
  | 'filter_removed'   // NEW: User cleared a filter
  | 'sort_change';

/**
 * Valid source values for click attribution
 */
export type ClickSource = 'search_results' | 'relaxed_results' | 'homepage' | 'similar' | 'saved';

/**
 * Device types (detected from window width, not user-agent)
 */
export type DeviceType = 'mobile' | 'tablet' | 'desktop';

/**
 * Tracking event structure
 */
export interface TrackingEvent {
  event_type: EventType;
  trip_id?: number;
  recommendation_request_id?: string;
  source?: ClickSource;
  metadata?: Record<string, unknown>;
  position?: number;
  score?: number;
  client_timestamp: string;
  page_url: string;
  referrer: string;  // Explicit referrer from document.referrer
}

// ============================================
// STATE
// ============================================

// Event queue for batching
let eventQueue: TrackingEvent[] = [];
let batchTimeout: NodeJS.Timeout | null = null;
let sessionInitialized = false;

// ============================================
// DEVICE DETECTION
// ============================================

/**
 * Detect device type from window width.
 * 
 * Breakpoints:
 * - Mobile: < 768px
 * - Tablet: 768px - 1023px
 * - Desktop: >= 1024px
 * 
 * @returns Device type string
 */
export function detectDeviceType(): DeviceType {
  if (typeof window === 'undefined') {
    return 'desktop';  // SSR fallback
  }
  
  const width = window.innerWidth;
  
  if (width < 768) {
    return 'mobile';
  } else if (width < 1024) {
    return 'tablet';
  }
  return 'desktop';
}

// ============================================
// IDENTITY MANAGEMENT
// ============================================

/**
 * Get or create anonymous user ID.
 * Persists in localStorage for cross-session tracking.
 * 
 * @returns UUID string
 */
export function getAnonymousId(): string {
  if (typeof window === 'undefined') {
    return uuidv4();  // SSR fallback
  }
  
  let anonymousId = localStorage.getItem(ANONYMOUS_ID_KEY);
  
  if (!anonymousId) {
    anonymousId = uuidv4();
    localStorage.setItem(ANONYMOUS_ID_KEY, anonymousId);
  }
  
  return anonymousId;
}

/**
 * Get or create session ID.
 * Sessions expire after 30 minutes of inactivity.
 * 
 * @returns UUID string
 */
export function getSessionId(): string {
  if (typeof window === 'undefined') {
    return uuidv4();  // SSR fallback
  }
  
  const now = Date.now();
  const expiry = localStorage.getItem(SESSION_EXPIRY_KEY);
  let sessionId = localStorage.getItem(SESSION_ID_KEY);
  
  // Check if session expired
  if (!sessionId || !expiry || now > parseInt(expiry, 10)) {
    // Create new session
    sessionId = uuidv4();
    localStorage.setItem(SESSION_ID_KEY, sessionId);
    sessionInitialized = false;  // Need to re-initialize with backend
  }
  
  // Extend session expiry
  localStorage.setItem(SESSION_EXPIRY_KEY, String(now + SESSION_TIMEOUT_MS));
  
  return sessionId;
}

/**
 * Get tracking identifiers for API requests.
 * 
 * @returns Object with anonymousId and sessionId
 */
export function getTrackingIds(): { anonymousId: string; sessionId: string } {
  return {
    anonymousId: getAnonymousId(),
    sessionId: getSessionId(),
  };
}

// ============================================
// SESSION INITIALIZATION
// ============================================

/**
 * Initialize session with backend.
 * Sends device type and referrer.
 * 
 * Called automatically on first event or manually.
 */
export async function initializeSession(): Promise<void> {
  if (typeof window === 'undefined' || sessionInitialized) {
    return;
  }
  
  const anonymousId = getAnonymousId();
  const sessionId = getSessionId();
  const deviceType = detectDeviceType();
  const referrer = document.referrer || '';
  
  try {
    const response = await fetch(`${API_BASE}/api/session/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        anonymous_id: anonymousId,
        session_id: sessionId,
        device_type: deviceType,
        referrer: referrer,
      }),
    });
    
    if (response.ok) {
      sessionInitialized = true;
    }
  } catch (error) {
    console.error('[Tracking] Failed to initialize session:', error);
  }
}

// ============================================
// EVENT TRACKING
// ============================================

/**
 * Track a single event.
 * Events are queued and sent in batches for efficiency.
 * 
 * @param eventType - Type of event
 * @param options - Event options
 */
export function trackEvent(
  eventType: EventType,
  options: {
    tripId?: number;
    recommendationRequestId?: string;
    source?: ClickSource;
    metadata?: Record<string, unknown>;
    position?: number;
    score?: number;
  } = {}
): void {
  if (typeof window === 'undefined') {
    return;  // Skip on SSR
  }
  
  // Ensure session is initialized
  if (!sessionInitialized) {
    initializeSession();
  }
  
  const event: TrackingEvent = {
    event_type: eventType,
    trip_id: options.tripId,
    recommendation_request_id: options.recommendationRequestId,
    source: options.source,
    metadata: options.metadata,
    position: options.position,
    score: options.score,
    client_timestamp: new Date().toISOString(),
    page_url: window.location.pathname + window.location.search,
    referrer: document.referrer || '',
  };
  
  eventQueue.push(event);
  
  // Send immediately if batch size reached
  if (eventQueue.length >= BATCH_SIZE) {
    flushEvents();
  } else if (!batchTimeout) {
    // Schedule batch send
    batchTimeout = setTimeout(flushEvents, BATCH_INTERVAL_MS);
  }
}

/**
 * Send queued events to backend.
 */
async function flushEvents(): Promise<void> {
  if (batchTimeout) {
    clearTimeout(batchTimeout);
    batchTimeout = null;
  }
  
  if (eventQueue.length === 0) {
    return;
  }
  
  const eventsToSend = [...eventQueue];
  eventQueue = [];
  
  const anonymousId = getAnonymousId();
  const sessionId = getSessionId();
  
  // Get Supabase user info if authenticated (optional)
  // Skip this during page unload to prevent blocking
  let userEmail: string | undefined;
  if (typeof window !== 'undefined' && document.visibilityState !== 'hidden') {
    try {
      const { getCurrentUser } = await import('./supabaseClient');
      const user = await getCurrentUser();
      userEmail = user?.email || undefined;
    } catch (error) {
      // Supabase not available or not configured - continue as guest
      // Silently fail - don't log to avoid console spam
    }
  }
  
  // Add identity to each event
  const payload = {
    events: eventsToSend.map(event => ({
      ...event,
      anonymous_id: anonymousId,
      session_id: sessionId,
      ...(userEmail ? { email: userEmail } : {}),  // Include email if authenticated
    })),
  };
  
  try {
    const response = await fetch(`${API_BASE}/api/events/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive: true,  // Allow completion during page unload
    });
    
    if (!response.ok) {
      console.error('[Tracking] Failed to send events:', response.status);
      // Re-queue failed events (with limit)
      if (eventQueue.length < 100) {
        eventQueue = [...eventsToSend, ...eventQueue];
      }
    }
  } catch (error) {
    console.error('[Tracking] Error sending events:', error);
    // Re-queue on network error
    if (eventQueue.length < 100) {
      eventQueue = [...eventsToSend, ...eventQueue];
    }
  }
}

/**
 * Flush pending events (call before page unload).
 * Uses sendBeacon for reliable delivery.
 * 
 * Note: This function cannot be async because it's called during page unload.
 * We'll get user email synchronously if available from session storage.
 */
export function flushPendingEvents(): void {
  if (eventQueue.length === 0) {
    return;
  }
  
  // Use sendBeacon for reliable delivery during page unload
  if (typeof navigator !== 'undefined' && navigator.sendBeacon) {
    const anonymousId = getAnonymousId();
    const sessionId = getSessionId();
    
    // Try to get user email from session storage (set by auth system)
    // This is a synchronous fallback since we can't await during page unload
    let userEmail: string | undefined;
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        // Supabase stores session in localStorage, but we can't easily extract email
        // For now, we'll send without email during page unload
        // The regular flushEvents() will include email when called normally
      }
    } catch (error) {
      // Ignore errors during unload
    }
    
    const payload = JSON.stringify({
      events: eventQueue.map(event => ({
        ...event,
        anonymous_id: anonymousId,
        session_id: sessionId,
        // Note: Email not included during page unload (would require async)
        // Regular flushEvents() includes email when called normally
      })),
    });
    
    const blob = new Blob([payload], { type: 'application/json' });
    navigator.sendBeacon(`${API_BASE}/api/events/batch`, blob);
    eventQueue = [];
  } else {
    // Fallback to async fetch
    flushEvents();
  }
}

// ============================================
// HIGH-LEVEL TRACKING FUNCTIONS
// ============================================

/**
 * Track page view event.
 */
export function trackPageView(pageName: string): void {
  trackEvent('page_view', {
    metadata: { page_name: pageName },
  });
}

/**
 * Track search submission.
 */
export function trackSearchSubmit(
  preferences: Record<string, unknown>,
  searchType: 'exploration' | 'focused_search' = 'exploration'
): void {
  trackEvent('search_submit', {
    metadata: { 
      preferences,
      search_type: searchType,
    },
  });
}

/**
 * Track results view.
 */
export function trackResultsView(
  resultCount: number,
  primaryCount: number,
  relaxedCount: number,
  topScore: number | null,
  responseTimeMs: number,
  recommendationRequestId?: string
): void {
  trackEvent('results_view', {
    recommendationRequestId,
    metadata: {
      result_count: resultCount,
      primary_count: primaryCount,
      relaxed_count: relaxedCount,
      top_score: topScore,
      has_relaxed: relaxedCount > 0,
      response_time_ms: responseTimeMs,
    },
  });
}

/**
 * Track trip impression (card visible in viewport).
 */
export function trackImpression(
  tripId: number,
  position: number,
  score: number,
  source: ClickSource = 'search_results'
): void {
  trackEvent('impression', {
    tripId,
    position,
    score,
    source,
  });
}

/**
 * Track trip click.
 * Source is REQUIRED for proper attribution.
 */
export function trackTripClick(
  tripId: number,
  position: number,
  score: number,
  source: ClickSource,  // Required!
  timeToClickMs?: number
): void {
  trackEvent('click_trip', {
    tripId,
    position,
    score,
    source,
    metadata: timeToClickMs ? { time_to_click_ms: timeToClickMs } : undefined,
  });
}

/**
 * Track trip detail page view.
 */
export function trackTripView(tripId: number): void {
  trackEvent('trip_view', {
    tripId,
    metadata: { referrer: document.referrer },
  });
}

/**
 * Track dwell time on trip page.
 * Called when user leaves the page.
 */
export function trackDwellTime(tripId: number, durationSeconds: number): void {
  // Only track if user spent meaningful time (> 2 seconds)
  if (durationSeconds > 2) {
    trackEvent('trip_dwell_time', {
      tripId,
      metadata: { duration_seconds: durationSeconds },
    });
  }
}

/**
 * Track filter change.
 */
export function trackFilterChange(
  filterName: string,
  oldValue: unknown,
  newValue: unknown
): void {
  trackEvent('filter_change', {
    metadata: {
      filter_name: filterName,
      old_value: oldValue,
      new_value: newValue,
    },
  });
}

/**
 * Track filter removed (user cleared a filter).
 */
export function trackFilterRemoved(filterName: string, oldValue: unknown): void {
  trackEvent('filter_removed', {
    metadata: {
      filter_name: filterName,
      old_value: oldValue,
    },
  });
}

/**
 * Track save/bookmark trip.
 */
export function trackSaveTrip(tripId: number): void {
  trackEvent('save_trip', { tripId });
}

/**
 * Track unsave trip.
 */
export function trackUnsaveTrip(tripId: number): void {
  trackEvent('unsave_trip', { tripId });
}

/**
 * Track WhatsApp contact click.
 */
export function trackWhatsAppContact(tripId: number): void {
  trackEvent('contact_whatsapp', { tripId });
}

/**
 * Track phone contact click.
 */
export function trackPhoneContact(tripId: number): void {
  trackEvent('contact_phone', { tripId });
}

/**
 * Track booking start.
 */
export function trackBookingStart(tripId: number): void {
  trackEvent('booking_start', { tripId });
}

// ============================================
// PAGE UNLOAD HANDLER
// ============================================

if (typeof window !== 'undefined') {
  // Flush events on page unload
  window.addEventListener('beforeunload', flushPendingEvents);
  window.addEventListener('pagehide', flushPendingEvents);
  
  // Initialize session on load
  if (document.readyState === 'complete') {
    initializeSession();
  } else {
    window.addEventListener('load', initializeSession);
  }
}
