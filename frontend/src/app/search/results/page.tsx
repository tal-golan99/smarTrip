'use client';

import React, { useState, useEffect, Suspense, useRef, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Image from 'next/image';
import { ArrowRight, Loader2 } from 'lucide-react';
import clsx from 'clsx';

// Phase 1: Tracking imports
import {
  usePageView,
  useResultsTracking,
  useImpressionTracking,
  trackTripClick,
  flushPendingEvents,
  ClickSource,
} from '@/hooks/useTracking';
import { trackEvent } from '@/services/tracking.service';
import type { Trip, Country, Guide, RecommendedTrip } from '@/services/api.service';
import { getRecommendations } from '@/services/api.service';

interface SearchResult {
  trip: Trip;
  match_score: number;
  match_details: string[];
  guide?: Guide;
}

import {
  getScoreColor,
  getScoreBgClass,
  getStatusLabel,
  getStatusIconUrl,
  getStatusIcon,
  getTripField,
  type ScoreThresholds,
} from '@/lib/utils';
import { TripResultCard } from '@/components/features/TripResultCard';


// ============================================
// TRIP RESULT CARD (Phase 1: With Impression Tracking)
// ============================================



// ============================================
// SCROLL DEPTH TRACKING HOOK (Phase 1)
// ============================================

/**
 * Track how far user scrolls through results.
 * Fires events at 25%, 50%, 75%, and 100% thresholds.
 */
function useScrollDepthTracking(totalResults: number, isLoading: boolean) {
  const trackedDepthsRef = useRef(new Set<number>());
  const scrollStartTimeRef = useRef<number | null>(null);
  
  useEffect(() => {
    // Reset when results change
    trackedDepthsRef.current = new Set<number>();
    scrollStartTimeRef.current = Date.now();
  }, [totalResults]);
  
  useEffect(() => {
    if (isLoading || totalResults === 0) return;
    
    const handleScroll = () => {
      const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (scrollHeight <= 0) return;
      
      const scrollPercent = Math.floor((window.scrollY / scrollHeight) * 100);
      const thresholds = [25, 50, 75, 100];
      
      for (const threshold of thresholds) {
        if (scrollPercent >= threshold && !trackedDepthsRef.current.has(threshold)) {
          trackedDepthsRef.current.add(threshold);
          
          const timeOnPage = scrollStartTimeRef.current 
            ? Math.floor((Date.now() - scrollStartTimeRef.current) / 1000)
            : 0;
          
          trackEvent('scroll_depth', {
            metadata: {
              depth_percent: threshold,
              trips_visible: Math.ceil((threshold / 100) * totalResults),
              time_on_page_seconds: timeOnPage,
            },
          });
        }
      }
    };
    
    // Throttle scroll events
    let ticking = false;
    const throttledScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          handleScroll();
          ticking = false;
        });
        ticking = true;
      }
    };
    
    window.addEventListener('scroll', throttledScroll, { passive: true });
    return () => window.removeEventListener('scroll', throttledScroll);
  }, [totalResults, isLoading]);
}

function SearchResultsPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const [results, setResults] = useState<SearchResult[]>([]);
  const [totalTrips, setTotalTrips] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scoreThresholds, setScoreThresholds] = useState<ScoreThresholds>({ HIGH: 70, MID: 50 });
  const [showRefinementMessage, setShowRefinementMessage] = useState(false);
  const [hasRelaxedResults, setHasRelaxedResults] = useState(false);
  const [primaryCount, setPrimaryCount] = useState(0);
  const [relaxedCount, setRelaxedCount] = useState(0);
  const [responseTimeMs, setResponseTimeMs] = useState(0);
  const [requestId, setRequestId] = useState<string | undefined>();
  
  // Phase 1: Track page view
  usePageView('search_results');
  
  // Phase 1: Track results view (fires when results are loaded)
  useResultsTracking(
    !isLoading && results.length > 0
      ? {
          resultCount: results.length,
          primaryCount,
          relaxedCount,
          topScore: results[0]?.match_score || null,
          responseTimeMs,
          recommendationRequestId: requestId,
        }
      : null
  );
  
  // Phase 1: Track scroll depth through results
  useScrollDepthTracking(results.length, isLoading);

  // Scroll to top on mount and when search params change
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
  }, [searchParams]);

  useEffect(() => {
    const fetchResults = async () => {
      // Build preferences from URL params
      const countries = searchParams.get('countries')?.split(',').map(Number).filter(Boolean) || [];
      const continents = searchParams.get('continents')?.split(',').filter(Boolean) || [];
      const type = searchParams.get('type');
      const themes = searchParams.get('themes')?.split(',').map(Number).filter(Boolean) || [];
      const year = searchParams.get('year');
      const month = searchParams.get('month');
      const minDuration = Number(searchParams.get('minDuration')) || 5;
      const maxDuration = Number(searchParams.get('maxDuration')) || 30;
      const budget = Number(searchParams.get('budget')) || 15000;
      const difficulty = Number(searchParams.get('difficulty')) || 2;

      const preferences = {
        selected_countries: countries,
        selected_continents: continents,
        preferred_type_id: type ? Number(type) : undefined,
        preferred_theme_ids: themes,
        min_duration: minDuration,
        max_duration: maxDuration,
        budget: budget,
        difficulty: difficulty,
        // Send year and month as separate hard filters
        year: year || 'all',
        month: month || 'all',
      };

      // Create cache key from search params
      const cacheKey = `search_results_${searchParams.toString()}`;
      
      // Check cache first
      try {
        const cached = sessionStorage.getItem(cacheKey);
        if (cached) {
          const cachedData = JSON.parse(cached);
          const cacheAge = Date.now() - cachedData.timestamp;
          const CACHE_MAX_AGE = 5 * 60 * 1000; // 5 minutes
          
          if (cacheAge < CACHE_MAX_AGE) {
            // Use cached data immediately
            console.log('[Results] Using cached data');
            setResults(cachedData.results);
            setTotalTrips(cachedData.totalTrips);
            setPrimaryCount(cachedData.primaryCount);
            setRelaxedCount(cachedData.relaxedCount);
            setHasRelaxedResults(cachedData.hasRelaxedResults);
            setScoreThresholds(cachedData.scoreThresholds);
            setShowRefinementMessage(cachedData.showRefinementMessage);
            setResponseTimeMs(cachedData.responseTimeMs);
            if (cachedData.requestId) {
              setRequestId(cachedData.requestId);
            }
            setIsLoading(false);
            setError(null);
            return;
          } else {
            // Cache expired, remove it
            sessionStorage.removeItem(cacheKey);
          }
        }
      } catch (e) {
        console.warn('[Results] Cache read error:', e);
      }

      // No cache or expired - fetch from API
      await fetchResultsFromAPI(preferences, cacheKey, true);
    };

    const fetchResultsFromAPI = async (preferences: any, cacheKey: string, showLoading: boolean) => {
      if (showLoading) {
        setIsLoading(true);
      }
      setError(null);

      // Log the request preferences (for debugging)
      console.log('Fetching recommendations with preferences:', preferences);

      // Phase 1: Track response time
      const startTime = Date.now();

      try {
        // Use centralized API service function
        // apiFetch returns the raw response, preserving all metadata fields
        const response = await getRecommendations(preferences) as any;

        // Phase 1: Calculate response time
        const endTime = Date.now();
        const responseTime = endTime - startTime;
        setResponseTimeMs(responseTime);

        console.log('API response:', { 
          success: response.success, 
          count: response.count, 
          totalTrips: response.total_trips,
          resultsLength: response.data?.length 
        });

        if (!response.success) {
          console.error('API error:', response.error);
          // Handle timeout errors specifically
          if (response.error?.includes('timeout') || response.error?.includes('taking too long')) {
            setError('הבקשה ארכה יותר מדי זמן. אנא נסה שוב או נסה עם פחות מסננים.');
          } else {
            setError(response.error || 'שגיאה בטעינת התוצאות. אנא נסה שוב.');
          }
          setIsLoading(false);
          return;
        }

        // Convert RecommendedTrip[] to SearchResult[] format
        // response.data contains the trips array with match_score and match_details
        const searchResults: SearchResult[] = (response.data || []).map((trip: RecommendedTrip) => ({
          trip: trip as Trip,
          match_score: trip.match_score,
          match_details: trip.match_details || [],
          guide: (trip as any).guide,
        }));
        
        setResults(searchResults);
        setTotalTrips(response.total_trips || 0);
        setPrimaryCount(response.primary_count || response.count || 0);
        setRelaxedCount(response.relaxed_count || 0);
        setHasRelaxedResults(response.has_relaxed_results || false);
        
        // Phase 1: Store request ID for event correlation
        if (response.request_id) {
          setRequestId(response.request_id);
        }
        
        // Get score thresholds and refinement message flag from API
        const thresholds = response.score_thresholds || { HIGH: 70, MID: 50 };
        setScoreThresholds(thresholds);
        setShowRefinementMessage(response.show_refinement_message || false);
        
        // Cache the results
        try {
          sessionStorage.setItem(cacheKey, JSON.stringify({
            results: searchResults,
            totalTrips: response.total_trips || 0,
            primaryCount: response.primary_count || response.count || 0,
            relaxedCount: response.relaxed_count || 0,
            hasRelaxedResults: response.has_relaxed_results || false,
            scoreThresholds: thresholds,
            showRefinementMessage: response.show_refinement_message || false,
            responseTimeMs: responseTime,
            requestId: response.request_id,
            timestamp: Date.now(),
          }));
        } catch (e) {
          console.warn('[Results] Cache write error:', e);
        }
        
      } catch (fetchErr: any) {
        console.error('Search failed:', fetchErr);
        // Handle timeout errors
        if (fetchErr.name === 'AbortError' || fetchErr.message?.includes('timeout')) {
          setError('הבקשה ארכה יותר מדי זמן. אנא נסה שוב או נסה עם פחות מסננים.');
        } else {
          setError('שגיאה בטעינת התוצאות. אנא נסה שוב.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [searchParams]);

  const handleBackToSearch = () => {
    // Scroll to top before navigation
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Small delay to allow scroll animation
    setTimeout(() => {
      router.push(`/search?${searchParams.toString()}`);
    }, 100);
  };

  // Navigate to trip detail page with tracking
  const handleTripClick = (
    tripId: number,
    position: number,
    score: number,
    source: ClickSource
  ) => {
    // Phase 1: Track click with source attribution
    trackTripClick(tripId, position, score, source);
    
    // Flush events before navigation
    flushPendingEvents();
    
    router.push(`/trip/${tripId}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-[#12acbe] mx-auto mb-4" />
          <p className="text-[#5a5a5a] text-lg">מחפש את הטיולים המושלמים עבורך...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center max-w-md">
          <p className="text-red-600 text-lg mb-6">{error}</p>
          <button
            onClick={handleBackToSearch}
            className="px-6 py-3 bg-[#076839] text-white rounded-xl font-medium hover:bg-[#0ba55c] transition-all"
          >
            חזור לחיפוש
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f8fafc]">
      {/* Header with Return Button */}
      <header className="bg-[#076839] text-white py-4 md:py-6 shadow-lg">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between gap-2 md:gap-4">
            {/* Return to Search Button (Top Right in RTL) */}
            <button
              onClick={handleBackToSearch}
              className="flex items-center gap-2 px-3 md:px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-all flex-shrink-0"
            >
              <ArrowRight className="w-4 h-4 md:w-5 md:h-5" />
              <span className="text-xs md:text-sm font-medium hidden sm:inline">חזור לחיפוש</span>
            </button>
            
            {/* Title - Centered and responsive */}
            <h1 className="text-xl md:text-2xl lg:text-3xl font-bold text-center text-white flex-1">
              {results.length > 0 
                ? `נמצאו ${primaryCount} טיולים מומלצים עבורך` 
                : 'לא נמצאו טיולים מתאימים'}
            </h1>
            
            {/* Spacer for right alignment balance */}
            <div className="w-16 sm:w-24 md:w-32 flex-shrink-0"></div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Refinement Message - Show when top result is mid-score (orange) */}
        {showRefinementMessage && results.length > 0 && (
          <div className="mb-6 p-6 bg-gradient-to-r from-orange-50 to-amber-50 border-2 border-orange-300 rounded-xl shadow-md text-center">
            <p className="text-lg font-bold text-orange-800 mb-4">
              רוצה שהאלגוריתם יקלע בול לטעם שלך?
            </p>
            <button
              onClick={handleBackToSearch}
              className="inline-flex items-center gap-2 px-6 py-3 bg-orange-500 text-white rounded-xl font-bold hover:bg-orange-600 transition-all shadow-lg"
            >
              <ArrowRight className="w-5 h-5" />
              סינון קריטריונים נוספים
            </button>
          </div>
        )}

        {results.length === 0 ? (
          <div className="text-center py-16">
            <div className="max-w-2xl mx-auto">
              <p className="text-[#5a5a5a] text-xl leading-relaxed mb-8">
                אומנם לא מצאנו התאמה מדויקת הפעם, אבל מתוך{' '}
                <span className="font-bold text-[#076839]">{totalTrips}</span> הטיולים שקיימים באתר – בטוח יש אחד שיתאים בול.
              </p>
              <button
                onClick={handleBackToSearch}
                className="inline-flex items-center gap-2 px-8 py-4 bg-[#076839] text-white rounded-xl font-bold text-lg hover:bg-[#0ba55c] transition-all shadow-lg"
              >
                <ArrowRight className="w-6 h-6" />
                חזור לחיפוש
              </button>
            </div>
          </div>
        ) : (
          <>
            {/* Results List (Vertical) */}
            <div className="space-y-6 mb-8">
              {results.map((result, index) => {
                const trip = result.trip || result;
                const tripId = trip?.id;
                const isRelaxed = (result as any).is_relaxed || false;
                const isFirstRelaxed = isRelaxed && (index === 0 || !(results[index - 1] as any).is_relaxed);
                
                return (
                  <React.Fragment key={tripId || index}>
                    {/* Separator before first relaxed result */}
                    {isFirstRelaxed && (
                      <div className="my-8 py-6">
                        <div className="flex items-center gap-4 mb-4">
                          <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
                          <span className="text-xl font-bold text-gray-700 px-4">תוצאות מורחבות</span>
                          <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
                        </div>
                        <p className="text-center text-gray-600 text-sm">
                          כדי לא להשאיר אתכם בלי כלום, האלגוריתם שלנו איתר יעדים נוספים שקרובים מאוד להעדפות שהגדרתם.
                        </p>
                      </div>
                    )}
                    
                    {(() => {
                
                // Get fields with both naming conventions support
                const title = getTripField(trip, 'title_he', 'titleHe') || getTripField(trip, 'title', 'title') || 'טיול מומלץ';
                const description = getTripField(trip, 'description_he', 'descriptionHe') || getTripField(trip, 'description', 'description') || '';
                const imageUrl = getTripField(trip, 'image_url', 'imageUrl');
                const startDate = getTripField(trip, 'start_date', 'startDate');
                const endDate = getTripField(trip, 'end_date', 'endDate');
                const spotsLeft = getTripField(trip, 'spots_left', 'spotsLeft');
                const tripType = getTripField(trip, 'trip_type', 'tripType') || getTripField(trip, 'type', 'type');
                const tripTypeNameHe = tripType?.nameHe || '';
                const tripTypeId = getTripField(trip, 'trip_type_id', 'tripTypeId');
                const isPrivateGroup = tripTypeId === 10;
                
                // Phase 1: Determine source for click attribution
                const clickSource: ClickSource = isRelaxed ? 'relaxed_results' : 'search_results';
                const matchScore = result?.match_score || 0;
                
                return (
                  <TripResultCard
                    key={tripId || index}
                    tripId={tripId}
                    position={index}
                    score={matchScore}
                    source={clickSource}
                    onClick={() => tripId && handleTripClick(tripId, index, matchScore, clickSource)}
                    className="group block relative h-80 rounded-xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-500 cursor-pointer"
                  >
                    {/* Background */}
                    <div className="absolute inset-0 bg-gray-400" />
                    
                    {/* Overlay */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/40 to-black/20 group-hover:from-black/80 group-hover:via-black/60 group-hover:to-black/40 transition-all duration-1000 ease-in-out" />
                    
                    {/* Top-Right: Match Score Badge with Color Coding */}
                    {(() => {
                      const score = result?.match_score || 0;
                      const colorLevel = getScoreColor(score, scoreThresholds);
                      const bgClass = getScoreBgClass(colorLevel);
                      return (
                        <div className={clsx(
                          "absolute top-4 right-4 px-4 py-2 rounded-full shadow-lg",
                          bgClass
                        )}>
                          <span className="text-2xl font-bold text-white">{score}</span>
                        </div>
                      );
                    })()}
                    
                    {/* Top-Left: Status Badge (Text + Icon) */}
                    {trip?.status && (
                      <div 
                        className="absolute top-4 left-4 px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full flex flex-row items-center gap-2"
                      >
                        {/* Text on Left */}
                        <span className="text-sm font-semibold text-white">
                          {getStatusLabel(trip.status)}
                        </span>
                        
                        {/* Icon on Right - Try image first, fallback to Lucide */}
                        {(() => {
                          const iconUrl = getStatusIconUrl(trip.status);
                          if (iconUrl) {
                            return (
                              <img 
                                src={iconUrl} 
                                alt={getStatusLabel(trip.status)}
                                className="w-5 h-5"
                                onError={(e) => {
                                  // Fallback to Lucide icon if image fails
                                  e.currentTarget.style.display = 'none';
                                }}
                              />
                            );
                          } else {
                            const StatusIcon = getStatusIcon(trip.status);
                            return <StatusIcon className="w-5 h-5 text-white" />;
                          }
                        })()}
                      </div>
                    )}
                    
                    {/* Bottom-Left: Trip Type Badge - Fixed to bottom-left corner of card */}
                    {tripTypeNameHe && (
                      <div className="absolute bottom-3 left-3 px-3 py-1.5 md:px-4 md:py-2 bg-white/20 backdrop-blur-sm rounded-full shadow-lg">
                        <span className="text-xs md:text-sm font-semibold text-white">
                          {tripTypeNameHe}
                        </span>
                      </div>
                    )}
                    
                    {/* Content - Positioned Bottom-Right by default, Centers on Hover - Extra left padding to avoid badge collision */}
                    <div className="absolute bottom-0 right-0 left-0 p-4 pb-3 pl-36 md:pl-48 md:p-8 text-right transition-all duration-1000 ease-in-out group-hover:inset-0 group-hover:flex group-hover:flex-col group-hover:items-center group-hover:justify-center group-hover:text-center group-hover:pl-0">
                      <h3 className="text-2xl md:text-3xl font-bold text-white mb-2 md:mb-3 drop-shadow-lg">
                        {title}
                      </h3>
                      
                      <p className="text-white/90 text-sm md:text-base mb-2 md:mb-3 drop-shadow-md line-clamp-2 max-w-2xl">
                        {description}
                      </p>
                      
                      {/* Guide Name (Hebrew ONLY - Enhanced Styling) */}
                      {result?.guide?.name && (
                        <p className="text-gray-200 text-xs md:text-sm mb-2 md:mb-3 drop-shadow-lg font-medium">
                          בהדרכה של: <span className="text-white font-bold">{result.guide.name}</span>
                        </p>
                      )}
                      
                      <div className="text-white drop-shadow-md text-base md:text-lg font-semibold" dir="ltr">
                        {!isPrivateGroup && startDate && endDate && (
                          <span className="whitespace-nowrap text-sm md:text-lg">
                            {new Date(startDate).toLocaleDateString('en-GB').replace(/\//g, '.')}
                            {' - '}
                            {new Date(endDate).toLocaleDateString('en-GB').replace(/\//g, '.')}
                          </span>
                        )}
                        {trip?.price && startDate && !isPrivateGroup && (
                          <span className="mx-2 md:mx-3 text-[#12acbe] text-xl md:text-2xl font-bold">|</span>
                        )}
                        {trip?.price && (
                          <span className="whitespace-nowrap text-sm md:text-lg">
                            ${Math.round(trip.price).toLocaleString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </TripResultCard>
                );
              })()}
                  </React.Fragment>
                );
              })}
            </div>

            {/* Back to Search Button */}
            <div className="text-center pt-4">
              <button
                onClick={handleBackToSearch}
                className="inline-flex items-center gap-2 px-8 py-4 bg-[#076839] text-white rounded-xl font-bold text-lg hover:bg-[#0ba55c] transition-all shadow-lg hover:shadow-xl"
              >
                <ArrowRight className="w-6 h-6" />
                חזור לחיפוש
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// ============================================
// SUSPENSE WRAPPER FOR NEXT.JS 14 STATIC GENERATION
// ============================================

function ResultsPageLoading() {
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
        <p className="text-white text-xl font-medium mb-2">טוען תוצאות...</p>
        <p className="text-white/80 text-sm">טעינה ראשונית עשויה לקחת מספר רגעים</p>
      </div>
    </div>
  );
}

export default function SearchResultsPage() {
  return (
    <Suspense fallback={<ResultsPageLoading />}>
      <SearchResultsPageContent />
    </Suspense>
  );
}
