/**
 * API Client for SmartTrip Flask Backend
 * V2 Schema: Uses TripTemplates + TripOccurrences
 * 
 * Handles all HTTP requests to the Python backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Warn if using localhost in production
if (typeof window !== 'undefined' && API_BASE_URL.includes('localhost') && process.env.NODE_ENV === 'production') {
  console.error('[API] WARNING: Using localhost API URL in production! Set NEXT_PUBLIC_API_URL in Vercel.');
}

// Use V2 API endpoints
const API_VERSION = '/api/v2';

/**
 * Generic API response type
 */
interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  count?: number;
  total?: number;
  error?: string;
  message?: string;
  api_version?: string;
}

/**
 * Get authentication headers (includes Supabase JWT if user is logged in)
 */
async function getAuthHeaders(): Promise<Record<string, string>> {
  try {
    // Only try to get auth token if we're in the browser (client-side)
    if (typeof window === 'undefined') {
      return {}; // Server-side rendering - no auth
    }
    
    // Dynamically import to avoid SSR issues
    const { getAccessToken } = await import('./supabaseClient');
    const token = await getAccessToken();
    
    if (token) {
      return {
        'Authorization': `Bearer ${token}`,
      };
    }
  } catch (error) {
    // Supabase not configured or not available - continue without auth
    // Don't log warnings for missing Supabase config (it's optional)
    if (error instanceof Error && !error.message.includes('Supabase not configured')) {
      console.warn('[API] Could not get auth token:', error);
    }
  }
  
  return {};
}

/**
 * Generic API fetch wrapper with error handling, authentication, timeout, and retry logic
 * Retries network errors (cold starts, timeouts) automatically
 */
