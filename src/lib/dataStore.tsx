/**
 * Centralized Data Store (Phase 1)
 * =================================
 * 
 * Single source of truth for reference data from the backend.
 * Eliminates the need for hardcoded fallback IDs in components.
 * 
 * Features:
 * - Caches data from backend API
 * - Provides React hooks for data access
 * - Handles loading and error states
 * - No hardcoded IDs - always fetches from backend
 */

'use client';

import React, { useState, useEffect, useCallback, createContext, useContext, ReactNode } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// ============================================
// TYPE DEFINITIONS
// ============================================

export interface Country {
  id: number;
  name: string;
  nameHe: string;
  continent: string;
}

export interface TripType {
  id: number;
  name: string;
  nameHe: string;
  description?: string;
}

export interface ThemeTag {
  id: number;
  name: string;
  nameHe: string;
  category: string;
}

interface DataStoreState {
  // Data
  countries: Country[];
  tripTypes: TripType[];
  themeTags: ThemeTag[];
  
  // Loading states
  isLoadingCountries: boolean;
  isLoadingTripTypes: boolean;
  isLoadingThemeTags: boolean;
  
  // Error states
  countriesError: string | null;
  tripTypesError: string | null;
  themeTagsError: string | null;
  
  // Cold start detection
  isColdStart: boolean;
  retryCount: number;
  
  // Computed
  isLoading: boolean;
  hasError: boolean;
}

interface DataStoreActions {
  refreshCountries: () => Promise<void>;
  refreshTripTypes: () => Promise<void>;
  refreshThemeTags: () => Promise<void>;
  refreshAll: () => Promise<void>;
  
  // Helper functions
  getCountryById: (id: number) => Country | undefined;
  getTripTypeById: (id: number) => TripType | undefined;
  getThemeTagById: (id: number) => ThemeTag | undefined;
  getCountriesByContinent: (continent: string) => Country[];
}

type DataStore = DataStoreState & DataStoreActions;

// ============================================
// CONTEXT
// ============================================

const DataStoreContext = createContext<DataStore | null>(null);

// ============================================
// PROVIDER COMPONENT
// ============================================

