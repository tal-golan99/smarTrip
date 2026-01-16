/**
 * useSearch Hook
 * Provides access to shared search state via Context API.
 * All components using this hook share the same state when wrapped in SearchProvider.
 */

'use client';

import { useSearchContext } from '@/contexts/SearchContext';

// Re-export types for convenience
export type { LocationSelection, SearchFilters } from '@/contexts/SearchContext';

/**
 * useSearch Hook
 * 
 * Access shared search state and actions.
 * Must be used within SearchProvider.
 */
export function useSearch() {
  return useSearchContext();
}
