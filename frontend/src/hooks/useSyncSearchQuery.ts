/**
 * useSyncSearchQuery Hook
 * Handles URL parameter serialization/deserialization.
 * Separates URL logic from business logic.
 */

'use client';

import { CONTINENTS } from '@/lib/dataStore';
import type { Country } from '@/lib/dataStore';
import type { SearchFilters, LocationSelection } from '@/contexts/SearchContext';

// ============================================
// SERIALIZATION (Filters -> URL)
// ============================================

export function serializeFiltersToUrl(filters: SearchFilters): URLSearchParams {
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
  params.set('minDuration', filters.minDuration.toString());
  params.set('maxDuration', filters.maxDuration.toString());
  params.set('budget', filters.maxBudget.toString());
  if (filters.difficulty !== null) params.set('difficulty', filters.difficulty.toString());

  return params;
}

// ============================================
// DESERIALIZATION (URL -> Filters)
// ============================================

export function loadFiltersFromUrl(
  searchParams: URLSearchParams,
  countries: Country[]
): Partial<SearchFilters> {
  const countriesParam = searchParams.get('countries');
  const continentsParam = searchParams.get('continents');
  const type = searchParams.get('type');
  const themes = searchParams.get('themes');
  const year = searchParams.get('year');
  const month = searchParams.get('month');
  const minDur = searchParams.get('minDuration');
  const maxDur = searchParams.get('maxDuration');
  const budget = searchParams.get('budget');
  const diff = searchParams.get('difficulty');

  const result: Partial<SearchFilters> = {};

  // Load locations
  if (countriesParam || continentsParam) {
    const newLocations: LocationSelection[] = [];
    const existingIds = new Set<string>();

    if (countriesParam) {
      const countryIds = countriesParam.split(',').map(Number);
      countryIds.forEach(id => {
        const country = countries.find(c => c.id === id);
        const key = `country-${id}`;
        if (country && !existingIds.has(key)) {
          newLocations.push({
            type: 'country',
            id: country.id,
            name: country.name,
            nameHe: country.nameHe
          });
          existingIds.add(key);
        }
      });
    }

    if (continentsParam) {
      const continentNames = continentsParam.split(',');
      continentNames.forEach(name => {
        const continent = CONTINENTS.find(c => c.value === name);
        const key = `continent-${name}`;
        if (continent && !existingIds.has(key)) {
          newLocations.push({
            type: 'continent',
            id: name,
            name: name,
            nameHe: continent.nameHe
          });
          existingIds.add(key);
        }
      });
    }

    if (newLocations.length > 0) {
      result.selectedLocations = newLocations;
    }
  }

  // Load other filters
  if (type) result.selectedType = Number(type);
  if (themes) result.selectedThemes = themes.split(',').map(Number);
  if (year) result.selectedYear = year;
  if (month) result.selectedMonth = month;
  if (minDur) result.minDuration = Math.max(5, Math.min(Number(minDur), 30));
  if (maxDur) result.maxDuration = Math.max(5, Math.min(Number(maxDur), 30));
  if (budget) result.maxBudget = Number(budget);
  if (diff) result.difficulty = Number(diff);

  return result;
}

// ============================================
// HOOK (for convenience)
// ============================================

export function useSyncSearchQuery() {
  // Return stable reference to functions
  return {
    serializeFiltersToUrl,
    loadFiltersFromUrl,
  };
}
