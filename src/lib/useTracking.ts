/**
 * React Tracking Hooks (Phase 1)
 * ==============================
 * 
 * Custom hooks for user event tracking in React components.
 * 
 * Hooks:
 * - usePageView: Track page views on mount
 * - useTripDwellTime: Track time spent on trip pages
 * - useImpressionTracking: Track visible trip cards
 * - useResultsTracking: Track search results display
 * - useFilterTracking: Track filter changes/removals
 * 
 * @module useTracking
 */

'use client';

import { useEffect, useRef, useCallback } from 'react';
import {
  trackPageView,
  trackTripView,
  trackDwellTime,
  trackImpression,
  trackResultsView,
  trackFilterChange,
  trackFilterRemoved,
  getTrackingIds,
  flushPendingEvents,
  ClickSource,
} from './tracking';

// ============================================
// PAGE VIEW HOOK
// ============================================

/**
 * Track page view on component mount.
 * 
 * @param pageName - Name of the page for analytics
 * 
 * @example
 * usePageView('search');
 */
export function usePageView(pageName: string): void {
  useEffect(() => {
    trackPageView(pageName);
    
    // Cleanup: flush events on unmount
    return () => {
      flushPendingEvents();
    };
  }, [pageName]);
}

// ============================================
// TRIP DWELL TIME HOOK
// ============================================

/**
 * Track time spent on a trip page.
 * 
 * Starts a timer on mount, sends trip_dwell_time event on unmount
 * if duration > 2 seconds.
 * 
 * @param tripId - ID of the trip being viewed
 * 
 * @example
 * useTripDwellTime(123);
 */
export function useTripDwellTime(tripId: number | undefined): void {
  const startTimeRef = useRef<number | null>(null);
  
  useEffect(() => {
    if (!tripId) return;
    
    // Record start time
    startTimeRef.current = Date.now();
    
    // Track trip view event
    trackTripView(tripId);
    
    // Cleanup: calculate duration and track on unmount
    return () => {
      if (startTimeRef.current && tripId) {
        const endTime = Date.now();
        const durationSeconds = Math.floor((endTime - startTimeRef.current) / 1000);
        
        // Track dwell time (only if > 2 seconds)
        trackDwellTime(tripId, durationSeconds);
        
        // Flush immediately since we're unmounting
        flushPendingEvents();
      }
    };
  }, [tripId]);
}

// ============================================
// IMPRESSION TRACKING HOOK
// ============================================

/**
 * Track when a trip card becomes visible in the viewport.
 * 
 * Uses IntersectionObserver for efficient visibility detection.
 * Fires impression event when card is at least 50% visible.
 * 
 * @param tripId - ID of the trip
 * @param position - Position in results (0-indexed)
 * @param score - Match score
 * @param source - Source context (search_results, relaxed_results, etc.)
 * 
 * @returns Ref to attach to the trip card element
 * 
 * @example
 * const ref = useImpressionTracking(trip.id, 0, 85.5, 'search_results');
 * return <div ref={ref}>...</div>;
 */
export function useImpressionTracking(
  tripId: number | undefined,
  position: number,
  score: number,
  source: ClickSource = 'search_results'
): React.RefCallback<HTMLElement> {
  const hasTrackedRef = useRef(false);
  const observerRef = useRef<IntersectionObserver | null>(null);
  
  // Cleanup observer on unmount
  useEffect(() => {
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
        observerRef.current = null;
      }
    };
  }, []);
  
  // Ref callback that sets up the observer
  const refCallback = useCallback(
    (element: HTMLElement | null) => {
      // Disconnect previous observer
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
      
      if (!element || !tripId || hasTrackedRef.current) {
        return;
      }
      
      // Create IntersectionObserver
      observerRef.current = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            // Track when at least 50% visible
            if (entry.isIntersecting && entry.intersectionRatio >= 0.5) {
              if (!hasTrackedRef.current) {
                hasTrackedRef.current = true;
                trackImpression(tripId, position, score, source);
              }
            }
          });
        },
        {
          threshold: 0.5,  // 50% visibility required
          rootMargin: '0px',
        }
      );
      
      observerRef.current.observe(element);
    },
    [tripId, position, score, source]
  );
  
  return refCallback;
}

// ============================================
// RESULTS TRACKING HOOK
// ============================================

interface ResultsTrackingData {
  resultCount: number;
  primaryCount: number;
  relaxedCount: number;
  topScore: number | null;
  responseTimeMs: number;
  recommendationRequestId?: string;
}

