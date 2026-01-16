/**
 * TypeScript type definitions inferred from Zod schemas
 * 
 * All types are derived from schemas using z.infer<typeof Schema>
 * This ensures types and validation schemas never go out of sync.
 * 
 * Schema-first approach: Define schemas first, infer types from them.
 */

import {
  BaseCountrySchema,
  BaseTripTypeSchema,
  BaseTagSchema,
  CountrySchema,
  GuideSchema,
  TagSchema,
  TripTypeSchema,
  CompanySchema,
  TripTemplateSchema,
  TripOccurrenceSchema,
  RecommendedTripOccurrenceSchema,
} from '../schemas';
import type { z } from 'zod';

// ============================================
// BASE TYPES (inferred from base schemas)
// ============================================

export type BaseCountry = z.infer<typeof BaseCountrySchema>;
export type BaseTripType = z.infer<typeof BaseTripTypeSchema>;
export type BaseTag = z.infer<typeof BaseTagSchema>;

// ============================================
// ENTITY TYPES (inferred from entity schemas)
// ============================================

export type Country = z.infer<typeof CountrySchema>;
export type Guide = z.infer<typeof GuideSchema>;
export type Tag = z.infer<typeof TagSchema>;
export type TripType = z.infer<typeof TripTypeSchema>;
export type Company = z.infer<typeof CompanySchema>;
export type TripTemplate = z.infer<typeof TripTemplateSchema>;
export type TripOccurrence = z.infer<typeof TripOccurrenceSchema>;
export type RecommendedTripOccurrence = z.infer<typeof RecommendedTripOccurrenceSchema>;

// ============================================
// GENERIC API RESPONSE TYPE
// ============================================

/**
 * Generic API response type
 * Note: This is a manual type since it's used as a generic wrapper
 */
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  count?: number;
  total?: number;
  error?: string;
  message?: string;
  api_version?: string;
}

// ============================================
// FILTER AND PREFERENCE TYPES
// ============================================

/**
 * TripFilters - Query parameters use snake_case (REST convention)
 * Note: These are manual types since they're not API response schemas
 */
export interface TripFilters {
  country_id?: number;  // Query param - snake_case
  guide_id?: number;    // Query param - snake_case
  tag_id?: number;      // Query param - snake_case
  trip_type_id?: number; // Query param - snake_case
  status?: string;
  difficulty?: number;
  start_date?: string;  // Query param - snake_case
  end_date?: string;    // Query param - snake_case
  year?: number;
  month?: number;
  include_relations?: boolean; // Query param - snake_case
  limit?: number;
  offset?: number;
}

/**
 * RecommendationPreferences - User preferences for recommendations (camelCase for frontend)
 * Note: These are manual types since they're request body, not API response schemas
 */
export interface RecommendationPreferences {
  selectedCountries?: number[];      // Optional list of country IDs
  selectedContinents?: string[];     // Optional list of continent names
  preferredTypeId?: number;         // Single TYPE tag ID (trip style)
  preferredThemeIds?: number[];     // Up to 3 THEME tag IDs (trip content)
  minDuration?: number;              // Minimum days
  maxDuration?: number;              // Maximum days
  budget?: number;                    // Maximum budget in ILS/USD
  difficulty?: number;                // 1=Easy, 2=Moderate, 3=Hard
  startDate?: string;                // ISO date string (YYYY-MM-DD)
  year?: number | string;             // Year filter
  month?: number | string;            // Month filter (1-12)
}