export function DataStoreProvider({ children }: { children: ReactNode }) {
  // State
  const [countries, setCountries] = useState<Country[]>([]);
  const [tripTypes, setTripTypes] = useState<TripType[]>([]);
  const [themeTags, setThemeTags] = useState<ThemeTag[]>([]);
  
  const [isLoadingCountries, setIsLoadingCountries] = useState(true);
  const [isLoadingTripTypes, setIsLoadingTripTypes] = useState(true);
  const [isLoadingThemeTags, setIsLoadingThemeTags] = useState(true);
  
  const [countriesError, setCountriesError] = useState<string | null>(null);
  const [tripTypesError, setTripTypesError] = useState<string | null>(null);
  const [themeTagsError, setThemeTagsError] = useState<string | null>(null);
  
  const [isColdStart, setIsColdStart] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  // Helper function to detect cold start errors
  const detectColdStart = (error: any): boolean => {
    const errorMessage = error?.message?.toLowerCase() || '';
    const errorName = error?.name?.toLowerCase() || '';
    
    // Common cold start indicators
    return (
      errorMessage.includes('failed to fetch') ||
      errorMessage.includes('networkerror') ||
      errorMessage.includes('timeout') ||
      errorMessage.includes('econnrefused') ||
      errorName === 'typeerror' ||
      error?.code === 'ECONNREFUSED'
    );
  };

  // ----------------------------------------
  // Fetch Functions
  // ----------------------------------------
  
  const refreshCountries = useCallback(async () => {
    setIsLoadingCountries(true);
    setCountriesError(null);
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout for cold starts
      
      const response = await fetch(`${API_URL}/api/locations`, {
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      
      if (!response.ok) throw new Error('Failed to fetch countries');
      
      const data = await response.json();
      if (data.success && data.data) {
        const mapped: Country[] = data.data.map((c: any) => ({
          id: c.id,
          name: c.name,
          nameHe: c.name_he || c.nameHe || c.name,
          continent: c.continent,
        }));
        setCountries(mapped);
        setIsColdStart(false); // Success, clear cold start flag
        setRetryCount(0);
      } else {
        throw new Error(data.error || 'Invalid response');
      }
    } catch (error) {
      console.error('[DataStore] Countries fetch error:', error);
      
      // Detect if this is a cold start issue
      if (detectColdStart(error)) {
        setIsColdStart(true);
        setCountriesError('cold_start');
        
        // Auto-retry once after 5 seconds for cold starts
        if (retryCount === 0) {
          setRetryCount(1);
          setTimeout(() => {
            console.log('[DataStore] Auto-retrying after cold start detection...');
            refreshCountries();
          }, 5000);
        }
      } else {
        setCountriesError(error instanceof Error ? error.message : 'Failed to load countries');
      }
    } finally {
      setIsLoadingCountries(false);
    }
  }, [retryCount]);

  const refreshTripTypes = useCallback(async () => {
    setIsLoadingTripTypes(true);
    setTripTypesError(null);
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000);
      
      const response = await fetch(`${API_URL}/api/trip-types`, {
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      
      if (!response.ok) throw new Error('Failed to fetch trip types');
      
      const data = await response.json();
      if (data.success && data.data) {
        const mapped: TripType[] = data.data.map((t: any) => ({
          id: t.id,
          name: t.name,
          nameHe: t.name_he || t.nameHe || t.name,
          description: t.description,
        }));
        setTripTypes(mapped);
        setIsColdStart(false);
        setRetryCount(0);
      } else {
        throw new Error(data.error || 'Invalid response');
      }
    } catch (error) {
      console.error('[DataStore] Trip types fetch error:', error);
      
      if (detectColdStart(error)) {
        setIsColdStart(true);
        setTripTypesError('cold_start');
      } else {
        setTripTypesError(error instanceof Error ? error.message : 'Failed to load trip types');
      }
    } finally {
      setIsLoadingTripTypes(false);
    }
  }, [retryCount]);

  const refreshThemeTags = useCallback(async () => {
    setIsLoadingThemeTags(true);
    setThemeTagsError(null);
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000);
      
      const response = await fetch(`${API_URL}/api/tags`, {
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      
      if (!response.ok) throw new Error('Failed to fetch tags');
      
      const data = await response.json();
      if (data.success && data.data) {
        // Only include THEME tags
        const mapped: ThemeTag[] = data.data
          .filter((t: any) => t.category === 'THEME')
          .map((t: any) => ({
            id: t.id,
            name: t.name,
            nameHe: t.name_he || t.nameHe || t.name,
            category: t.category,
          }));
        setThemeTags(mapped);
        setIsColdStart(false);
        setRetryCount(0);
      } else {
        throw new Error(data.error || 'Invalid response');
      }
    } catch (error) {
      console.error('[DataStore] Theme tags fetch error:', error);
      
      if (detectColdStart(error)) {
        setIsColdStart(true);
        setThemeTagsError('cold_start');
      } else {
        setThemeTagsError(error instanceof Error ? error.message : 'Failed to load theme tags');
      }
    } finally {
      setIsLoadingThemeTags(false);
    }
  }, [retryCount]);

  const refreshAll = useCallback(async () => {
    await Promise.all([
      refreshCountries(),
      refreshTripTypes(),
      refreshThemeTags(),
    ]);
  }, [refreshCountries, refreshTripTypes, refreshThemeTags]);

  // ----------------------------------------
  // Helper Functions
  // ----------------------------------------
  
  const getCountryById = useCallback((id: number) => {
    return countries.find(c => c.id === id);
  }, [countries]);

  const getTripTypeById = useCallback((id: number) => {
    return tripTypes.find(t => t.id === id);
  }, [tripTypes]);

  const getThemeTagById = useCallback((id: number) => {
    return themeTags.find(t => t.id === id);
  }, [themeTags]);

  const getCountriesByContinent = useCallback((continent: string) => {
    return countries.filter(c => c.continent === continent);
  }, [countries]);

  // ----------------------------------------
  // Initial Load
  // ----------------------------------------
  
  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  // ----------------------------------------
  // Computed Values
  // ----------------------------------------
  
  const isLoading = isLoadingCountries || isLoadingTripTypes || isLoadingThemeTags;
  const hasError = !!(countriesError || tripTypesError || themeTagsError);

  // ----------------------------------------
  // Context Value
  // ----------------------------------------
  
  const value: DataStore = {
    // Data
    countries,
    tripTypes,
    themeTags,
    
    // Loading states
    isLoadingCountries,
    isLoadingTripTypes,
    isLoadingThemeTags,
    isLoading,
    
    // Error states
    countriesError,
    tripTypesError,
    themeTagsError,
    hasError,
    
    // Cold start detection
    isColdStart,
    retryCount,
    
    // Actions
    refreshCountries,
    refreshTripTypes,
    refreshThemeTags,
    refreshAll,
    
    // Helpers
    getCountryById,
    getTripTypeById,
    getThemeTagById,
    getCountriesByContinent,
  };

  const Provider = DataStoreContext.Provider;
  
  return (
    <Provider value={value}>
      {children}
    </Provider>
  );
}

// ============================================
// HOOKS
// ============================================

/**
 * Access the full data store.
 * Must be used within DataStoreProvider.
 */
export function useDataStore(): DataStore {
  const context = useContext(DataStoreContext);
  if (!context) {
    throw new Error('useDataStore must be used within DataStoreProvider');
  }
  return context;
}

/**
 * Get countries data.
 */
export function useCountries() {
  const { countries, isLoadingCountries, countriesError, getCountriesByContinent } = useDataStore();
  return { countries, isLoading: isLoadingCountries, error: countriesError, getByContinent: getCountriesByContinent };
}

/**
 * Get trip types data.
 */
export function useTripTypes() {
  const { tripTypes, isLoadingTripTypes, tripTypesError, getTripTypeById } = useDataStore();
  return { tripTypes, isLoading: isLoadingTripTypes, error: tripTypesError, getById: getTripTypeById };
}

/**
 * Get theme tags data.
 */
export function useThemeTags() {
  const { themeTags, isLoadingThemeTags, themeTagsError, getThemeTagById } = useDataStore();
  return { themeTags, isLoading: isLoadingThemeTags, error: themeTagsError, getById: getThemeTagById };
}

// ============================================
// ICON MAPPINGS (UI only - no IDs)
// ============================================

// These map by NAME, not by ID, so they work regardless of database IDs
import { 
  Compass, Ship, Camera, Mountain, Palmtree,
  Plane, Train, Users, Snowflake, Car,
  TrendingUp, PawPrint, Landmark, Utensils,
  Waves, Sun, TreePine, Globe
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export const TRIP_TYPE_ICONS: Record<string, LucideIcon> = {
  'Geographic Depth': Compass,
  'Carnivals & Festivals': TreePine,
  'African Safari': PawPrint,
  'Train Tours': Train,
  'Geographic Cruises': Ship,
  'Nature Hiking': Mountain,
  'Jeep Tours': Car,
  'Snowmobile Tours': Snowflake,
  'Private Groups': Users,
  'Photography': Camera,
};

export const THEME_TAG_ICONS: Record<string, LucideIcon> = {
  'Cultural & Historical': Landmark,
  'Wildlife': PawPrint,
  'Extreme': TrendingUp,
  'Food & Wine': Utensils,
  'Beach & Island': Waves,
  'Mountain': Mountain,
  'Desert': Sun,
  'Arctic & Snow': Snowflake,
  'Tropical': Palmtree,
  'Hanukkah & Christmas Lights': TreePine,
};

/**
 * Get icon for a trip type by name.
 */
export function getTripTypeIcon(name: string): LucideIcon {
  return TRIP_TYPE_ICONS[name] || Globe;
}

/**
 * Get icon for a theme tag by name.
 */
export function getThemeTagIcon(name: string): LucideIcon {
  return THEME_TAG_ICONS[name] || Globe;
}

// ============================================
// CONTINENT DATA (Static - no IDs involved)
// ============================================

export const CONTINENTS = [
  { value: 'Africa', nameHe: 'אפריקה' },
  { value: 'Antarctica', nameHe: 'אנטארקטיקה' },
  { value: 'Asia', nameHe: 'אסיה' },
  { value: 'Europe', nameHe: 'אירופה' },
  { value: 'North & Central America', nameHe: 'צפון ומרכז אמריקה' },
  { value: 'Oceania', nameHe: 'אוקיאניה' },
  { value: 'South America', nameHe: 'דרום אמריקה' },
] as const;

export type ContinentValue = typeof CONTINENTS[number]['value'];
