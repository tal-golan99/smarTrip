/**
 * useSearchFilters Hook
 * URL-based state management for search filters.
 * Uses URL parameters as the single source of truth.
 * 
 * Benefits:
 * - No dual state management (URL is the only source)
 * - No sync issues between Context and URL
 * - Shareable URLs work automatically
 * - Browser back/forward works automatically
 * - Simpler code with fewer moving parts
 */

'use client';

import { useMemo, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { CONTINENTS } from '@/lib/dataStore';
import type { Country } from '@/lib/dataStore';
import { DEFAULT_FILTERS } from '@/schemas/search';
import type { SearchFilters, LocationSelection } from '@/schemas/search';
import {
  trackSearchSubmit,
  flushPendingEvents,
} from '@/hooks/useTracking';

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Parse location selections from URL parameters
 */
function parseLocations(
  countriesParam: string | null,
  continentsParam: string | null,
  countries: Country[]
): LocationSelection[] {
  const locations: LocationSelection[] = [];
  const existingIds = new Set<string>();

  // Parse countries
  if (countriesParam) {
    const countryIds = countriesParam.split(',').map(Number).filter(id => !isNaN(id));
    countryIds.forEach(id => {
      const country = countries.find(c => c.id === id);
      const key = `country-${id}`;
      if (country && !existingIds.has(key)) {
        locations.push({
          type: 'country',
          id: country.id,
          name: country.name,
          nameHe: country.nameHe
        });
        existingIds.add(key);
      }
    });
  }

  // Parse continents
  if (continentsParam) {
    const continentNames = continentsParam.split(',');
    continentNames.forEach(name => {
      const continent = CONTINENTS.find(c => c.value === name);
      const key = `continent-${name}`;
      if (continent && !existingIds.has(key)) {
        locations.push({
          type: 'continent',
          id: name,
          name: name,
          nameHe: continent.nameHe
        });
        existingIds.add(key);
      }
    });
  }

  return locations;
}

/**
 * Parse filters from URL parameters
 */
function parseFiltersFromUrl(
  searchParams: URLSearchParams,
  countries: Country[]
): SearchFilters {
  const countriesParam = searchParams.get('countries');
  const continentsParam = searchParams.get('continents');
  const typeParam = searchParams.get('type');
  const themesParam = searchParams.get('themes');
  const yearParam = searchParams.get('year');
  const monthParam = searchParams.get('month');
  const minDurParam = searchParams.get('minDuration');
  const maxDurParam = searchParams.get('maxDuration');
  const budgetParam = searchParams.get('budget');
  const diffParam = searchParams.get('difficulty');

  return {
    selectedLocations: parseLocations(countriesParam, continentsParam, countries),
    selectedType: typeParam ? Number(typeParam) : null,
    selectedThemes: themesParam ? themesParam.split(',').map(Number).filter(id => !isNaN(id)) : [],
    selectedYear: yearParam || 'all',
    selectedMonth: monthParam || 'all',
    minDuration: minDurParam ? Math.max(5, Math.min(Number(minDurParam), 30)) : DEFAULT_FILTERS.minDuration,
    maxDuration: maxDurParam ? Math.max(5, Math.min(Number(maxDurParam), 30)) : DEFAULT_FILTERS.maxDuration,
    maxBudget: budgetParam ? Number(budgetParam) : DEFAULT_FILTERS.maxBudget,
    difficulty: diffParam ? Number(diffParam) : null,
  };
}

/**
 * Serialize filters to URL parameters
 */
function serializeFiltersToUrl(filters: SearchFilters): URLSearchParams {
  const params = new URLSearchParams();
  
  const countriesIds = filters.selectedLocations
    .filter(s => s.type === 'country')
    .map(s => s.id as number)
    .join(',');
  
  const continents = filters.selectedLocations
    .filter(s => s.type === 'continent')
    .map(s => s.name)
    .join(',');

  if (countriesIds) params.set('countries', countriesIds);
  if (continents) params.set('continents', continents);
  if (filters.selectedType) params.set('type', filters.selectedType.toString());
  if (filters.selectedThemes.length) params.set('themes', filters.selectedThemes.join(','));
  if (filters.selectedYear !== 'all') params.set('year', filters.selectedYear);
  if (filters.selectedMonth !== 'all') params.set('month', filters.selectedMonth);
  
  // Only include duration if not default
  if (filters.minDuration !== DEFAULT_FILTERS.minDuration) {
    params.set('minDuration', filters.minDuration.toString());
  }
  if (filters.maxDuration !== DEFAULT_FILTERS.maxDuration) {
    params.set('maxDuration', filters.maxDuration.toString());
  }
  
  // Only include budget if not default
  if (filters.maxBudget !== DEFAULT_FILTERS.maxBudget) {
    params.set('budget', filters.maxBudget.toString());
  }
  
  if (filters.difficulty !== null) params.set('difficulty', filters.difficulty.toString());

  return params;
}

// ============================================
// HOOK
// ============================================

export interface UseSearchFiltersReturn {
  filters: SearchFilters;
  hasActiveFilters: boolean;
  addLocation: (location: LocationSelection) => void;
  removeLocation: (index: number) => void;
  setTripType: (typeId: number | null) => void;
  toggleTheme: (themeId: number) => void;
  setDate: (year: string, month: string) => void;
  setDuration: (min: number, max: number) => void;
  setBudget: (budget: number) => void;
  setDifficulty: (difficulty: number | null) => void;
  clearAllFilters: () => void;
  executeSearch: () => void;
}

/**
 * useSearchFilters Hook
 * 
 * Manages search filters using URL parameters as the single source of truth.
 * This is the core implementation that requires countries data.
 * 
 * For a simpler API without params, use useSearch() instead.
 * 
 * @param countries - List of countries for parsing location selections
 */
export function useSearchFilters(countries: Country[]): UseSearchFiltersReturn {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Read filters from URL (single source of truth)
  const filters = useMemo(() => {
    return parseFiltersFromUrl(searchParams, countries);
  }, [searchParams, countries]);

  // Computed: Check if any filters are active (not defaults)
  const hasActiveFilters = useMemo(() => {
    return filters.selectedLocations.length > 0 ||
           filters.selectedType !== null ||
           filters.selectedThemes.length > 0 ||
           filters.selectedYear !== 'all' ||
           filters.selectedMonth !== 'all' ||
           filters.minDuration !== DEFAULT_FILTERS.minDuration ||
           filters.maxDuration !== DEFAULT_FILTERS.maxDuration ||
           filters.maxBudget !== DEFAULT_FILTERS.maxBudget ||
           filters.difficulty !== null;
  }, [filters]);

  // Helper: Update URL with new filters
  const updateUrl = useCallback((newFilters: SearchFilters, replace: boolean = false) => {
    const params = serializeFiltersToUrl(newFilters);
    const url = `/search?${params.toString()}`;
    
    if (replace) {
      router.replace(url);
    } else {
      router.push(url);
    }
  }, [router]);

  // Action: Add location
  const addLocation = useCallback((location: LocationSelection) => {
    // Special case: Antarctica - prevent adding as both country and continent
    const isAntarctica = location.name === 'Antarctica' || location.nameHe === 'אנטארקטיקה';
    if (isAntarctica) {
      const antarcticaExists = filters.selectedLocations.some(s => 
        s.name === 'Antarctica' || s.nameHe === 'אנטארקטיקה'
      );
      if (antarcticaExists) {
        return; // Already selected, don't add again
      }
    }
    
    // Check if already selected (same type and id)
    const exists = filters.selectedLocations.some(s => 
      s.type === location.type && s.id === location.id
    );
    
    if (exists) {
      return;
    }
    
    const newFilters = {
      ...filters,
      selectedLocations: [...filters.selectedLocations, location],
    };
    updateUrl(newFilters, true); // Use replace to avoid cluttering history
  }, [filters, updateUrl]);

  // Action: Remove location
  const removeLocation = useCallback((index: number) => {
    const newFilters = {
      ...filters,
      selectedLocations: filters.selectedLocations.filter((_, i) => i !== index),
    };
    updateUrl(newFilters, true);
  }, [filters, updateUrl]);

  // Action: Set trip type
  const setTripType = useCallback((typeId: number | null) => {
    const newFilters = {
      ...filters,
      selectedType: filters.selectedType === typeId ? null : typeId,
    };
    updateUrl(newFilters, true);
  }, [filters, updateUrl]);

  // Action: Toggle theme
  const toggleTheme = useCallback((themeId: number) => {
    let newThemes: number[];
    
    if (filters.selectedThemes.includes(themeId)) {
      newThemes = filters.selectedThemes.filter(id => id !== themeId);
    } else if (filters.selectedThemes.length < 3) {
      newThemes = [...filters.selectedThemes, themeId];
    } else {
      return; // Max 3 themes
    }
    
    const newFilters = {
      ...filters,
      selectedThemes: newThemes,
    };
    updateUrl(newFilters, true);
  }, [filters, updateUrl]);

  // Action: Set date
  const setDate = useCallback((year: string, month: string) => {
    const newFilters = {
      ...filters,
      selectedYear: year,
      selectedMonth: month,
    };
    updateUrl(newFilters, true);
  }, [filters, updateUrl]);

  // Action: Set duration
  const setDuration = useCallback((min: number, max: number) => {
    const newFilters = {
      ...filters,
      minDuration: min,
      maxDuration: max,
    };
    updateUrl(newFilters, true);
  }, [filters, updateUrl]);

  // Action: Set budget
  const setBudget = useCallback((budget: number) => {
    const newFilters = {
      ...filters,
      maxBudget: budget,
    };
    updateUrl(newFilters, true);
  }, [filters, updateUrl]);

  // Action: Set difficulty
  const setDifficulty = useCallback((difficulty: number | null) => {
    const newFilters = {
      ...filters,
      difficulty: filters.difficulty === difficulty ? null : difficulty,
    };
    updateUrl(newFilters, true);
  }, [filters, updateUrl]);

  // Action: Clear all filters
  const clearAllFilters = useCallback(() => {
    router.replace('/search');
  }, [router]);

  // Action: Execute search - navigate to results page
  const executeSearch = useCallback(() => {
    const countriesIds = filters.selectedLocations
      .filter(s => s.type === 'country')
      .map(s => s.id as number)
      .join(',');
    
    const continents = filters.selectedLocations
      .filter(s => s.type === 'continent')
      .map(s => s.name)
      .join(',');

    const params = serializeFiltersToUrl(filters);

    // Track search submission
    const preferences = {
      countries: countriesIds ? countriesIds.split(',').map(Number) : [],
      continents: continents ? continents.split(',') : [],
      type: filters.selectedType,
      themes: filters.selectedThemes,
      year: filters.selectedYear,
      month: filters.selectedMonth,
      minDuration: filters.minDuration,
      maxDuration: filters.maxDuration,
      budget: filters.maxBudget,
      difficulty: filters.difficulty,
    };
    
    // Classify search type
    const filterCount = [
      countriesIds, 
      continents, 
      filters.selectedType, 
      filters.selectedThemes.length > 0,
      filters.selectedYear !== 'all',
      filters.selectedMonth !== 'all',
      filters.difficulty !== null
    ].filter(Boolean).length;
    
    const searchType = filterCount >= 2 ? 'focused_search' : 'exploration';
    trackSearchSubmit(preferences, searchType);
    
    // Flush events before navigation
    flushPendingEvents();

    router.push(`/search/results?${params.toString()}`);
  }, [filters, router]);

  return {
    filters,
    hasActiveFilters,
    addLocation,
    removeLocation,
    setTripType,
    toggleTheme,
    setDate,
    setDuration,
    setBudget,
    setDifficulty,
    clearAllFilters,
    executeSearch,
  };
}