async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit,
  retryAttempt = 0
): Promise<ApiResponse<T>> {
  const MAX_RETRIES = 1; // Retry once
  const RETRY_DELAY = 2500; // 2.5 seconds (gives server time to wake up from cold start)
  const TIMEOUT_MS = 30000; // 30 second timeout
  
  let timeoutId: NodeJS.Timeout | null = null;
  let controller: AbortController | null = null;
  
  try {
    // Get auth headers (if user is logged in)
    const authHeaders = await getAuthHeaders();
    
    // Create abort controller for timeout
    controller = new AbortController();
    timeoutId = setTimeout(() => {
      controller?.abort();
    }, TIMEOUT_MS);
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
        ...options?.headers,
      },
    });

    // Clear timeout on successful response
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'API request failed');
    }

    return data;
  } catch (error) {
    // Clear timeout if it wasn't cleared
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
    
    // Determine if error is retryable (network error, timeout, connection refused)
    const isRetryableError = 
      error instanceof Error && (
        error.name === 'AbortError' || // Timeout
        error.message.includes('fetch') || // Network error
        error.message.includes('Failed to fetch') || // Chrome/Firefox network error
        error.message.includes('NetworkError') || // Firefox network error
        error.message.includes('Network request failed') || // React Native
        error.message.toLowerCase().includes('connection') || // Connection errors
        error.message.toLowerCase().includes('refused') || // Connection refused
        error.message.toLowerCase().includes('timeout') // Timeout errors
      );
    
    // If it's a retryable error AND we haven't exceeded max retries, retry
    if (isRetryableError && retryAttempt < MAX_RETRIES) {
      console.log(`[API] Network error detected, retrying in ${RETRY_DELAY}ms... (attempt ${retryAttempt + 1}/${MAX_RETRIES + 1})`);
      
      // Wait before retrying (gives server time to wake up from cold start)
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
      
      // Retry the request
      return apiFetch<T>(endpoint, options, retryAttempt + 1);
    }
    
    // Not retryable, or max retries exceeded - return error
    console.error('API Error:', error);
    
    // Provide user-friendly error message
    let errorMessage = 'Unknown error occurred';
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        errorMessage = 'Request timeout - server is taking too long to respond';
      } else if (isRetryableError) {
        errorMessage = 'Cannot connect to server - please try again in a moment';
      } else {
        errorMessage = error.message;
      }
    }
    
    return {
      success: false,
      error: errorMessage,
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
  category: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TripType {
  id: number;
  name: string;
  nameHe: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

// V2: Company (NEW)
export interface Company {
  id: number;
  name: string;
  nameHe: string;
  description?: string;
  descriptionHe?: string;
  logoUrl?: string;
  websiteUrl?: string;
  email?: string;
  phone?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// V2: Trip Template (trip definition)
export interface TripTemplate {
  id: number;
  title: string;
  titleHe: string;
  description: string;
  descriptionHe: string;
  shortDescription?: string;
  shortDescriptionHe?: string;
  imageUrl?: string;
  basePrice: number;
  singleSupplementPrice?: number;
  typicalDurationDays: number;
  defaultMaxCapacity: number;
  difficultyLevel: 1 | 2 | 3 | 4 | 5;
  companyId: number;
  tripTypeId?: number;
  primaryCountryId?: number;
  isActive: boolean;
  properties?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  // Relations
  company?: Company;
  tripType?: TripType;
  primaryCountry?: Country;
  countries?: Country[];
  tags?: Tag[];
  occurrences?: TripOccurrence[];
}

// V2: Trip Occurrence (scheduled instance)
export interface TripOccurrence {
  id: number;
  tripTemplateId: number;
  guideId?: number;
  startDate: string;
  endDate: string;
  priceOverride?: number;
  singleSupplementOverride?: number;
  maxCapacityOverride?: number;
  spotsLeft: number;
  status: 'Open' | 'Guaranteed' | 'Last Places' | 'Full' | 'Cancelled';
  imageUrlOverride?: string;
  notes?: string;
  notesHe?: string;
  properties?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  // Computed
  effectivePrice?: number;
  effectiveMaxCapacity?: number;
  effectiveImageUrl?: string;
  durationDays?: number;
  // Relations
  template?: TripTemplate;
  guide?: Guide;
}

// Backward Compatible Trip Interface (maps occurrence to old format)
export interface Trip {
  id: number;
  templateId?: number;  // NEW: Link to template
  title: string;
  titleHe: string;
  title_he?: string;  // snake_case alias
  description: string;
  descriptionHe: string;
  description_he?: string;  // snake_case alias
  imageUrl?: string;
  image_url?: string;  // snake_case alias
  startDate: string;
  start_date?: string;  // snake_case alias
  endDate: string;
  end_date?: string;  // snake_case alias
  price: number;
  singleSupplementPrice?: number;
  single_supplement_price?: number;  // snake_case alias
  maxCapacity: number;
  max_capacity?: number;  // snake_case alias
  spotsLeft: number;
  spots_left?: number;  // snake_case alias
  status: 'Open' | 'Guaranteed' | 'Last Places' | 'Full' | 'Cancelled';
  difficultyLevel: 1 | 2 | 3;
  difficulty_level?: number;  // snake_case alias
  countryId: number;
  country_id?: number;  // snake_case alias
  guideId?: number;
  guide_id?: number;  // snake_case alias
  tripTypeId?: number;
  trip_type_id?: number;  // snake_case alias
  companyId?: number;  // NEW
  company_id?: number;  // NEW snake_case alias
  createdAt: string;
  updatedAt: string;
  // Optional relations
  country?: Country;
  guide?: Guide;
  tripType?: TripType;
  trip_type?: TripType;  // snake_case alias
  company?: Company;  // NEW
  tags?: Tag[];
}

export interface TripFilters {
  country_id?: number;
  guide_id?: number;
  tag_id?: number;
  trip_type_id?: number;
  status?: string;
  difficulty?: number;
  start_date?: string;
  end_date?: string;
  year?: number;
  month?: number;
  include_relations?: boolean;
  limit?: number;
  offset?: number;
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
  year?: number | string;             // Year filter
  month?: number | string;            // Month filter (1-12)
}

export interface RecommendedTrip extends Trip {
  match_score: number;                // 0-100 score
  match_details: string[];            // List of match reasons
  is_relaxed?: boolean;               // True if from relaxed criteria
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
 * Get all trip types
 */
export async function getTripTypes(): Promise<ApiResponse<TripType[]>> {
  return apiFetch<TripType[]>('/api/trip-types');
}

// ============================================
// V2 API: COMPANIES
// ============================================

/**
 * Get all companies
 */
export async function getCompanies(): Promise<ApiResponse<Company[]>> {
  return apiFetch<Company[]>(`${API_VERSION}/companies`);
}

/**
 * Get company by ID
 */
export async function getCompany(id: number): Promise<ApiResponse<Company>> {
  return apiFetch<Company>(`${API_VERSION}/companies/${id}`);
}

// ============================================
// V2 API: TRIP TEMPLATES
// ============================================

/**
 * Get all trip templates with optional filters
 */
export async function getTemplates(filters?: {
  company_id?: number;
  trip_type_id?: number;
  country_id?: number;
  difficulty?: number;
  include_occurrences?: boolean;
  limit?: number;
  offset?: number;
}): Promise<ApiResponse<TripTemplate[]>> {
  const params = new URLSearchParams();
  
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, String(value));
      }
    });
  }
  
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiFetch<TripTemplate[]>(`${API_VERSION}/templates${query}`);
}

