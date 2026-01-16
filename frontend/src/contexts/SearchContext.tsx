'use client';

import React, { createContext, useContext, useState, useMemo, useCallback, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import {
  trackSearchSubmit,
  flushPendingEvents,
} from '@/hooks/useTracking';
// ============================================
// TYPES
// ============================================

export interface LocationSelection {
  type: 'continent' | 'country';
  id: string | number;
  name: string;
  nameHe: string;
}

export interface SearchFilters {
  selectedLocations: LocationSelection[];
  selectedType: number | null;
  selectedThemes: number[];
  selectedYear: string;
  selectedMonth: string;
  minDuration: number;
  maxDuration: number;
  maxBudget: number;
  difficulty: number | null;
}

const DEFAULT_FILTERS: SearchFilters = {
  selectedLocations: [],
  selectedType: null,
  selectedThemes: [],
  selectedYear: 'all',
  selectedMonth: 'all',
  minDuration: 5,
  maxDuration: 30,
  maxBudget: 15000,
  difficulty: null,
};

interface SearchContextType {
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
  loadFilters: (newFilters: Partial<SearchFilters>) => void;
  executeSearch: () => void;
}

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export function SearchProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [filters, setFilters] = useState<SearchFilters>(DEFAULT_FILTERS);

  // Computed: Check if any filters are active (not defaults)
  const hasActiveFilters = useMemo(() => {
    return filters.selectedLocations.length > 0 ||
           filters.selectedType !== null ||
           filters.selectedThemes.length > 0 ||
           filters.selectedYear !== 'all' ||
           filters.selectedMonth !== 'all' ||
           filters.minDuration !== 5 ||
           filters.maxDuration !== 30 ||
           filters.maxBudget !== 15000 ||
           filters.difficulty !== null;
  }, [filters]);

  // Actions: Location management
  const addLocation = useCallback((location: LocationSelection) => {
    setFilters(prev => {
      // Special case: Antarctica - prevent adding as both country and continent
      const isAntarctica = location.name === 'Antarctica' || location.nameHe === 'אנטארקטיקה';
      if (isAntarctica) {
        const antarcticaExists = prev.selectedLocations.some(s => 
          s.name === 'Antarctica' || s.nameHe === 'אנטארקטיקה'
        );
        if (antarcticaExists) {
          return prev; // Already selected, don't add again
        }
      }
      
      // Check if already selected (same type and id)
      const exists = prev.selectedLocations.some(s => 
        s.type === location.type && s.id === location.id
      );
      
      if (exists) {
        return prev;
      }
      
      return {
        ...prev,
        selectedLocations: [...prev.selectedLocations, location],
      };
    });
  }, []);

  const removeLocation = useCallback((index: number) => {
    setFilters(prev => ({
      ...prev,
      selectedLocations: prev.selectedLocations.filter((_, i) => i !== index),
    }));
  }, []);

  // Actions: Trip type
  const setTripType = useCallback((typeId: number | null) => {
    setFilters(prev => ({
      ...prev,
      selectedType: prev.selectedType === typeId ? null : typeId,
    }));
  }, []);

  // Actions: Theme tags (max 3)
  const toggleTheme = useCallback((themeId: number) => {
    setFilters(prev => {
      if (prev.selectedThemes.includes(themeId)) {
        return {
          ...prev,
          selectedThemes: prev.selectedThemes.filter(id => id !== themeId),
        };
      } else if (prev.selectedThemes.length < 3) {
        return {
          ...prev,
          selectedThemes: [...prev.selectedThemes, themeId],
        };
      }
      return prev; // Max 3 themes
    });
  }, []);

  // Actions: Date
  const setDate = useCallback((year: string, month: string) => {
    setFilters(prev => ({
      ...prev,
      selectedYear: year,
      selectedMonth: month,
    }));
  }, []);

  // Actions: Duration
  const setDuration = useCallback((min: number, max: number) => {
    setFilters(prev => ({
      ...prev,
      minDuration: min,
      maxDuration: max,
    }));
  }, []);

  // Actions: Budget
  const setBudget = useCallback((budget: number) => {
    setFilters(prev => ({
      ...prev,
      maxBudget: budget,
    }));
  }, []);

  // Actions: Difficulty
  const setDifficulty = useCallback((difficulty: number | null) => {
    setFilters(prev => ({
      ...prev,
      difficulty: prev.difficulty === difficulty ? null : difficulty,
    }));
  }, []);

  // Actions: Clear all filters
  const clearAllFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  // Actions: Load filters from object (for URL sync)
  const loadFilters = useCallback((newFilters: Partial<SearchFilters>) => {
    setFilters(prev => ({
      ...prev,
      ...newFilters,
    }));
  }, []);

  // Actions: Execute search - navigate to results page
  const executeSearch = useCallback(() => {
    const countriesIds = filters.selectedLocations
      .filter(s => s.type === 'country')
      .map(s => s.id as number)
      .join(',');
    
    const continents = filters.selectedLocations
      .filter(s => s.type === 'continent')
      .map(s => s.name)
      .join(',');

    const params = new URLSearchParams();
    if (countriesIds) params.set('countries', countriesIds);
    if (continents) params.set('continents', continents);
    if (filters.selectedType) params.set('type', filters.selectedType.toString());
    if (filters.selectedThemes.length) params.set('themes', filters.selectedThemes.join(','));
    if (filters.selectedYear !== 'all') params.set('year', filters.selectedYear);
    if (filters.selectedMonth !== 'all') params.set('month', filters.selectedMonth);
    params.set('minDuration', filters.minDuration.toString());
    params.set('maxDuration', filters.maxDuration.toString());
    params.set('budget', filters.maxBudget.toString());
    if (filters.difficulty !== null) params.set('difficulty', filters.difficulty.toString());

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

  const value = useMemo(() => ({
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
    loadFilters,
    executeSearch,
  }), [
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
    loadFilters,
    executeSearch,
  ]);

  return (
    <SearchContext.Provider value={value}>
      {children}
    </SearchContext.Provider>
  );
}

export function useSearchContext(): SearchContextType {
  const context = useContext(SearchContext);
  if (context === undefined) {
    throw new Error('useSearchContext must be used within a SearchProvider');
  }
  return context;
}
