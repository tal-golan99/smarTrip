/**
 * Trip details page - Displays full information about a specific trip.
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Image from 'next/image';
import { ArrowRight, Calendar, Clock, DollarSign, MapPin, User, X, Loader2 } from 'lucide-react';
import clsx from 'clsx';

// Phase 1: Tracking imports
import {
  usePageView,
  useTripDwellTime,
  trackWhatsAppContact,
  trackPhoneContact,
  trackSaveTrip,
} from '@/hooks/useTracking';
import type { TripOccurrence } from '@/api';
import { getTripOccurrence } from '@/api';
import {
  formatDate,
  calculateDuration,
  getDifficultyLabel,
  getStatusLabel,
} from '@/lib/utils';
import { RegistrationModal } from '@/components/features/RegistrationModal';

// Modal Component

export default function TripPage() {
  const router = useRouter();
  const params = useParams();
  const tripId = params.id as string;
  let tripIdNum: number | undefined;
  if (tripId) {
    const parsed = parseInt(tripId, 10);
    tripIdNum = isNaN(parsed) ? undefined : parsed;
  } else {
    tripIdNum = undefined;
  }
  
  const [trip, setTrip] = useState<TripOccurrence | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Phase 1: Track page view
  usePageView('trip_detail');
  
  // Phase 1: Track dwell time (fires on unmount if > 2 seconds)
  useTripDwellTime(tripIdNum);

  // Scroll to top on mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Fetch trip data
  useEffect(() => {
    const fetchTrip = async () => {
      if (!tripId || !tripIdNum) return;
      
      setIsLoading(true);
      setError(null);

      try {
        const response = await getTripOccurrence(tripIdNum);
        
        if (!response.success || !response.data) {
          if (response.error?.includes('404') || response.error?.includes('not found')) {
            throw new Error('הטיול לא נמצא');
          }
          throw new Error(response.error || 'שגיאה בטעינת פרטי הטיול');
        }

        setTrip(response.data);
      } catch (err) {
        console.error('Error fetching trip:', err);
        setError(err instanceof Error ? err.message : 'שגיאה בטעינת פרטי הטיול');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrip();
  }, [tripId, tripIdNum]);

  const handleBack = () => {
    router.back();
  };

  const handleRegister = () => {
    setIsModalOpen(true);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-[#12acbe] mx-auto mb-4" />
          <p className="text-[#5a5a5a] text-lg">טוען פרטי טיול...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !trip) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center max-w-md px-4">
          <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-red-100 flex items-center justify-center">
            <X className="w-8 h-8 text-red-500" />
          </div>
          <p className="text-red-600 text-xl font-bold mb-4">{error || 'הטיול לא נמצא'}</p>
          <button
            onClick={handleBack}
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#076839] text-white rounded-xl font-medium hover:bg-[#0ba55c] transition-all"
          >
            <ArrowRight className="w-5 h-5" />
            חזור לתוצאות
          </button>
        </div>
      </div>
    );
  }

  // Get trip fields from nested structure (TripOccurrence with template)
  const template = trip.template;
  if (!template) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center max-w-md px-4">
          <p className="text-red-600 text-xl font-bold mb-4">שגיאה: תבנית הטיול לא נמצאה</p>
          <button
            onClick={handleBack}
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#076839] text-white rounded-xl font-medium hover:bg-[#0ba55c] transition-all"
          >
            <ArrowRight className="w-5 h-5" />
            חזור לתוצאות
          </button>
        </div>
      </div>
    );
  }
  
  const title = template.titleHe || template.title || 'טיול מומלץ';
  const description = template.descriptionHe || template.description || '';
  const startDate = trip.startDate;
  const endDate = trip.endDate;
  const duration = calculateDuration(startDate, endDate);
  const guideName = trip.guide?.name || '';
  const countryName = template.primaryCountry?.nameHe || template.primaryCountry?.name || '';
  const difficultyLevel = template.difficultyLevel;
  const spotsLeft = trip.spotsLeft;
  const tripType = template.tripType;
  const isPrivateGroup = tripType?.name === 'Private Groups' || tripType?.nameHe === 'קבוצות פרטיות';
  
  // Get effective price
  const price = trip.effectivePrice || trip.priceOverride || template.basePrice || 0;
  
  // Get effective image URL
  const imageUrl = trip.effectiveImageUrl || trip.imageUrlOverride || template.imageUrl;

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Hero Section */}
      <div className="relative h-[50vh] md:h-[60vh] bg-gray-400">
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-black/20" />
        
        {/* Back Button (Top Right) */}
        <button
          onClick={handleBack}
          className="absolute top-6 right-6 z-10 flex items-center gap-2 px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full text-white hover:bg-white/30 transition-all"
        >
          <span className="text-sm font-medium">חזרה</span>
          <ArrowRight className="w-4 h-4" />
        </button>
        
        {/* Status Badge (Top Left) */}
        {trip.status && (
          <div className="absolute top-6 left-6 px-4 py-2 bg-[#12acbe] rounded-full shadow-lg">
            <span className="text-sm font-bold text-white">{getStatusLabel(trip.status)}</span>
          </div>
        )}
        
        {/* Title Overlay (Bottom) */}
        <div className="absolute bottom-0 left-0 right-0 p-6 md:p-10">
          <div className="container mx-auto max-w-4xl">
            <h1 className="text-3xl md:text-5xl font-bold text-white drop-shadow-lg text-right">
              {title}
            </h1>
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="flex-1 container mx-auto max-w-4xl px-4 py-8 md:py-12">
        {/* Quick Info Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {/* Dates */}
          <div className="bg-gray-50 rounded-xl p-4 text-center">
            <Calendar className="w-6 h-6 text-[#12acbe] mx-auto mb-2" />
            <p className="text-xs text-gray-500 mb-1">תאריכים</p>
            <p className="text-sm font-bold text-[#5a5a5a]" dir="ltr">
              {isPrivateGroup ? 'ניתן לקבוע מול המדריך' : `${formatDate(startDate)} - ${formatDate(endDate)}`}
            </p>
          </div>
          
          {/* Duration */}
          <div className="bg-gray-50 rounded-xl p-4 text-center">
            <Clock className="w-6 h-6 text-[#12acbe] mx-auto mb-2" />
            <p className="text-xs text-gray-500 mb-1">משך הטיול</p>
            <p className="text-sm font-bold text-[#5a5a5a]">
              {isPrivateGroup ? 'ניתן לקבוע מול המדריך' : `${duration} ימים`}
            </p>
          </div>
          
          {/* Price */}
          <div className="bg-gray-50 rounded-xl p-4 text-center">
            <DollarSign className="w-6 h-6 text-[#12acbe] mx-auto mb-2" />
            <p className="text-xs text-gray-500 mb-1">מחיר</p>
            <p className="text-sm font-bold text-[#076839]">${Math.round(price).toLocaleString()}</p>
          </div>
          
          {/* Difficulty */}
          <div className="bg-gray-50 rounded-xl p-4 text-center">
            <div className="w-6 h-6 mx-auto mb-2 flex items-center justify-center">
              <div className={clsx(
                'w-4 h-4 rounded-full',
                difficultyLevel === 1 && 'bg-green-500',
                difficultyLevel === 2 && 'bg-yellow-500',
                difficultyLevel === 3 && 'bg-red-500'
              )} />
            </div>
            <p className="text-xs text-gray-500 mb-1">רמת קושי</p>
            <p className="text-sm font-bold text-[#5a5a5a]">{getDifficultyLabel(difficultyLevel)}</p>
          </div>
        </div>

        {/* Guide and Company Info */}
        <div className="flex flex-wrap gap-4 mb-8">
          {/* Guide Info */}
          {guideName && (
            <div className="flex-1 min-w-[200px] flex items-center gap-3 p-4 bg-[#12acbe]/10 rounded-xl">
              <div className="w-12 h-12 rounded-full bg-[#12acbe] flex items-center justify-center">
                <User className="w-6 h-6 text-white" />
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">בהדרכה של</p>
                <p className="text-lg font-bold text-[#076839]">{guideName}</p>
              </div>
            </div>
          )}
          
          {/* Company Info */}
          {template.company && (
            <div className="flex-1 min-w-[200px] flex items-center gap-3 p-4 bg-[#076839]/10 rounded-xl">
              <div className="w-12 h-12 rounded-full bg-[#076839] flex items-center justify-center">
                <MapPin className="w-6 h-6 text-white" />
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">מאורגן על ידי</p>
                <p className="text-lg font-bold text-[#076839]">{template.company.nameHe || template.company.name}</p>
              </div>
            </div>
          )}
        </div>

        {/* Description */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-[#5a5a5a] mb-4 text-right">אודות הטיול</h2>
          <p className="text-gray-600 text-lg leading-relaxed text-right whitespace-pre-line">
            {description}
          </p>
        </div>

        {/* Spots Left Warning - Show if LAST_PLACES status OR spotsLeft <= 4 */}
        {(trip.status?.toUpperCase().replace(/\s+/g, '_') === 'LAST_PLACES' || (spotsLeft !== undefined && spotsLeft <= 4 && spotsLeft > 0)) && (
          <div className="mb-8 p-4 bg-orange-50 border-2 border-orange-300 rounded-xl shadow-md">
            <p className="text-orange-700 font-bold text-center text-lg">
              נותרו רק {spotsLeft} מקומות אחרונים!
            </p>
          </div>
        )}
      </div>

      {/* Sticky Bottom Actions */}
      <div className="sticky bottom-0 bg-white border-t border-gray-200 shadow-lg">
        <div className="container mx-auto max-w-4xl px-4 py-4">
          <div className="flex gap-4">
            {/* Back Button (Left) */}
            <button
              onClick={handleBack}
              className="flex-1 md:flex-none px-6 py-4 border-2 border-[#076839] text-[#076839] rounded-xl font-bold text-lg hover:bg-[#076839] hover:text-white transition-all"
            >
              <span className="flex items-center justify-center gap-2">
                <ArrowRight className="w-5 h-5" />
                בחזרה לתוצאות
              </span>
            </button>
            
            {/* Register Button (Right) */}
            <button
              onClick={handleRegister}
              className="flex-1 px-8 py-4 bg-[#12acbe] text-white rounded-xl font-bold text-lg hover:bg-[#0ea5b6] transition-all shadow-lg"
            >
              להרשמה
            </button>
          </div>
        </div>
      </div>

      {/* Registration Modal */}
      <RegistrationModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
      />
    </div>
  );
}