/**
 * Get template by ID with full details
 */
export async function getTemplate(id: number): Promise<ApiResponse<TripTemplate>> {
  return apiFetch<TripTemplate>(`${API_VERSION}/templates/${id}`);
}

// ============================================
// V2 API: TRIP OCCURRENCES
// ============================================

/**
 * Get all trip occurrences with optional filters
 */
export async function getOccurrences(filters?: {
  template_id?: number;
  guide_id?: number;
  status?: string;
  start_date?: string;
  end_date?: string;
  year?: number;
  month?: number;
  max_price?: number;
  include_template?: boolean;
  limit?: number;
  offset?: number;
}): Promise<ApiResponse<TripOccurrence[]>> {
  const params = new URLSearchParams();
  
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, String(value));
      }
    });
  }
  
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiFetch<TripOccurrence[]>(`${API_VERSION}/occurrences${query}`);
}

/**
 * Get occurrence by ID with full details
 */
export async function getOccurrence(id: number): Promise<ApiResponse<TripOccurrence>> {
  return apiFetch<TripOccurrence>(`${API_VERSION}/occurrences/${id}`);
}

// ============================================
// V2 API: TRIPS (Backward Compatible)
// ============================================

/**
 * Get all trips with optional filters (V2 - backward compatible)
 * Returns occurrences formatted as Trip objects
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
  // Use V2 trips endpoint (backward compatible)
  return apiFetch<Trip[]>(`${API_VERSION}/trips${query}`);
}

/**
 * Get trip by ID with full details (V2 - backward compatible)
 * Returns occurrence formatted as Trip object
 */
export async function getTrip(id: number): Promise<ApiResponse<Trip>> {
  // Use V2 trips endpoint (backward compatible)
  return apiFetch<Trip>(`${API_VERSION}/trips/${id}`);
}

/**
 * Get personalized trip recommendations (V2)
 * Returns trips sorted by match score (0-100)
 */
export async function getRecommendations(
  preferences: RecommendationPreferences
): Promise<ApiResponse<RecommendedTrip[]>> {
  // Use V2 recommendations endpoint
  return apiFetch<RecommendedTrip[]>(`${API_VERSION}/recommendations`, {
    method: 'POST',
    body: JSON.stringify(preferences),
  });
}

// ============================================
// V2 API: SCHEMA INFO
// ============================================

/**
 * Get V2 schema information and statistics
 */
export async function getSchemaInfo(): Promise<ApiResponse<{
  schema_version: string;
  statistics: {
    companies: number;
    templates: number;
    occurrences: number;
    active_occurrences: number;
  };
  endpoints: Record<string, string>;
}>> {
  return apiFetch(`${API_VERSION}/schema-info`);
}
