'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { ArrowRight, Calendar, Clock, DollarSign, MapPin, User, X, Loader2 } from 'lucide-react';
import clsx from 'clsx';

// API URL from environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

interface Country {
  id: number;
  name: string;
  name_he: string;
  continent: string;
}

interface Guide {
  id: number;
  name: string;
  name_he?: string;
}

interface TripType {
  id: number;
  name: string;
  name_he?: string;
}

interface Trip {
  id: number;
  title?: string;
  title_he?: string;
  description?: string;
  description_he?: string;
  image_url?: string;
  start_date?: string;
  end_date?: string;
  price: number;
  spots_left?: number;
  status?: string;
  difficulty_level?: number;
  country?: Country;
  guide?: Guide;
  trip_type?: TripType;
  trip_type_id?: number;
}

// Helper to get trip field with both snake_case and camelCase support
const getTripField = (trip: Trip, snakeCase: string, camelCase: string): any => {
  return (trip as any)[snakeCase] || (trip as any)[camelCase];
};

// Generate dynamic background image based on country
const getDynamicImage = (trip: Trip): string => {
  const countryName = trip.country?.name || 'landscape';
  return `https://image.pollinations.ai/prompt/beautiful%20landscape%20view%20of%20${encodeURIComponent(countryName)}%20travel%20destination?width=1200&height=600&nologo=true`;
};

// Format date to DD.MM.YYYY
const formatDate = (dateString?: string): string => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('en-GB').replace(/\//g, '.');
};

// Calculate duration in days
const calculateDuration = (startDate?: string, endDate?: string): number => {
  if (!startDate || !endDate) return 0;
  const start = new Date(startDate);
  const end = new Date(endDate);
  const diffTime = Math.abs(end.getTime() - start.getTime());
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};

// Get difficulty label in Hebrew
const getDifficultyLabel = (level?: number): string => {
  switch (level) {
    case 1: return 'קל';
    case 2: return 'בינוני';
    case 3: return 'מאתגר';
    default: return 'בינוני';
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

// Modal Component
function RegistrationModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal Content */}
      <div className="relative bg-white rounded-2xl shadow-2xl p-8 max-w-md mx-4 text-center transform animate-in zoom-in-95 duration-200">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 left-4 p-2 rounded-full hover:bg-gray-100 transition-colors"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>
        
        {/* Icon */}
        <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-[#12acbe]/10 flex items-center justify-center">
          <Calendar className="w-8 h-8 text-[#12acbe]" />
        </div>
        
        {/* Message */}
        <h3 className="text-2xl font-bold text-[#076839] mb-4">
          שים לב
        </h3>
        <p className="text-lg text-[#5a5a5a] mb-8">
          פעולה זו עדיין אינה פעילה
        </p>
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="px-8 py-3 bg-[#076839] text-white rounded-xl font-bold text-lg hover:bg-[#0ba55c] transition-all shadow-lg"
        >
          חזור
        </button>
      </div>
    </div>
  );
}

export default function TripPage() {
  const router = useRouter();
  const params = useParams();
  const tripId = params.id as string;
  
  const [trip, setTrip] = useState<Trip | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Scroll to top on mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Fetch trip data
  useEffect(() => {
    const fetchTrip = async () => {
      if (!tripId) return;
      
      setIsLoading(true);
      setError(null);

      try {
        console.log('Fetching trip:', `${API_URL}/api/trips/${tripId}`);
        
        const response = await fetch(`${API_URL}/api/trips/${tripId}`);
        
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('הטיול לא נמצא');
          }
          throw new Error('שגיאה בטעינת פרטי הטיול');
        }

        const data = await response.json();
        console.log('Trip data:', data);
        
        if (data.success && data.data) {
          setTrip(data.data);
        } else {
          throw new Error('שגיאה בטעינת פרטי הטיול');
        }
      } catch (err) {
        console.error('Error fetching trip:', err);
        setError(err instanceof Error ? err.message : 'שגיאה בטעינת פרטי הטיול');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrip();
  }, [tripId]);

  const handleBack = () => {
    router.back();
  };

  const handleRegister = () => {
    setIsModalOpen(true);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
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

  // Get trip fields
  const title = getTripField(trip, 'title_he', 'titleHe') || getTripField(trip, 'title', 'title') || 'טיול מומלץ';
  const description = getTripField(trip, 'description_he', 'descriptionHe') || getTripField(trip, 'description', 'description') || '';
  const imageUrl = getTripField(trip, 'image_url', 'imageUrl') || getDynamicImage(trip);
  const startDate = getTripField(trip, 'start_date', 'startDate');
  const endDate = getTripField(trip, 'end_date', 'endDate');
  const duration = calculateDuration(startDate, endDate);
  const guideName = trip.guide?.name_he || '';
  const countryName = trip.country?.name_he || trip.country?.name || '';
  const difficultyLevel = getTripField(trip, 'difficulty_level', 'difficultyLevel');
  const spotsLeft = getTripField(trip, 'spots_left', 'spotsLeft');
  const tripType = (trip as any).type || (trip as any).trip_type;
  const isPrivateGroup = tripType?.name === 'Private Groups' || tripType?.nameHe === 'קבוצות פרטיות';

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Hero Section */}
      <div className="relative h-[50vh] md:h-[60vh]">
        {/* Background Image */}
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${imageUrl})` }}
        />
        
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
            {/* Country Badge */}
            {countryName && (
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full mb-4">
                <MapPin className="w-4 h-4 text-white" />
                <span className="text-sm text-white font-medium">{countryName}</span>
              </div>
            )}
            
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
              {formatDate(startDate)} - {formatDate(endDate)}
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
            <p className="text-sm font-bold text-[#076839]">${trip.price?.toLocaleString()}</p>
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

        {/* Guide Info */}
        {guideName && (
          <div className="flex items-center gap-3 mb-8 p-4 bg-[#12acbe]/10 rounded-xl">
            <div className="w-12 h-12 rounded-full bg-[#12acbe] flex items-center justify-center">
              <User className="w-6 h-6 text-white" />
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">בהדרכה של</p>
              <p className="text-lg font-bold text-[#076839]">{guideName}</p>
            </div>
          </div>
        )}

        {/* Description */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-[#5a5a5a] mb-4 text-right">אודות הטיול</h2>
          <p className="text-gray-600 text-lg leading-relaxed text-right whitespace-pre-line">
            {description}
          </p>
        </div>

        {/* Spots Left Warning - Show if LAST_PLACES status OR spots_left <= 4 */}
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