/**
 * Track search results display.
 * 
 * Call when results are loaded and displayed.
 * 
 * @param data - Results data (count, scores, timing)
 * 
 * @example
 * useResultsTracking({
 *   resultCount: 10,
 *   primaryCount: 8,
 *   relaxedCount: 2,
 *   topScore: 92.5,
 *   responseTimeMs: 150,
 * });
 */
export function useResultsTracking(data: ResultsTrackingData | null): void {
  const hasTrackedRef = useRef(false);
  const dataRef = useRef<ResultsTrackingData | null>(null);
  
  useEffect(() => {
    // Only track once per unique data
    if (!data || hasTrackedRef.current) return;
    
    // Check if data is different from previous
    const prevData = dataRef.current;
    if (
      prevData &&
      prevData.resultCount === data.resultCount &&
      prevData.primaryCount === data.primaryCount &&
      prevData.relaxedCount === data.relaxedCount
    ) {
      return;
    }
    
    dataRef.current = data;
    hasTrackedRef.current = true;
    
    trackResultsView(
      data.resultCount,
      data.primaryCount,
      data.relaxedCount,
      data.topScore,
      data.responseTimeMs,
      data.recommendationRequestId
    );
  }, [data]);
  
  // Reset when data changes significantly
  useEffect(() => {
    if (data === null) {
      hasTrackedRef.current = false;
      dataRef.current = null;
    }
  }, [data]);
}

// ============================================
// FILTER TRACKING HOOK
// ============================================

interface FilterState {
  [key: string]: unknown;
}

/**
 * Track filter changes and removals.
 * 
 * Compares previous and current filter state to detect:
 * - Filter changes (value modified)
 * - Filter removals (value cleared/removed)
 * 
 * @param filters - Current filter state
 * 
 * @example
 * useFilterTracking({
 *   budget: 5000,
 *   difficulty: 3,
 *   continents: ['europe'],
 * });
 */
export function useFilterTracking(filters: FilterState): void {
  const prevFiltersRef = useRef<FilterState | null>(null);
  const isFirstRenderRef = useRef(true);
  
  useEffect(() => {
    // Skip first render (initial state)
    if (isFirstRenderRef.current) {
      isFirstRenderRef.current = false;
      prevFiltersRef.current = { ...filters };
      return;
    }
    
    const prevFilters = prevFiltersRef.current;
    if (!prevFilters) {
      prevFiltersRef.current = { ...filters };
      return;
    }
    
    // Compare each filter
    for (const key of Object.keys(filters)) {
      const oldValue = prevFilters[key];
      const newValue = filters[key];
      
      // Skip if unchanged
      if (JSON.stringify(oldValue) === JSON.stringify(newValue)) {
        continue;
      }
      
      // Check if filter was removed (cleared)
      const isRemoved = isFilterRemoved(oldValue, newValue);
      
      if (isRemoved) {
        // Filter was cleared/removed
        trackFilterRemoved(key, oldValue);
      } else if (oldValue !== undefined && newValue !== undefined) {
        // Filter was changed
        trackFilterChange(key, oldValue, newValue);
      }
    }
    
    // Update previous state
    prevFiltersRef.current = { ...filters };
  }, [filters]);
}

/**
 * Check if a filter was removed (not just changed).
 */
function isFilterRemoved(oldValue: unknown, newValue: unknown): boolean {
  // Null/undefined check
  if (newValue === null || newValue === undefined || newValue === '') {
    return oldValue !== null && oldValue !== undefined && oldValue !== '';
  }
  
  // Empty array check
  if (Array.isArray(newValue) && newValue.length === 0) {
    return Array.isArray(oldValue) && oldValue.length > 0;
  }
  
  // Default value checks
  if (newValue === 'all' && oldValue !== 'all') {
    return true;
  }
  
  return false;
}

// ============================================
// UTILITY HOOKS
// ============================================

/**
 * Get tracking IDs for API requests.
 * 
 * @returns Object with anonymousId and sessionId
 */
export function useTrackingIds(): { anonymousId: string; sessionId: string } {
  const idsRef = useRef<{ anonymousId: string; sessionId: string } | null>(null);
  
  if (!idsRef.current) {
    idsRef.current = getTrackingIds();
  }
  
  return idsRef.current;
}

// ============================================
// EXPORTS
// ============================================

export {
  trackTripClick,
  trackSaveTrip,
  trackUnsaveTrip,
  trackWhatsAppContact,
  trackPhoneContact,
  trackBookingStart,
  trackSearchSubmit,
  flushPendingEvents,
} from './tracking';

export type { ClickSource } from './tracking';
