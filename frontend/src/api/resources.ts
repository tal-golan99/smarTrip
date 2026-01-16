/**
 * Resources API endpoints
 * Reference data: countries, guides, tags, trip types
 */

import { apiFetch } from './client';
import {
  CountryArrayResponseSchema,
  CountryResponseSchema,
  GuideArrayResponseSchema,
  GuideResponseSchema,
  TagArrayResponseSchema,
  TripTypeArrayResponseSchema,
  LocationsResponseSchema,
} from '../schemas';
import type { ApiResponse, Country, Guide, Tag, TripType } from './types';

/**
 * Get all countries
 */
export async function getCountries(continent?: string): Promise<ApiResponse<Country[]>> {
  const query = continent ? `?continent=${continent}` : '';
  return apiFetch<Country[]>(`/api/countries${query}`, undefined, 0, CountryArrayResponseSchema);
}

/**
 * Get all locations (countries + continents) for search dropdown
 * This endpoint returns both countries and continents in a single response
 * Backend format: { success: true, countries: [...], continents: [...] }
 */
export async function getLocations(): Promise<ApiResponse<{
  countries: Country[];
  continents: Array<{ value: string; nameHe: string }>;
}>> {
  // The backend returns: { success: true, countries: [...], continents: [...] }
  // apiFetch returns this directly (not wrapped in data field)
  // We need to type assert because ApiResponse doesn't include countries/continents at top level
  const response = await apiFetch<any>('/api/locations', undefined, 0, LocationsResponseSchema) as any as {
    success: boolean;
    countries?: Array<{
      id: number;
      name: string;
      name_he?: string;
      nameHe?: string;
      continent: string;
    }>;
    continents?: Array<{ value: string; nameHe: string }>;
    error?: string;
  };
  
  if (!response || !response.success) {
    return {
      success: false,
      error: response?.error || 'Failed to fetch locations',
    };
  }
  
  // Backend returns countries/continents at top level
  const countries = response.countries || [];
  const continents = response.continents || [];
  
  return {
    success: true,
    data: {
      countries: countries.map((c) => ({
        id: c.id,
        name: c.name,
        nameHe: c.name_he || c.nameHe || c.name,
        continent: c.continent,
        createdAt: '',
        updatedAt: '',
      })),
      continents: continents,
    },
  };
}

/**
 * Get country by ID
 */
export async function getCountry(id: number): Promise<ApiResponse<Country>> {
  return apiFetch<Country>(`/api/countries/${id}`, undefined, 0, CountryResponseSchema);
}

/**
 * Get all guides
 */
export async function getGuides(): Promise<ApiResponse<Guide[]>> {
  return apiFetch<Guide[]>('/api/guides', undefined, 0, GuideArrayResponseSchema);
}

/**
 * Get guide by ID
 */
export async function getGuide(id: number): Promise<ApiResponse<Guide>> {
  return apiFetch<Guide>(`/api/guides/${id}`, undefined, 0, GuideResponseSchema);
}

/**
 * Get all tags
 */
export async function getTags(): Promise<ApiResponse<Tag[]>> {
  return apiFetch<Tag[]>('/api/tags', undefined, 0, TagArrayResponseSchema);
}

/**
 * Get all trip types
 */
export async function getTripTypes(): Promise<ApiResponse<TripType[]>> {
  return apiFetch<TripType[]>('/api/trip-types', undefined, 0, TripTypeArrayResponseSchema);
}
