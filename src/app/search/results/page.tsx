'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowRight, Loader2, CheckCircle, AlertCircle, Clock, XCircle } from 'lucide-react';
import clsx from 'clsx';

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

// Status translation to Hebrew
const getStatusLabel = (status?: string): string => {
  const statusMap: Record<string, string> = {
    'GUARANTEED': 'יציאה מובטחת',
    'LAST_PLACES': 'מקומות אחרונים',
    'OPEN': 'הרשמה פתוחה',
    'FULL': 'מלא',
    'CANCELLED': 'בוטל',
  };
  return status ? statusMap[status.toUpperCase()] || 'הרשמה פתוחה' : 'הרשמה פתוחה';
};

// Status icon mapping - using image files
const getStatusIconUrl = (status?: string): string | null => {
  const statusUpper = status?.toUpperCase();
  switch (statusUpper) {
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
  const statusUpper = status?.toUpperCase();
  switch (statusUpper) {
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

  // Scroll to top on mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

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
          start_date: year && year !== 'all' && month && month !== 'all'
            ? `${year}-${month.padStart(2, '0')}-01`
            : undefined,
        };

        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/922e0c9a-fc2e-4baa-9d6c-cdb2a1ae398a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'results/page.tsx:156',message:'Sending request to backend',data:{preferences},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'A'})}).catch(()=>{});
        // #endregion

        const response = await fetch('http://localhost:5000/api/recommendations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(preferences),
        });

        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/922e0c9a-fc2e-4baa-9d6c-cdb2a1ae398a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'results/page.tsx:163',message:'Response received',data:{ok:response.ok,status:response.status},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'B'})}).catch(()=>{});
        // #endregion

        if (!response.ok) {
          // #region agent log
          const errorText = await response.text();
          fetch('http://127.0.0.1:7242/ingest/922e0c9a-fc2e-4baa-9d6c-cdb2a1ae398a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'results/page.tsx:167',message:'API error response',data:{status:response.status,errorText},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'B'})}).catch(()=>{});
          // #endregion
          throw new Error('Failed to fetch recommendations');
        }

        const data = await response.json();
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/922e0c9a-fc2e-4baa-9d6c-cdb2a1ae398a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'results/page.tsx:180',message:'Response data parsed',data:{success:data.success,count:data.count,dataLength:data.data?.length,sampleTrip:data.data?.[0]},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'D'})}).catch(()=>{});
        // #endregion
        setResults(data.data || []);
        setTotalTrips(data.total_candidates || 0);
      } catch (err) {
        console.error('Error fetching results:', err);
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/922e0c9a-fc2e-4baa-9d6c-cdb2a1ae398a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'results/page.tsx:187',message:'Frontend error caught',data:{errorMessage:err instanceof Error ? err.message : String(err),errorStack:err instanceof Error ? err.stack : undefined},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'B'})}).catch(()=>{});
        // #endregion
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

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
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
      {/* Header */}
      <header className="bg-[#076839] text-white py-6 shadow-lg">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold text-center text-white">
            {results.length > 0 
              ? `נמצאו ${results.length} טיולים מומלצים עבורך` 
              : 'לא נמצאו טיולים מתאימים'}
          </h1>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {results.length === 0 ? (
          <div className="text-center py-16">
            <div className="max-w-2xl mx-auto">
              <p className="text-[#5a5a5a] text-2xl font-bold mb-4">
                לצערנו, אין טיולים שמתאימים לקריטריונים שבחרת.
              </p>
              <p className="text-[#5a5a5a] text-xl mb-8">
                אך שתדע שיש לנו <span className="font-bold text-[#076839]">{totalTrips}</span> טיולים באתר.
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
                const tripUrl = `https://www.ayalageo.co.il/trips/${trip?.id || ''}`;
                
                // Get fields with both naming conventions support
                const title = getTripField(trip, 'title_he', 'titleHe') || getTripField(trip, 'title', 'title') || 'טיול מומלץ';
                const description = getTripField(trip, 'description_he', 'descriptionHe') || getTripField(trip, 'description', 'description') || '';
                const imageUrl = getTripField(trip, 'image_url', 'imageUrl');
                const startDate = getTripField(trip, 'start_date', 'startDate');
                const endDate = getTripField(trip, 'end_date', 'endDate');
                const spotsLeft = getTripField(trip, 'spots_left', 'spotsLeft');
                
                return (
                  <a
                    key={trip?.id || index}
                    href={tripUrl}
                    target="_blank"
                    rel="noopener noreferrer"
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
                    
                    {/* Top-Right: Match Score Badge */}
                    <div className="absolute top-4 right-4 px-4 py-2 bg-[#12acbe] rounded-full shadow-lg">
                      <span className="text-2xl font-bold text-white">{result?.match_score || 0}%</span>
                    </div>
                    
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
                                  const StatusIcon = getStatusIcon(trip.status);
                                  e.currentTarget.style.display = 'none';
                                  const iconElement = document.createElement('div');
                                  iconElement.innerHTML = `<svg class="w-5 h-5 text-white"></svg>`;
                                  e.currentTarget.parentElement?.appendChild(iconElement);
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
                    
                    {/* Content - Positioned Bottom-Right by default, Centers on Hover */}
                    <div className="absolute bottom-0 right-0 p-8 text-right transition-all duration-1000 ease-in-out group-hover:inset-0 group-hover:flex group-hover:flex-col group-hover:items-center group-hover:justify-center group-hover:text-center">
                      <h3 className="text-3xl font-bold text-white mb-3 drop-shadow-lg">
                        {title}
                      </h3>
                      
                      <p className="text-white/90 text-base mb-3 drop-shadow-md line-clamp-2 max-w-2xl">
                        {description}
                      </p>
                      
                      {/* Guide Name (Hebrew Only) */}
                      {(result?.guide?.name_he || result?.guide?.name) && (
                        <p className="text-gray-300 text-sm mb-3 drop-shadow-md">
                          בהדרכה של: {result.guide.name_he || result.guide.name}
                        </p>
                      )}
                      
                      <div className="text-white drop-shadow-md text-lg font-semibold" dir="ltr">
                        {startDate && endDate && (
                          <span className="whitespace-nowrap">
                            {new Date(startDate).toLocaleDateString('en-GB').replace(/\//g, '.')}
                            {' - '}
                            {new Date(endDate).toLocaleDateString('en-GB').replace(/\//g, '.')}
                          </span>
                        )}
                        {trip?.price && startDate && (
                          <span className="mx-3 text-[#12acbe] text-2xl font-bold">|</span>
                        )}
                        {trip?.price && (
                          <span className="whitespace-nowrap">
                            ${trip.price.toLocaleString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </a>
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-12 h-12 text-emerald-400 animate-spin mx-auto mb-4" />
        <p className="text-white text-lg">Loading results...</p>
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

