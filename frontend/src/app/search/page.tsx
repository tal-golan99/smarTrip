'use client';

import { useState, useEffect, useMemo, useRef, useCallback, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Image from 'next/image';
import { 
  Search, X, ChevronDown, MapPin, Calendar, DollarSign, 
  TrendingUp, Compass, Ship, Camera, Mountain, Palmtree,
  Plane, Train, Users, Users2, Snowflake, Car, Sparkles, Globe,
  Utensils, Landmark, TreePine, Waves, Sun, PawPrint, Loader2, Home, LogOut
} from 'lucide-react';
import clsx from 'clsx';

// Phase 1: Tracking imports
import {
  usePageView,
  useFilterTracking,
  trackSearchSubmit,
  flushPendingEvents,
} from '@/hooks/useTracking';

// Supabase auth imports
import { supabase, isAuthAvailable } from '@/lib/supabaseClient';
import { useUser } from '@/hooks/useUser';

// Data store imports
import { 
  CONTINENTS,
  TRIP_TYPE_ICONS,
  THEME_TAG_ICONS,
  COUNTRY_FLAGS,
  CONTINENT_IMAGES,
  useCountries,
  useTripTypes,
  useThemeTags,
  useDataStore,
  type Country
} from '@/lib/dataStore';

// API URL from environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Log API URL on module load for debugging (only in browser)
if (typeof window !== 'undefined') {
  console.log('[SearchPage] API_URL:', API_URL);
  // Warn if still using localhost in production
  if (API_URL.includes('localhost') && process.env.NODE_ENV === 'production') {
    console.error('[SearchPage] WARNING: Using localhost API URL in production! Set NEXT_PUBLIC_API_URL in Vercel.');
  }
}

// ============================================
// TYPES
// ============================================

// Local Tag type for search page (simplified, doesn't include API metadata)
interface SearchTag {
  id: number;
  name: string;
  nameHe: string;
  category: 'Type' | 'Theme';
}

interface LocationSelection {
  type: 'continent' | 'country';
  id: string | number;
  name: string;
  nameHe: string;
}

// ============================================
// DATA IS FETCHED FROM BACKEND API
// ============================================
// All data (countries, trip types, theme tags) is fetched from the backend API.
// This ensures IDs always match the database and eliminates sync issues.
// NO hardcoded fallback data - if API fails, UI shows error with retry.

import { getAvailableMonths, getAvailableYears } from '@/lib/utils';
import { DualRangeSlider } from '@/components/features/DualRangeSlider';
import { LogoutConfirmModal } from '@/components/features/LogoutConfirmModal';

// ============================================
// SUB-COMPONENTS
// ============================================

function SelectionBadge({ 
  selection, 
  onRemove 
}: { 
  selection: LocationSelection; 
  onRemove: () => void;
}) {
  const [isHovered, setIsHovered] = useState(false);
  const flagCode = selection.type === 'country' ? COUNTRY_FLAGS[selection.name] : null;
  const flagUrl = flagCode ? `https://flagcdn.com/96x72/${flagCode}.png` : null;

  // Use uploaded continent images
  const continentMapUrl = selection.type === 'continent' 
    ? CONTINENT_IMAGES[selection.name]
    : null;

  return (
    <div
      className="relative group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div 
        className={clsx(
          'w-20 h-20 md:w-24 md:h-24 rounded-full flex items-center justify-center relative overflow-hidden',
          'border-2 transition-all duration-200',
          isHovered ? 'border-[#12acbe] scale-105' : 'border-[#0092a3]'
        )}
      >
        {/* Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={flagUrl ? {
            backgroundImage: `url(${flagUrl})`,
          } : continentMapUrl ? {
            backgroundImage: `url(${continentMapUrl})`,
          } : {
            background: 'linear-gradient(to bottom right, #0092a3, #4a5568)'
          }}
        />
        
        {/* Darker overlay for better text contrast */}
        <div className="absolute inset-0 bg-black/50" />
        
        {/* Text content */}
        <div className="relative text-center px-2 z-10">
          <p className="text-white text-xs font-bold leading-tight drop-shadow-lg">
            {selection.nameHe}
          </p>
        </div>
      </div>
      
      {isHovered && (
        <button
          onClick={onRemove}
          className="absolute -top-1 -left-1 w-6 h-6 bg-[#ff2b00] rounded-full flex items-center justify-center shadow-lg hover:bg-red-700 transition-colors"
        >
          <X className="w-4 h-4 text-white" />
        </button>
      )}
    </div>
  );
}

function TagCircle({ 
  tag, 
  isSelected, 
  onClick,
  iconMap
}: { 
  tag: SearchTag; 
  isSelected: boolean; 
  onClick: () => void;
  iconMap: Record<string, any>;
}) {
  const Icon = iconMap[tag.name] || Compass;

  return (
    <button
      onClick={onClick}
      className={clsx(
        'flex flex-col items-center gap-2 p-3 md:p-4 rounded-xl transition-all duration-200',
        'border-2 hover:scale-105',
        isSelected 
          ? 'bg-[#076839] border-[#12acbe] text-white' 
          : 'bg-white border-gray-200 text-[#5a5a5a] hover:border-[#12acbe]'
      )}
    >
      <div className={clsx(
        'w-10 h-10 md:w-12 md:h-12 rounded-full flex items-center justify-center',
        isSelected ? 'bg-[#12acbe]' : 'bg-gray-100'
      )}>
        <Icon className="w-5 h-5 md:w-6 md:h-6" />
      </div>
      <span className="text-[10px] md:text-xs font-medium text-center leading-tight">
        {tag.nameHe}
      </span>
    </button>
  );
}

// ============================================
// DUAL RANGE SLIDER COMPONENT
// ============================================


// ============================================
// MAIN COMPONENT
// ============================================

function SearchPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // Use DataStore hooks instead of local state and fetching
  const { countries, isLoading: isLoadingCountries, error: countriesError } = useCountries();
  const { tripTypes: tripTypesData, isLoading: isLoadingTripTypes, error: tripTypesError } = useTripTypes();
  const { themeTags: themeTagsData, isLoading: isLoadingThemeTags, error: themeTagsError } = useThemeTags();
  const { refreshAll } = useDataStore();

  // Map DataStore types to SearchTag format for compatibility
  const tripTypes: SearchTag[] = tripTypesData.map(t => ({
    id: t.id,
    name: t.name,
    nameHe: t.nameHe || t.name,
    category: 'Type' as const
  }));

  const themeTags: SearchTag[] = themeTagsData.map(t => ({
    id: t.id,
    name: t.name,
    nameHe: t.nameHe || t.name,
    category: 'Theme' as const
  }));

  // Combined loading and error states
  const isLoadingTypes = isLoadingTripTypes || isLoadingThemeTags;
  const typesError = tripTypesError || themeTagsError;

  // Location search state
  const [locationSearch, setLocationSearch] = useState('');
  const [isLocationDropdownOpen, setIsLocationDropdownOpen] = useState(false);
  const [selectedLocations, setSelectedLocations] = useState<LocationSelection[]>([]);
  
  // Ref for detecting clicks outside dropdown
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Tag selection state
  const [selectedType, setSelectedType] = useState<number | null>(null);
  const [selectedThemes, setSelectedThemes] = useState<number[]>([]);

  // Date filters
  const [selectedYear, setSelectedYear] = useState<string>('all');
  const [selectedMonth, setSelectedMonth] = useState<string>('all');

  // Range filters with proper defaults
  const [minDuration, setMinDuration] = useState(5);
  const [maxDuration, setMaxDuration] = useState(30);
  const [maxBudget, setMaxBudget] = useState(15000);
  const [difficulty, setDifficulty] = useState<number | null>(null);

  // Available years (current and future only)
  const availableYears = useMemo(() => getAvailableYears(), []);
  
  // Available months based on selected year
  const availableMonths = useMemo(() => getAvailableMonths(selectedYear), [selectedYear]);
  
  // User authentication state
  const { userName, isLoading: isLoadingUser } = useUser();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  
  // Phase 1: Track page view (non-blocking)
  usePageView('search');
  
  // Show logout confirmation dialog
  const handleLogout = () => {
    setShowLogoutConfirm(true);
  };

  // Confirm logout
  const confirmLogout = async () => {
    if (!isAuthAvailable() || !supabase) {
      return;
    }
    
    try {
      await supabase.auth.signOut();
      setShowLogoutConfirm(false);
      router.push('/auth?redirect=/search');
    } catch (error) {
      console.error('[SearchPage] Error logging out:', error);
      setShowLogoutConfirm(false);
    }
  };

  // Cancel logout
  const cancelLogout = () => {
    setShowLogoutConfirm(false);
  };
  
  // Phase 1: Track filter changes/removals
  // Create a memoized filters object to track changes
  const currentFilters = useMemo(() => ({
    locations: selectedLocations.map(l => l.id).join(','),
    type: selectedType,
    themes: selectedThemes.join(','),
    year: selectedYear,
    month: selectedMonth,
    minDuration,
    maxDuration,
    budget: maxBudget,
    difficulty,
  }), [selectedLocations, selectedType, selectedThemes, selectedYear, selectedMonth, minDuration, maxDuration, maxBudget, difficulty]);
  
  useFilterTracking(currentFilters);
  
  // Track if filters have been changed from defaults
  const hasActiveFilters = useMemo(() => {
    return selectedLocations.length > 0 ||
           selectedType !== null ||
           selectedThemes.length > 0 ||
           selectedYear !== 'all' ||
           selectedMonth !== 'all' ||
           minDuration !== 5 ||
           maxDuration !== 30 ||
           maxBudget !== 15000 ||
           difficulty !== null;
  }, [selectedLocations, selectedType, selectedThemes, selectedYear, selectedMonth, minDuration, maxDuration, maxBudget, difficulty]);

  // Scroll to top on mount
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
  }, []);
  // DataStore handles all fetching automatically on mount
  // No need for manual fetch calls or useEffect hooks

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsLocationDropdownOpen(false);
      }
    };

    if (isLocationDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isLocationDropdownOpen]);

  // Load state from URL params (for back button) - prevent duplicates
  useEffect(() => {
    // Scroll to top when returning to search
    window.scrollTo({ top: 0, behavior: 'smooth' });

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

    // Only load from URL if there are params
    const hasUrlParams = countriesParam || continentsParam || type || themes;
    
    if (hasUrlParams) {
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

      // REPLACE state to prevent duplicates
      if (newLocations.length > 0) {
        setSelectedLocations(newLocations);
      }
    }

    if (type) setSelectedType(Number(type));
    if (themes) setSelectedThemes(themes.split(',').map(Number));
    if (year) setSelectedYear(year);
    if (month) setSelectedMonth(month);
    if (minDur) setMinDuration(Math.max(5, Math.min(Number(minDur), 30)));
    if (maxDur) setMaxDuration(Math.max(5, Math.min(Number(maxDur), 30)));
    if (budget) setMaxBudget(Number(budget));
    if (diff) setDifficulty(Number(diff));
  }, [searchParams, countries]);

  // Filter countries by search
  const filteredCountries = useMemo(() => {
    if (!locationSearch) return countries;
    
    const searchLower = locationSearch.toLowerCase();
    return countries.filter(c => 
      c.name.toLowerCase().includes(searchLower) ||
      c.nameHe.includes(locationSearch) ||
      c.continent.toLowerCase().includes(searchLower)
    );
  }, [locationSearch, countries]);

  // Filter continents by search
  const filteredContinents = useMemo(() => {
    if (!locationSearch) return CONTINENTS;
    
    const searchLower = locationSearch.toLowerCase();
    return CONTINENTS.filter(c => 
      c.value.toLowerCase().includes(searchLower) ||
      c.nameHe.includes(locationSearch)
    );
  }, [locationSearch]);

  // Group countries by continent
  const countriesByContinent = useMemo(() => {
    const grouped: Record<string, Country[]> = {};
    filteredCountries.forEach(country => {
      if (!grouped[country.continent]) {
        grouped[country.continent] = [];
      }
      grouped[country.continent].push(country);
    });
    
    // Sort countries alphabetically within each continent
    Object.keys(grouped).forEach(continent => {
      grouped[continent].sort((a, b) => a.nameHe.localeCompare(b.nameHe, 'he'));
    });
    
    return grouped;
  }, [filteredCountries]);

  // Handle location selection
  const addLocation = (type: 'continent' | 'country', id: string | number, name: string, nameHe: string) => {
    const newSelection: LocationSelection = { type, id, name, nameHe };
    
    // Special case: Antarctica - prevent adding as both country and continent
    const isAntarctica = name === 'Antarctica' || name === 'אנטארקטיקה';
    if (isAntarctica) {
      // Check if Antarctica is already selected (as either country or continent)
      const antarcticaExists = selectedLocations.some(s => 
        s.name === 'Antarctica' || s.nameHe === 'אנטארקטיקה'
      );
      if (antarcticaExists) {
        // Already selected, don't add again
        setIsLocationDropdownOpen(false);
        setLocationSearch('');
        return;
      }
    }
    
    // Check if already selected (same type and id)
    const exists = selectedLocations.some(s => s.type === type && s.id === id);
    if (!exists) {
      setSelectedLocations([...selectedLocations, newSelection]);
    }
    
    setIsLocationDropdownOpen(false);
    setLocationSearch('');
  };

  const removeLocation = (index: number) => {
    setSelectedLocations(selectedLocations.filter((_, i) => i !== index));
  };

  // Handle theme selection (max 3)
  const toggleTheme = (themeId: number) => {
    if (selectedThemes.includes(themeId)) {
      setSelectedThemes(selectedThemes.filter(id => id !== themeId));
    } else if (selectedThemes.length < 3) {
      setSelectedThemes([...selectedThemes, themeId]);
    }
  };

  // Handle duration change (with 3-day gap enforcement)
  const handleDurationChange = (newMin: number, newMax: number) => {
    setMinDuration(newMin);
    setMaxDuration(newMax);
  };

  // Handle search submission - navigate to results page with query params
  const handleSearch = () => {
    const countriesIds = selectedLocations
      .filter(s => s.type === 'country')
      .map(s => s.id as number)
      .join(',');
    
    const continents = selectedLocations
      .filter(s => s.type === 'continent')
      .map(s => s.name)
      .join(',');

    const params = new URLSearchParams();
    if (countriesIds) params.set('countries', countriesIds);
    if (continents) params.set('continents', continents);
    if (selectedType) params.set('type', selectedType.toString());
    if (selectedThemes.length) params.set('themes', selectedThemes.join(','));
    if (selectedYear !== 'all') params.set('year', selectedYear);
    if (selectedMonth !== 'all') params.set('month', selectedMonth);
    params.set('minDuration', minDuration.toString());
    params.set('maxDuration', maxDuration.toString());
    params.set('budget', maxBudget.toString());
    if (difficulty !== null) params.set('difficulty', difficulty.toString());

    // Phase 1: Track search submission
    const preferences = {
      countries: countriesIds ? countriesIds.split(',').map(Number) : [],
      continents: continents ? continents.split(',') : [],
      type: selectedType,
      themes: selectedThemes,
      year: selectedYear,
      month: selectedMonth,
      minDuration,
      maxDuration,
      budget: maxBudget,
      difficulty,
    };
    
    // Classify search type
    const filterCount = [
      countriesIds, 
      continents, 
      selectedType, 
      selectedThemes.length > 0,
      selectedYear !== 'all',
      selectedMonth !== 'all',
      difficulty !== null
    ].filter(Boolean).length;
    
    const searchType = filterCount >= 2 ? 'focused_search' : 'exploration';
    trackSearchSubmit(preferences, searchType);
    
    // Flush events before navigation
    flushPendingEvents();

    router.push(`/search/results?${params.toString()}`);
  };

  // Clear all filters - reset to defaults
  const handleClearSearch = () => {
    if (!hasActiveFilters) return;
    
    setSelectedLocations([]);
    setSelectedType(null);
    setSelectedThemes([]);
    setSelectedYear('all');
    setSelectedMonth('all');
    setMinDuration(5);
    setMaxDuration(30);
    setMaxBudget(15000);
    setDifficulty(null);
    setLocationSearch('');
  };

  // Show loading state while data is being fetched
  const isLoading = isLoadingCountries || isLoadingTypes;
  const hasError = countriesError || typesError;
  const hasData = countries.length > 0 && tripTypes.length > 0;

  // If still loading initial data, show loading indicator (clean white background)
  if (isLoading && !hasData && !hasError) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <Loader2 className="w-12 h-12 animate-spin text-[#12acbe] mx-auto mb-4" />
          <p className="text-[#5a5a5a] text-lg mb-2">טוען אפשרויות חיפוש...</p>
        </div>
      </div>
    );
  }

  // If error fetching data and no cached data, show error with retry
  if (hasError && !hasData) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="text-center max-w-md p-8">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <X className="w-8 h-8 text-red-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-800 mb-4">
            שגיאת חיבור לשרת
          </h2>
          <div className="text-gray-600 mb-6 space-y-2 text-sm">
            <p>נסה לרענן את הדף בעוד כמה רגעים</p>
          </div>
          <button
            onClick={() => refreshAll()}
            className="w-full px-6 py-3 bg-[#076839] hover:bg-[#0ba55c] text-white rounded-xl font-medium transition-all"
          >
            נסה שוב עכשיו
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <LogoutConfirmModal
        isOpen={showLogoutConfirm}
        onConfirm={confirmLogout}
        onCancel={cancelLogout}
      />

      {/* Header */}
      <header className="bg-[#076839] text-white py-4 md:py-6 shadow-lg">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between gap-4">
            {/* Return to Home Button and Logout */}
            <div className="w-16 md:w-32 flex items-center justify-start gap-2">
              <button
                onClick={() => router.push('/')}
                className="flex items-center gap-2 px-3 py-2 md:px-4 md:py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all duration-200 group"
                title="חזרה לדף הבית"
              >
                <Home className="w-5 h-5 md:w-6 md:h-6 group-hover:scale-110 transition-transform" />
              </button>
              {isAuthAvailable() && userName && (
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 px-3 py-2 md:px-4 md:py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all duration-200 group"
                  title="התנתק"
                  type="button"
                >
                  <LogOut className="w-5 h-5 md:w-6 md:h-6 group-hover:scale-110 transition-transform" />
                </button>
              )}
            </div>
            
            {/* Title - Centered */}
            <div className="flex-1 text-center">
              <h1 className="text-2xl md:text-3xl font-bold text-white">
                מצא את הטיול המושלם עבורך
              </h1>
              <p className="text-gray-100 mt-1 md:mt-2 text-sm md:text-base">
                {isLoadingUser ? (
                  'טוען...'
                ) : userName ? (
                  <span className="font-medium">שלום {userName}!</span>
                ) : null}
              </p>
            </div>
            
            {/* Company Logo */}
            <div className="w-16 md:w-32 flex items-center justify-end">
              <Image 
                src="/images/logo/smartrip.png" 
                alt="SmartTrip Logo" 
                width={128}
                height={64}
                className="h-10 md:h-16 w-auto object-contain"
              />
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6 md:py-8 max-w-6xl">
        {/* Clear Search Button - Positioned top right */}
        <div className="mb-4 md:mb-6 flex justify-start">
          <button
            onClick={handleClearSearch}
            disabled={!hasActiveFilters}
            className={clsx(
              'px-6 py-3 rounded-lg font-medium transition-all text-sm border',
              hasActiveFilters
                ? 'bg-white text-[#0a192f] border-gray-300 hover:bg-gray-50 cursor-pointer shadow-md'
                : 'bg-gray-200 text-gray-400 border-gray-300 cursor-not-allowed'
            )}
          >
            ניקוי חיפוש
          </button>
        </div>
        
        {/* ============================================ */}
        {/* LOCATION SEARCH */}
        {/* ============================================ */}
        <section className="bg-white rounded-xl shadow-md p-4 md:p-6 mb-4 md:mb-6">
          <h2 className="text-xl md:text-2xl font-bold mb-3 md:mb-4 flex items-center gap-2 text-[#5a5a5a]">
            <MapPin className="text-[#12acbe]" />
            לאן תרצה לנסוע?
          </h2>

          {/* Search Input and Dropdown Container */}
          <div className="relative" ref={dropdownRef}>
            <input
              type="text"
              value={locationSearch}
              onChange={(e) => setLocationSearch(e.target.value)}
              onFocus={() => setIsLocationDropdownOpen(true)}
              placeholder="חפש יעד או יבשת..."
              className="w-full px-4 py-3 pr-12 pl-12 border-2 border-gray-200 rounded-lg focus:border-[#12acbe] focus:outline-none text-right text-base"
            />
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
            <button
              onClick={() => setIsLocationDropdownOpen(!isLocationDropdownOpen)}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-[#12acbe]"
            >
              <ChevronDown className={clsx(
                'w-5 h-5 transition-transform',
                isLocationDropdownOpen && 'rotate-180'
              )} />
            </button>

            {/* Dropdown - Full RTL layout with mobile optimization */}
            {isLocationDropdownOpen && (
              <div className="absolute z-50 left-0 right-0 mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl max-h-[70vh] md:max-h-96 overflow-y-auto overscroll-contain" dir="rtl">
              {/* Show matching continents first if searching */}
              {locationSearch && filteredContinents.length > 0 && (
                <div className="border-b">
                  <div className="px-4 py-3 bg-gray-100 text-sm font-bold text-gray-600 text-right sticky top-0">יבשות</div>
                  {filteredContinents.map(continent => (
                    <button
                      key={continent.value}
                      onClick={() => addLocation('continent', continent.value, continent.value, continent.nameHe)}
                      className="w-full px-5 py-4 md:py-3 text-right hover:bg-[#12acbe]/10 active:bg-[#12acbe]/20 text-[#076839] font-bold transition-colors touch-manipulation"
                    >
                      {continent.nameHe}
                    </button>
                  ))}
                </div>
              )}
              
              {/* Countries grouped by continent - SORTED A-Z by continent name */}
              {Object.keys(countriesByContinent).length > 0 ? (
                Object.entries(countriesByContinent)
                .sort(([continentA], [continentB]) => {
                  // Use the Hebrew names for sorting alphabetically
                  const continentInfoA = CONTINENTS.find(c => c.value === continentA);
                  const continentInfoB = CONTINENTS.find(c => c.value === continentB);
                  const nameA = continentInfoA?.nameHe || continentA;
                  const nameB = continentInfoB?.nameHe || continentB;
                  return nameA.localeCompare(nameB, 'he');
                })
                .map(([continent, countriesList]) => {
                  const continentInfo = CONTINENTS.find(c => c.value === continent);
                  
                  return (
                    <div key={continent} className="border-b last:border-b-0">
                      {/* Continent Header - RTL with continent name on right, chevron on left */}
                      <button
                        onClick={() => addLocation('continent', continent, continent, continentInfo?.nameHe || continent)}
                        className="w-full px-4 py-3 bg-gray-50 hover:bg-[#12acbe]/10 font-bold text-[#076839] flex items-center justify-between"
                      >
                        <ChevronDown className="w-4 h-4 flex-shrink-0" />
                        <span className="flex-1 text-right">{continentInfo?.nameHe || continent}</span>
                      </button>
                      
                      {/* Countries */}
                      <div className="bg-white">
                        {countriesList.map(country => (
                          <button
                            key={country.id}
                            onClick={() => addLocation('country', country.id, country.name, country.nameHe)}
                            className="w-full px-6 py-3 md:py-2 text-right hover:bg-gray-50 active:bg-gray-100 text-[#5a5a5a] hover:text-[#12acbe] transition-colors touch-manipulation"
                          >
                            {country.nameHe}
                          </button>
                        ))}
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="p-4 text-center text-gray-500">
                  {isLoadingCountries ? (
                    <>
                      <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                      טוען יעדים...
                    </>
                  ) : (
                    'לא ניתן לטעון יעדים מהשרת'
                  )}
                </div>
              )}
              </div>
            )}
          </div>

          {/* Selected Locations (Circle Badges) - RTL layout with proper overflow handling */}
          {selectedLocations.length > 0 && (
            <div className="mt-4 md:mt-6" dir="rtl">
              <p className="text-sm text-gray-600 mb-3">יעדים נבחרים:</p>
              <div className="flex flex-wrap gap-3 md:gap-4 max-h-48 overflow-y-auto py-2">
                {selectedLocations.map((selection, index) => (
                  <SelectionBadge
                    key={`${selection.type}-${selection.id}`}
                    selection={selection}
                    onRemove={() => removeLocation(index)}
                  />
                ))}
              </div>
            </div>
          )}
        </section>

        {/* ============================================ */}
        {/* TRIP STYLE (TYPE) */}
        {/* ============================================ */}
        <section className="bg-white rounded-xl shadow-md p-4 md:p-6 mb-4 md:mb-6">
          <h2 className="text-xl md:text-2xl font-bold mb-3 md:mb-4 flex items-center gap-2 text-[#5a5a5a]">
            <Compass className="text-[#12acbe]" />
            סגנון הטיול
          </h2>
          <p className="text-sm text-gray-600 mb-3 md:mb-4 text-right">בחר סגנון טיול אחד</p>

          <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 md:gap-4">
            {tripTypes.length > 0 ? tripTypes.map(tag => (
              <TagCircle
                key={tag.id}
                tag={tag}
                isSelected={selectedType === tag.id}
                onClick={() => setSelectedType(selectedType === tag.id ? null : tag.id)}
                iconMap={TRIP_TYPE_ICONS}
              />
            )) : (
              <div className="col-span-full text-center text-gray-500 py-4 text-sm">
                {isLoadingTypes ? 'טוען סגנונות טיול...' : 'לא ניתן לטעון סגנונות טיול'}
              </div>
            )}
          </div>
          
          <div className="mt-4 md:mt-6">
            <a
              href="https://wa.me/972500000000?text=שלום, אני מעוניין בטיול בוטיק בתפירה אישית"
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full text-center py-3 px-4 md:px-6 border-2 border-[#12acbe] text-[#12acbe] hover:bg-[#12acbe] hover:text-white rounded-xl font-medium transition-all text-sm md:text-base"
            >
              אני רוצה לצאת לטיול בוטיק בתפירה אישית במקום
            </a>
          </div>
        </section>

        {/* ============================================ */}
        {/* TRIP THEMES */}
        {/* ============================================ */}
        <section className="bg-white rounded-xl shadow-md p-4 md:p-6 mb-4 md:mb-6">
          <h2 className="text-xl md:text-2xl font-bold mb-3 md:mb-4 flex items-center gap-2 text-[#5a5a5a]">
            <Sparkles className="text-[#12acbe]" />
            תחומי עניין
          </h2>
          <p className="text-sm text-gray-600 mb-3 md:mb-4 text-right">
            בחר עד 3 תחומי עניין ({selectedThemes.length}/3)
          </p>

          <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2 md:gap-4">
            {themeTags.length > 0 ? themeTags.map(tag => (
              <TagCircle
                key={tag.id}
                tag={tag}
                isSelected={selectedThemes.includes(tag.id)}
                onClick={() => toggleTheme(tag.id)}
                iconMap={THEME_TAG_ICONS}
              />
            )) : (
              <div className="col-span-full text-center text-gray-500 py-4 text-sm">
                {isLoadingTypes ? 'טוען נושאי טיול...' : 'לא ניתן לטעון נושאי טיול'}
              </div>
            )}
          </div>
        </section>

        {/* ============================================ */}
        {/* DATE SELECTION */}
        {/* ============================================ */}
        <section className="bg-white rounded-xl shadow-md p-4 md:p-6 mb-4 md:mb-6">
          <h2 className="text-xl md:text-2xl font-bold mb-3 md:mb-4 flex items-center gap-2 text-[#5a5a5a]">
            <Calendar className="text-[#12acbe]" />
            מתי תרצה לנסוע?
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Year */}
            <div>
              <label className="block text-sm font-medium mb-2 text-right">שנה</label>
              <select
                value={selectedYear}
                onChange={(e) => {
                  setSelectedYear(e.target.value);
                  // Reset month if current selection is no longer valid
                  if (e.target.value !== 'all') {
                    const newMonths = getAvailableMonths(e.target.value);
                    if (selectedMonth !== 'all' && !newMonths.find(m => m.index.toString() === selectedMonth)) {
                      setSelectedMonth('all');
                    }
                  }
                }}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-[#ff9402] focus:outline-none text-right"
              >
                <option value="all">כל השנים</option>
                {availableYears.map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>

            {/* Month */}
            <div>
              <label className="block text-sm font-medium mb-2 text-right">חודש</label>
              <select
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-[#12acbe] focus:outline-none text-right"
              >
                <option value="all">כל השנה</option>
                {availableMonths.map(({ index, name }) => (
                  <option key={index} value={String(index)}>
                    {name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </section>

        {/* ============================================ */}
        {/* SLIDERS & RANGES */}
        {/* ============================================ */}
        <section className="bg-white rounded-xl shadow-md p-4 md:p-6 mb-4 md:mb-6">
          <h2 className="text-xl md:text-2xl font-bold mb-4 md:mb-6 flex items-center gap-2 text-[#5a5a5a]">
            <TrendingUp className="text-[#12acbe]" />
            העדפות נוספות
          </h2>

          {/* Duration - Dual Range Slider with RTL Direction */}
          <div className="mb-6 md:mb-8">
            <DualRangeSlider
              min={5}
              max={30}
              minValue={minDuration}
              maxValue={maxDuration}
              step={1}
              minGap={3}
              onChange={handleDurationChange}
              label="משך הטיול"
            />
          </div>

          {/* Budget - Turquoise styled slider */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-3 flex items-center gap-2 justify-end">
              <span className="text-[#076839] font-bold">
                ${maxBudget.toLocaleString()}
              </span>
              :תקציב מקסימלי
              <DollarSign className="w-5 h-5 text-[#12acbe]" />
            </label>
            <div className="relative">
              <input
                type="range"
                min="2000"
                max="15000"
                step="500"
                value={maxBudget}
                onChange={(e) => setMaxBudget(Number(e.target.value))}
                style={{
                  background: `linear-gradient(to left, #12acbe 0%, #12acbe ${((maxBudget - 2000) / (15000 - 2000)) * 100}%, #e5e7eb ${((maxBudget - 2000) / (15000 - 2000)) * 100}%, #e5e7eb 100%)`
                }}
                className="w-full h-2 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-[#12acbe] [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:shadow-lg [&::-moz-range-thumb]:w-5 [&::-moz-range-thumb]:h-5 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-[#12acbe] [&::-moz-range-thumb]:cursor-pointer [&::-moz-range-thumb]:border-0"
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>$2,000</span>
              <span>$15,000+</span>
            </div>
          </div>

          {/* Difficulty */}
          <div>
            <label className="block text-sm font-medium mb-3 text-right">רמת קושי (אופציונלי)</label>
            <div className="grid grid-cols-3 gap-2 md:gap-3">
              {[
                { value: 1, label: 'קל', labelEn: 'Easy' },
                { value: 2, label: 'בינוני', labelEn: 'Moderate' },
                { value: 3, label: 'מאתגר', labelEn: 'Hard' }
              ].map(({ value, label }) => (
                <button
                  key={value}
                  onClick={() => setDifficulty(difficulty === value ? null : value)}
                  className={clsx(
                    'py-3 px-3 md:px-4 rounded-lg font-medium transition-all text-sm md:text-base',
                    'border-2',
                    difficulty === value
                      ? 'bg-[#076839] text-white border-[#12acbe]'
                      : 'bg-white text-[#5a5a5a] border-gray-200 hover:border-[#12acbe]'
                  )}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* ============================================ */}
        {/* SEARCH BUTTONS */}
        {/* ============================================ */}
        <div className="flex flex-col md:flex-row gap-3 md:gap-4">
          <button
            onClick={handleSearch}
            className="flex-1 bg-[#076839] text-white py-4 px-6 md:px-8 rounded-xl font-bold text-lg md:text-xl hover:bg-[#0ba55c] transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
          >
            <Search className="w-5 h-5 md:w-6 md:h-6" />
            מצא את הטיול שלי
          </button>
          
          <button
            onClick={handleClearSearch}
            disabled={!hasActiveFilters}
            className={clsx(
              'px-6 md:px-8 py-4 rounded-xl font-medium transition-all border text-base',
              hasActiveFilters
                ? 'bg-white text-[#0a192f] border-gray-300 hover:bg-gray-50 cursor-pointer shadow-md'
                : 'bg-gray-300 text-gray-400 border-gray-300 cursor-not-allowed'
            )}
          >
            ניקוי חיפוש
          </button>
        </div>
      </div>
    </div>
  );
}

// ============================================
// SUSPENSE WRAPPER FOR NEXT.JS 14 STATIC GENERATION
// ============================================

function SearchPageLoading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#076839] via-[#0ba55c] to-[#12acbe] flex items-center justify-center p-4">
      <div className="text-center">
        <div className="mb-6">
          <Image 
            src="/images/logo/smartrip.png" 
            alt="SmartTrip Logo" 
            width={180} 
            height={180} 
            className="mx-auto"
            priority
          />
        </div>
        <Loader2 className="w-12 h-12 animate-spin text-white mx-auto mb-4" />
        <p className="text-white text-xl font-medium mb-2">טוען...</p>
        <p className="text-white/80 text-sm">טעינה ראשונית עשויה לקחת מספר רגעים</p>
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<SearchPageLoading />}>
      <SearchPageContent />
    </Suspense>
  );
}
