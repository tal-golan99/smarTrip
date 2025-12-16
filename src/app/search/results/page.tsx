'use client';

import React, { useState, useEffect, Suspense, useRef, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Image from 'next/image';
import { ArrowRight, Loader2, CheckCircle, AlertCircle, Clock, XCircle } from 'lucide-react';
import clsx from 'clsx';

// Phase 1: Tracking imports
import {
  usePageView,
  useResultsTracking,
  useImpressionTracking,
  trackTripClick,
  flushPendingEvents,
  ClickSource,
} from '@/lib/useTracking';

// API URL from environment variable (set in Vercel)
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

interface Country {
  id: number;
  name: string;
  name_he: string;
  continent: string;
}

interface Trip {
  id: number;
  title?: string;
  title_he?: string;
  titleHe?: string;
  description?: string;
  description_he?: string;
  descriptionHe?: string;
  image_url?: string;
  imageUrl?: string;
  start_date?: string;
  startDate?: string;
  end_date?: string;
  endDate?: string;
  price: number;
  spots_left?: number;
  spotsLeft?: number;
  status?: string;
  country?: Country;
  country_id?: number;
  countryId?: number;
}

interface Guide {
  id: number;
  name: string;
  name_he?: string;
}

interface SearchResult {
  trip: Trip;
  match_score: number;
  match_details: string[];
  guide?: Guide;
}

interface ScoreThresholds {
  HIGH: number;
  MID: number;
}

// Score color coding helper
const getScoreColor = (score: number, thresholds: ScoreThresholds): 'high' | 'mid' | 'low' => {
  if (score >= thresholds.HIGH) return 'high';
  if (score >= thresholds.MID) return 'mid';
  return 'low';
};

const getScoreBgClass = (colorLevel: 'high' | 'mid' | 'low'): string => {
  switch (colorLevel) {
    case 'high':
      return 'bg-[#12acbe]';  // Turquoise - excellent
    case 'mid':
      return 'bg-[#f59e0b]';  // Orange - medium
    case 'low':
      return 'bg-[#ef4444]';  // Red - low
  }
};

// Status translation to Hebrew
const getStatusLabel = (status?: string): string => {
  const statusMap: Record<string, string> = {
    'GUARANTEED': 'יציאה מובטחת',
    'LAST_PLACES': 'מקומות אחרונים',
    'OPEN': 'הרשמה פתוחה',
    'FULL': 'מלא',
    'CANCELLED': 'בוטל',
  };
  // Normalize status: uppercase and replace spaces with underscores
  const statusNormalized = status?.toUpperCase().replace(/\s+/g, '_');
  return statusNormalized ? statusMap[statusNormalized] || 'הרשמה פתוחה' : 'הרשמה פתוחה';
};

// Status icon mapping - using image files
const getStatusIconUrl = (status?: string): string | null => {
  // Normalize status: uppercase and replace spaces with underscores
  const statusNormalized = status?.toUpperCase().replace(/\s+/g, '_');
  switch (statusNormalized) {
    case 'GUARANTEED':
      return '/images/trip status/guaranteed.svg';
    case 'LAST_PLACES':
      return '/images/trip status/last places.svg';
    case 'OPEN':
      return '/images/trip status/open.svg';
    case 'FULL':
      return '/images/trip status/full.png';
    default:
      return null;
  }
};

// Fallback icon mapping (Lucide icons as backup)
const getStatusIcon = (status?: string) => {
  // Normalize status: uppercase and replace spaces with underscores
  const statusNormalized = status?.toUpperCase().replace(/\s+/g, '_');
  switch (statusNormalized) {
    case 'GUARANTEED':
      return CheckCircle;
    case 'LAST_PLACES':
      return AlertCircle;
    case 'OPEN':
      return Clock;
    case 'FULL':
      return XCircle;
    default:
      return Clock;
  }
};

// Generate dynamic background image based on country
const getDynamicImage = (trip: Trip): string => {
  // Try to get country name for dynamic image
  const countryName = trip.country?.name || 'landscape';
  // Use pollinations.ai for high-quality, unique images
  return `https://image.pollinations.ai/prompt/beautiful%20landscape%20view%20of%20${encodeURIComponent(countryName)}%20travel%20destination?width=1200&height=600&nologo=true`;
};

// ============================================
// TRIP RESULT CARD (Phase 1: With Impression Tracking)
// ============================================

interface TripResultCardProps {
  tripId: number | undefined;
  position: number;
  score: number;
  source: ClickSource;
  onClick: () => void;
  className?: string;
  children: React.ReactNode;
}

/**
 * Trip result card wrapper with impression tracking.
 * Fires impression event when card is 50% visible.
 */
function TripResultCard({
  tripId,
  position,
  score,
  source,
  onClick,
  className,
  children,
}: TripResultCardProps) {
  // Phase 1: Track impression when card enters viewport
  const impressionRef = useImpressionTracking(tripId, position, score, source);
  
  return (
    <div
      ref={impressionRef}
      onClick={onClick}
      className={className}
    >
      {children}
    </div>
  );
}

// Helper to get trip field with both snake_case and camelCase support
const getTripField = (trip: Trip, snakeCase: string, camelCase: string): any => {
  return (trip as any)[snakeCase] || (trip as any)[camelCase];
};

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

  // Scroll to top on mount and when search params change
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
  }, [searchParams]);

  useEffect(() => {
    const fetchResults = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Build preferences from URL params
        const countries = searchParams.get('countries')?.split(',').map(Number).filter(Boolean) || [];
        const continents = searchParams.get('continents')?.split(',').filter(Boolean) || [];
        const type = searchParams.get('type');
        const themes = searchParams.get('themes')?.split(',').map(Number).filter(Boolean) || [];
        const year = searchParams.get('year');
        const month = searchParams.get('month');
        const minDuration = Number(searchParams.get('minDuration')) || 7;
        const maxDuration = Number(searchParams.get('maxDuration')) || 21;
        const budget = Number(searchParams.get('budget')) || 5000;
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

        // Log the API URL being used (for debugging)
        console.log('Fetching recommendations from:', `${API_URL}/api/recommendations`);
        console.log('Request preferences:', preferences);

        // Phase 1: Track response time
        const startTime = Date.now();

        const response = await fetch(`${API_URL}/api/recommendations`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(preferences),
        });

        // Phase 1: Calculate response time
        const endTime = Date.now();
        setResponseTimeMs(endTime - startTime);

        console.log('Response status:', response.status, response.ok);

        if (!response.ok) {
          const errorText = await response.text();
          console.error('API error response:', response.status, errorText);
          throw new Error(`Failed to fetch recommendations: ${response.status}`);
        }

        const data = await response.json();
        console.log('API response data:', { success: data.success, count: data.count, totalTrips: data.total_trips, resultsLength: data.data?.length });
        
        setResults(data.data || []);
        setTotalTrips(data.total_trips || 0);
        setPrimaryCount(data.primary_count || data.count || 0);
        setRelaxedCount(data.relaxed_count || 0);
        setHasRelaxedResults(data.has_relaxed_results || false);
        
        // Phase 1: Store request ID for event correlation
        if (data.request_id) {
          setRequestId(data.request_id);
        }
        
        // Get score thresholds and refinement message flag from API
        if (data.score_thresholds) {
          setScoreThresholds(data.score_thresholds);
        }
        setShowRefinementMessage(data.show_refinement_message || false);
      } catch (err) {
        console.error('Search failed:', err);
        console.error('Attempted to fetch from:', `${API_URL}/api/recommendations`);
        setError('שגיאה בטעינת התוצאות. אנא נסה שוב.');
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
                const dynamicImage = getDynamicImage(trip);
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
                const tripTypeNameHe = tripType?.name_he || tripType?.nameHe || '';
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
                    {/* Background Image */}
                    <div
                      className="absolute inset-0 bg-cover bg-center transition-all duration-1000 ease-in-out group-hover:scale-105"
                      style={{
                        backgroundImage: `url(${imageUrl || dynamicImage})`,
                      }}
                    />
                    
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
                    
                    {/* Bottom-Left: Trip Type Badge (Same style as Status Badge) */}
                    {tripTypeNameHe && (
                      <div className="absolute bottom-4 left-4 px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full shadow-lg">
                        <span className="text-sm font-semibold text-white">
                          {tripTypeNameHe}
                        </span>
                      </div>
                    )}
                    
                    {/* Content - Positioned Bottom-Right by default, Centers on Hover */}
                    <div className="absolute bottom-0 right-0 p-8 text-right transition-all duration-1000 ease-in-out group-hover:inset-0 group-hover:flex group-hover:flex-col group-hover:items-center group-hover:justify-center group-hover:text-center">
                      <h3 className="text-3xl font-bold text-white mb-3 drop-shadow-lg">
                        {title}
                      </h3>
                      
                      <p className="text-white/90 text-base mb-3 drop-shadow-md line-clamp-2 max-w-2xl">
                        {description}
                      </p>
                      
                      {/* Guide Name (Hebrew ONLY - Enhanced Styling) */}
                      {result?.guide?.name_he && (
                        <p className="text-gray-200 text-sm mb-3 drop-shadow-lg font-medium">
                          בהדרכה של: <span className="text-white font-bold">{result.guide.name_he}</span>
                        </p>
                      )}
                      
                      <div className="text-white drop-shadow-md text-lg font-semibold" dir="ltr">
                        {!isPrivateGroup && startDate && endDate && (
                          <span className="whitespace-nowrap">
                            {new Date(startDate).toLocaleDateString('en-GB').replace(/\//g, '.')}
                            {' - '}
                            {new Date(endDate).toLocaleDateString('en-GB').replace(/\//g, '.')}
                          </span>
                        )}
                        {trip?.price && startDate && !isPrivateGroup && (
                          <span className="mx-3 text-[#12acbe] text-2xl font-bold">|</span>
                        )}
                        {trip?.price && (
                          <span className="whitespace-nowrap">
                            ${trip.price.toLocaleString()}
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
