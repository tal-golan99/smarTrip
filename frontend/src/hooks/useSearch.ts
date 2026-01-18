/**
 * useSearch Hook
 * 
 * Convenient wrapper for accessing URL-based search filters.
 * This is the recommended way to use search filters in components.
 * 
 * Architecture:
 * - useSearch() ← Simple API (use this in components)
 * - SearchFiltersContext ← Provides countries data
 * - useSearchFilters(countries) ← Core implementation
 * - URL Parameters ← Single source of truth
 * 
 * Benefits of using this over useSearchFilters directly:
 * - No need to pass countries parameter
 * - Cleaner, more intuitive API
 * - Consistent with Next.js conventions (useRouter, useParams, etc.)
 */

'use client';

import { useSearchFiltersContext } from '@/contexts/SearchFiltersContext';

// Re-export types for convenience
export type { LocationSelection, SearchFilters } from '@/schemas/search';

/**
 * useSearch Hook
 * 
 * Access URL-based search filters and actions.
 * Must be used within SearchFiltersProvider.
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { filters, addLocation, executeSearch } = useSearch();
 *   // ...
 * }
 * ```
 */
export function useSearch() {
  return useSearchFiltersContext();
}
