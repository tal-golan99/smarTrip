/**
 * Search-related types and schemas
 * 
 * These are client-side types for search filters and location selections.
 * Unlike other schemas in this folder, these don't have Zod schemas yet
 * as they represent client-side state, not API responses.
 */

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

export const DEFAULT_FILTERS: SearchFilters = {
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
