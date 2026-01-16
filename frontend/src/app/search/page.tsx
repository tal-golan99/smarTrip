'use client';

import { Suspense, useState, useEffect, useRef, useMemo } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { supabase, isAuthAvailable } from '@/lib/supabaseClient';
import { useUser } from '@/hooks/useUser';
import { useCountries, useTripTypes, useDataStore } from '@/lib/dataStore';
import { useSearch } from '@/hooks/useSearch';
import { useSyncSearchQuery } from '@/hooks/useSyncSearchQuery';
import { usePageView, useFilterTracking } from '@/hooks/useTracking';
import { SearchProvider } from '@/contexts/SearchContext';
import { LogoutConfirmModal } from '@/components/features/LogoutConfirmModal';
import { ClearFiltersButton } from '@/components/ui/ClearFiltersButton';
import { SearchPageHeader } from '@/components/features/search/SearchPageHeader';
import { SearchActions } from '@/components/features/search/SearchActions';
import { SearchPageError } from '@/components/features/search/SearchPageError';
import { SearchPageLoading } from '@/components/features/search/SearchPageLoading';
import { LocationFilterSection } from '@/components/features/search/filters/LocationFilterSection';
import { TripTypeFilterSection } from '@/components/features/search/filters/TripTypeFilterSection';
import { ThemeFilterSection } from '@/components/features/search/filters/ThemeFilterSection';
import { DateFilterSection } from '@/components/features/search/filters/DateFilterSection';
import { RangeFiltersSection } from '@/components/features/search/filters/RangeFiltersSection';

function SearchPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // Data fetching hooks
  const { countries, isLoading: isLoadingCountries, error: countriesError } = useCountries();
  const { tripTypes: tripTypesData, isLoading: isLoadingTripTypes, error: tripTypesError } = useTripTypes();
  const { refreshAll } = useDataStore();

  // Combined loading and error states
  const isLoadingTypes = isLoadingTripTypes;
  const typesError = tripTypesError;
  const isLoading = isLoadingCountries || isLoadingTypes;
  const hasError = countriesError || typesError;
  const hasData = countries.length > 0 && tripTypesData.length > 0;

  // User authentication
  const { userName, isLoading: isLoadingUser } = useUser();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  // Location search state (local UI state, not in useSearch hook)
  const [locationSearch, setLocationSearch] = useState('');

  // Logout handlers
  const handleLogout = () => {
    setShowLogoutConfirm(true);
  };

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

  const cancelLogout = () => {
    setShowLogoutConfirm(false);
  };

  // If still loading initial data, show loading indicator
  if (isLoading && !hasData && !hasError) {
    return null; // Will be handled by Suspense fallback
  }

  // If error fetching data and no cached data, show error with retry
  if (hasError && !hasData) {
    return <SearchPageError onRetry={refreshAll} />;
  }

  return (
    <SearchProvider>
      <SearchPageContentInner
        router={router}
        searchParams={searchParams}
        countries={countries}
        tripTypesData={tripTypesData}
        userName={userName}
        isLoadingUser={isLoadingUser}
        showLogoutConfirm={showLogoutConfirm}
        locationSearch={locationSearch}
        setLocationSearch={setLocationSearch}
        handleLogout={handleLogout}
        confirmLogout={confirmLogout}
        cancelLogout={cancelLogout}
      />
    </SearchProvider>
  );
}

function SearchPageContentInner({
  router,
  searchParams,
  countries,
  tripTypesData,
  userName,
  isLoadingUser,
  showLogoutConfirm,
  locationSearch,
  setLocationSearch,
  handleLogout,
  confirmLogout,
  cancelLogout,
}: {
  router: ReturnType<typeof useRouter>;
  searchParams: ReturnType<typeof useSearchParams>;
  countries: any[];
  tripTypesData: any[];
  userName: string | null;
  isLoadingUser: boolean;
  showLogoutConfirm: boolean;
  locationSearch: string;
  setLocationSearch: (value: string) => void;
  handleLogout: () => void;
  confirmLogout: () => void;
  cancelLogout: () => void;
}) {
  // Headless search hook - all business logic here (now uses shared context)
  const search = useSearch();
  const urlSync = useSyncSearchQuery();

  // Track if this is the initial mount to prevent unwanted scrolls
  const isInitialMount = useRef(true);
  const lastSearchParamsString = useRef<string>('');

  // Phase 1: Track page view (non-blocking)
  usePageView('search');

  // Scroll to top only on initial mount
  useEffect(() => {
    if (isInitialMount.current) {
      window.scrollTo({ top: 0, behavior: 'instant' });
      isInitialMount.current = false;
    }
  }, []);

  // Load state from URL params using useSyncSearchQuery hook
  useEffect(() => {
    const currentParamsString = searchParams.toString();
    
    // Only process if params actually changed (navigation occurred)
    if (currentParamsString === lastSearchParamsString.current) {
      return;
    }
    
    lastSearchParamsString.current = currentParamsString;

    // Only load from URL if there are params
    const hasUrlParams = searchParams.get('countries') || 
                         searchParams.get('continents') || 
                         searchParams.get('type') || 
                         searchParams.get('themes');
    
    if (hasUrlParams && countries.length > 0) {
      const loadedFilters = urlSync.loadFiltersFromUrl(searchParams, countries);
      if (Object.keys(loadedFilters).length > 0) {
        search.loadFilters(loadedFilters);
      }
    }
  }, [searchParams, countries, urlSync, search]);

  // Phase 1: Track filter changes/removals
  const currentFilters = useMemo(() => ({
    locations: search.filters.selectedLocations.map(l => l.id).join(','),
    type: search.filters.selectedType,
    themes: search.filters.selectedThemes.join(','),
    year: search.filters.selectedYear,
    month: search.filters.selectedMonth,
    minDuration: search.filters.minDuration,
    maxDuration: search.filters.maxDuration,
    budget: search.filters.maxBudget,
    difficulty: search.filters.difficulty,
  }), [search.filters]);
  
  useFilterTracking(currentFilters);

  return (
    <div className="min-h-screen bg-white">
      <LogoutConfirmModal
        isOpen={showLogoutConfirm}
        onConfirm={confirmLogout}
        onCancel={cancelLogout}
      />

      <SearchPageHeader
        userName={userName}
        isLoadingUser={isLoadingUser}
        onLogout={handleLogout}
      />

      <div className="container mx-auto px-4 py-6 md:py-8 max-w-6xl">
        {/* Clear Search Button - Positioned top right */}
        <div className="mb-4 md:mb-6 flex justify-start">
          <ClearFiltersButton
            hasActiveFilters={search.hasActiveFilters}
            onClick={() => {
              search.clearAllFilters();
              setLocationSearch('');
            }}
          />
        </div>
        
        <LocationFilterSection />
        <TripTypeFilterSection />
        <ThemeFilterSection />
        <DateFilterSection />
        <RangeFiltersSection />
        
        <SearchActions
          onSearch={search.executeSearch}
          onClear={search.clearAllFilters}
          hasActiveFilters={search.hasActiveFilters}
          onClearLocationSearch={() => setLocationSearch('')}
        />
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
