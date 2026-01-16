/**
 * V2 API endpoints
 * Templates, occurrences, trips, recommendations, companies
 */

import { apiFetch, camelToSnake, camelToSnakeObject, API_VERSION } from './client';
import {
  CompanyArrayResponseSchema,
  CompanyResponseSchema,
  TripTemplateArrayResponseSchema,
  TripTemplateResponseSchema,
  TripOccurrenceArrayResponseSchema,
  TripOccurrenceResponseSchema,
  RecommendedTripOccurrenceArrayResponseSchema,
  SchemaInfoResponseSchema,
} from '../schemas';
import type { 
  ApiResponse, 
  Company, 
  TripTemplate, 
  TripOccurrence, 
  TripFilters,
  RecommendationPreferences,
  RecommendedTripOccurrence
} from './types';

/**
 * Get all companies
 */
export async function getCompanies(): Promise<ApiResponse<Company[]>> {
  return apiFetch<Company[]>(`${API_VERSION}/companies`, undefined, 0, CompanyArrayResponseSchema);
}

/**
 * Get company by ID
 */
export async function getCompany(id: number): Promise<ApiResponse<Company>> {
  return apiFetch<Company>(`${API_VERSION}/companies/${id}`, undefined, 0, CompanyResponseSchema);
}

/**
 * Get all trip templates with optional filters
 * Note: Query parameters use snake_case (REST convention)
 */
export async function getTemplates(filters?: {
  companyId?: number;
  tripTypeId?: number;
  countryId?: number;
  difficulty?: number;
  includeOccurrences?: boolean;
  limit?: number;
  offset?: number;
}): Promise<ApiResponse<TripTemplate[]>> {
  const params = new URLSearchParams();
  
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        // Convert camelCase to snake_case for query params
        const snakeKey = camelToSnake(key);
        params.append(snakeKey, String(value));
      }
    });
  }
  
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiFetch<TripTemplate[]>(`${API_VERSION}/templates${query}`, undefined, 0, TripTemplateArrayResponseSchema);
}

/**
 * Get template by ID with full details
 */
export async function getTemplate(id: number): Promise<ApiResponse<TripTemplate>> {
  return apiFetch<TripTemplate>(`${API_VERSION}/templates/${id}`, undefined, 0, TripTemplateResponseSchema);
}

/**
 * Get all trip occurrences with optional filters
 * Note: Query parameters use snake_case (REST convention)
 */
export async function getOccurrences(filters?: {
  templateId?: number;
  guideId?: number;
  status?: string;
  startDate?: string;
  endDate?: string;
  year?: number;
  month?: number;
  maxPrice?: number;
  includeTemplate?: boolean;
  limit?: number;
  offset?: number;
}): Promise<ApiResponse<TripOccurrence[]>> {
  const params = new URLSearchParams();
  
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        // Convert camelCase to snake_case for query params
        const snakeKey = camelToSnake(key);
        params.append(snakeKey, String(value));
      }
    });
  }
  
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiFetch<TripOccurrence[]>(`${API_VERSION}/occurrences${query}`, undefined, 0, TripOccurrenceArrayResponseSchema);
}

/**
 * Get occurrence by ID with full details
 */
export async function getOccurrence(id: number): Promise<ApiResponse<TripOccurrence>> {
  return apiFetch<TripOccurrence>(`${API_VERSION}/occurrences/${id}`, undefined, 0, TripOccurrenceResponseSchema);
}

/**
 * Get all trips (occurrences) with optional filters
 * Returns occurrences using TripOccurrenceSchema
 */
export async function getTripOccurrences(filters?: TripFilters): Promise<ApiResponse<TripOccurrence[]>> {
  const params = new URLSearchParams();
  
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, String(value));
      }
    });
  }
  
  const query = params.toString() ? `?${params.toString()}` : '';
  // Use V2 trip-occurrences endpoint
  return apiFetch<TripOccurrence[]>(`${API_VERSION}/trip-occurrences${query}`, undefined, 0, TripOccurrenceArrayResponseSchema);
}

/**
 * Get trip occurrence by ID with full details
 */
export async function getTripOccurrence(id: number): Promise<ApiResponse<TripOccurrence>> {
  // Get a single trip occurrence by ID
  return apiFetch<TripOccurrence>(`${API_VERSION}/occurrences/${id}`, undefined, 0, TripOccurrenceResponseSchema);
}

/**
 * Get personalized trip recommendations (V2)
 * Returns trips sorted by match score (0-100)
 * Note: Request body is converted to snake_case for backend compatibility
 */
export async function getRecommendations(
  preferences: RecommendationPreferences
): Promise<ApiResponse<RecommendedTripOccurrence[]>> {
  // Convert camelCase to snake_case for request body
  const requestBody = camelToSnakeObject(preferences);
  
  // Use V2 recommendations endpoint
  return apiFetch<RecommendedTripOccurrence[]>(
    `${API_VERSION}/recommendations`,
    {
      method: 'POST',
      body: JSON.stringify(requestBody),
    },
    0,
    RecommendedTripOccurrenceArrayResponseSchema
  );
}

/**
 * Get V2 schema information and statistics
 */
export async function getSchemaInfo(): Promise<ApiResponse<{
  schemaVersion: string;
  statistics: {
    companies: number;
    templates: number;
    occurrences: number;
    activeOccurrences: number;
  };
  endpoints: Record<string, string>;
}>> {
  // Backend returns data at top level: { success: true, schema_version: '2.3', statistics: {...}, endpoints: {...} }
  const response = await apiFetch<any>(`${API_VERSION}/schema-info`, undefined, 0, SchemaInfoResponseSchema) as any;

  if (!response.success) {
    return {
      success: false,
      error: response.error || 'Failed to get schema info',
    };
  }

  // Map snake_case to camelCase and wrap in standard ApiResponse format
  return {
    success: true,
    data: {
      schemaVersion: response.schema_version,
      statistics: {
        companies: response.statistics?.companies || 0,
        templates: response.statistics?.templates || 0,
        occurrences: response.statistics?.occurrences || 0,
        activeOccurrences: response.statistics?.active_occurrences || 0,
      },
      endpoints: response.endpoints || {},
    },
  };
}
