/**
 * SearchFiltersContext
 * Provides URL-based search filters to all filter components.
 * Uses URL parameters as the single source of truth.
 */

'use client';

import React, { createContext, useContext, ReactNode } from 'react';
import { useSearchFilters, type UseSearchFiltersReturn } from '@/hooks/useSearchFilters';
import type { Country } from '@/lib/dataStore';

// Re-export types for convenience
export type { LocationSelection, SearchFilters } from '@/schemas/search';

const SearchFiltersContext = createContext<UseSearchFiltersReturn | undefined>(undefined);

interface SearchFiltersProviderProps {
  children: ReactNode;
  countries: Country[];
}

export function SearchFiltersProvider({ children, countries }: SearchFiltersProviderProps) {
  const searchFilters = useSearchFilters(countries);

  return (
    <SearchFiltersContext.Provider value={searchFilters}>
      {children}
    </SearchFiltersContext.Provider>
  );
}

export function useSearchFiltersContext(): UseSearchFiltersReturn {
  const context = useContext(SearchFiltersContext);
  if (context === undefined) {
    throw new Error('useSearchFiltersContext must be used within a SearchFiltersProvider');
  }
  return context;
}
