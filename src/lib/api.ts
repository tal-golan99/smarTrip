/**
 * API Client for SmartTrip Flask Backend
 * Handles all HTTP requests to the Python backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

/**
 * Generic API response type
 */
interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  count?: number;
  error?: string;
  message?: string;
}

/**
 * Generic API fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'API request failed');
    }

    return data;
  } catch (error) {
    console.error('API Error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
}

// ============================================
// TYPE DEFINITIONS
// ============================================

export interface Country {
  id: number;
  name: string;
  nameHe: string;
  continent: string;
  createdAt: string;
  updatedAt: string;
}

export interface Guide {
  id: number;
  name: string;
  email: string;
  phone?: string;
  gender: string;
  age?: number;
  bio?: string;
  bioHe?: string;
  imageUrl?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Tag {
  id: number;
  name: string;
  nameHe: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Trip {
  id: number;
  title: string;
  titleHe: string;
  description: string;
  descriptionHe: string;
  imageUrl?: string;
  startDate: string;
  endDate: string;
  price: number;
  singleSupplementPrice?: number;
  maxCapacity: number;
  spotsLeft: number;
  status: 'Open' | 'Guaranteed' | 'Last Places' | 'Full' | 'Cancelled';
  difficultyLevel: 1 | 2 | 3;
  countryId: number;
  guideId: number;
  createdAt: string;
  updatedAt: string;
  // Optional relations (when include_relations=true)
  country?: Country;
  guide?: Guide;
  tags?: Tag[];
}

export interface TripFilters {
  country_id?: number;
  guide_id?: number;
  tag_id?: number;
  status?: string;
  difficulty?: number;
  start_date?: string;
  end_date?: string;
  include_relations?: boolean;
}

export interface RecommendationPreferences {
  selected_countries?: number[];      // Optional list of country IDs
  selected_continents?: string[];     // Optional list of continent names
  preferred_type_id?: number;         // Single TYPE tag ID (trip style)
  preferred_theme_ids?: number[];     // Up to 3 THEME tag IDs (trip content)
  min_duration?: number;              // Minimum days
  max_duration?: number;              // Maximum days
  budget?: number;                    // Maximum budget in ILS/USD
  difficulty?: number;                // 1=Easy, 2=Moderate, 3=Hard
  start_date?: string;                // ISO date string (YYYY-MM-DD)
}

export interface RecommendedTrip extends Trip {
  match_score: number;                // 0-100 score
  match_details: string[];            // List of match reasons
}

// ============================================
// API FUNCTIONS
// ============================================

/**
 * Health check
 */
export async function healthCheck() {
  return apiFetch('/api/health');
}

/**
 * Get all countries
 */
export async function getCountries(continent?: string): Promise<ApiResponse<Country[]>> {
  const query = continent ? `?continent=${continent}` : '';
  return apiFetch<Country[]>(`/api/countries${query}`);
}

/**
 * Get country by ID
 */
export async function getCountry(id: number): Promise<ApiResponse<Country>> {
  return apiFetch<Country>(`/api/countries/${id}`);
}

/**
 * Get all guides
 */
export async function getGuides(): Promise<ApiResponse<Guide[]>> {
  return apiFetch<Guide[]>('/api/guides');
}

/**
 * Get guide by ID
 */
export async function getGuide(id: number): Promise<ApiResponse<Guide>> {
  return apiFetch<Guide>(`/api/guides/${id}`);
}

/**
 * Get all tags
 */
export async function getTags(): Promise<ApiResponse<Tag[]>> {
  return apiFetch<Tag[]>('/api/tags');
}

/**
 * Get all trips with optional filters
 */
export async function getTrips(filters?: TripFilters): Promise<ApiResponse<Trip[]>> {
  const params = new URLSearchParams();
  
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, String(value));
      }
    });
  }
  
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiFetch<Trip[]>(`/api/trips${query}`);
}

/**
 * Get trip by ID with full details
 */
export async function getTrip(id: number): Promise<ApiResponse<Trip>> {
  return apiFetch<Trip>(`/api/trips/${id}`);
}

/**
 * Get personalized trip recommendations with weighted scoring
 * Returns trips sorted by match score (0-100)
 */
export async function getRecommendations(
  preferences: RecommendationPreferences
): Promise<ApiResponse<RecommendedTrip[]>> {
  return apiFetch<RecommendedTrip[]>('/api/recommendations', {
    method: 'POST',
    body: JSON.stringify(preferences),
  });
}


