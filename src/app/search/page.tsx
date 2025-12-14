'use client';

import { useState, useEffect, useMemo, useRef, useCallback, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { 
  Search, X, ChevronDown, MapPin, Calendar, DollarSign, 
  TrendingUp, Compass, Ship, Camera, Mountain, Palmtree,
  Plane, Train, Users, Users2, Snowflake, Car, Sparkles, Globe,
  Utensils, Landmark, TreePine, Waves, Sun, PawPrint, Loader2
} from 'lucide-react';
import clsx from 'clsx';

// API URL from environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// ============================================
// TYPES
// ============================================

interface Country {
  id: number;
  name: string;
  nameHe: string;
  continent: string;
}

interface Tag {
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
// FALLBACK DATA (Used when API fails)
// ============================================

const FALLBACK_COUNTRIES: Country[] = [
  // AFRICA
  { id: 1, name: 'South Africa', nameHe: 'דרום אפריקה', continent: 'Africa' },
  { id: 2, name: 'Egypt', nameHe: 'מצרים', continent: 'Africa' },
  { id: 3, name: 'Morocco', nameHe: 'מרוקו', continent: 'Africa' },
  { id: 4, name: 'Kenya', nameHe: 'קניה', continent: 'Africa' },
  { id: 5, name: 'Tanzania', nameHe: 'טנזניה', continent: 'Africa' },
  { id: 6, name: 'Namibia', nameHe: 'נמיביה', continent: 'Africa' },
  
  // ASIA
  { id: 20, name: 'Japan', nameHe: 'יפן', continent: 'Asia' },
  { id: 21, name: 'Thailand', nameHe: 'תאילנד', continent: 'Asia' },
  { id: 22, name: 'Vietnam', nameHe: 'וייטנאם', continent: 'Asia' },
  { id: 23, name: 'Nepal', nameHe: 'נפאל', continent: 'Asia' },
  { id: 24, name: 'India', nameHe: 'הודו', continent: 'Asia' },
  { id: 25, name: 'Jordan', nameHe: 'ירדן', continent: 'Asia' },
  { id: 26, name: 'Turkey', nameHe: 'טורקיה', continent: 'Asia' },
  
  // EUROPE
  { id: 40, name: 'Greece', nameHe: 'יוון', continent: 'Europe' },
  { id: 41, name: 'Italy', nameHe: 'איטליה', continent: 'Europe' },
  { id: 42, name: 'Spain', nameHe: 'ספרד', continent: 'Europe' },
  { id: 43, name: 'France', nameHe: 'צרפת', continent: 'Europe' },
  { id: 44, name: 'Iceland', nameHe: 'איסלנד', continent: 'Europe' },
  { id: 45, name: 'Norway', nameHe: 'נורבגיה', continent: 'Europe' },
  
  // SOUTH AMERICA
  { id: 60, name: 'Peru', nameHe: 'פרו', continent: 'South America' },
  { id: 61, name: 'Argentina', nameHe: 'ארגנטינה', continent: 'South America' },
  { id: 62, name: 'Brazil', nameHe: 'ברזיל', continent: 'South America' },
  { id: 63, name: 'Chile', nameHe: 'צ\'ילה', continent: 'South America' },
  
  // NORTH & CENTRAL AMERICA
  { id: 70, name: 'United States', nameHe: 'ארצות הברית', continent: 'North & Central America' },
  { id: 71, name: 'Canada', nameHe: 'קנדה', continent: 'North & Central America' },
  { id: 72, name: 'Guatemala', nameHe: 'גואטמלה', continent: 'North & Central America' },
  { id: 73, name: 'Hawaii', nameHe: 'הוואי', continent: 'North & Central America' },
  { id: 74, name: 'Mexico', nameHe: 'מקסיקו', continent: 'North & Central America' },
  { id: 75, name: 'Panama', nameHe: 'פנמה', continent: 'North & Central America' },
  { id: 76, name: 'Cuba', nameHe: 'קובה', continent: 'North & Central America' },
  { id: 77, name: 'Costa Rica', nameHe: 'קוסטה ריקה', continent: 'North & Central America' },
  
  // OCEANIA
  { id: 80, name: 'Australia', nameHe: 'אוסטרליה', continent: 'Oceania' },
  { id: 81, name: 'New Zealand', nameHe: 'ניו זילנד', continent: 'Oceania' },
  
  // ANTARCTICA
  { id: 90, name: 'Antarctica', nameHe: 'אנטארקטיקה', continent: 'Antarctica' },
];

const MOCK_TYPE_TAGS: Tag[] = [
  { id: 1, name: 'Geographic Depth', nameHe: 'טיולי עומק גיאוגרפיים', category: 'Type' },
  { id: 2, name: 'Carnivals & Festivals', nameHe: 'קרנבלים ופסטיבלים', category: 'Type' },
  { id: 3, name: 'African Safari', nameHe: 'ספארי באפריקה', category: 'Type' },
  { id: 4, name: 'Train Tours', nameHe: 'טיולי רכבות', category: 'Type' },
  { id: 5, name: 'Geographic Cruises', nameHe: 'טיולי שייט גיאוגרפיים', category: 'Type' },
  { id: 6, name: 'Nature Hiking', nameHe: 'טיולי הליכות בטבע', category: 'Type' },
  { id: 8, name: 'Jeep Tours', nameHe: 'טיולי ג\'יפים', category: 'Type' },
  { id: 9, name: 'Snowmobile Tours', nameHe: 'טיולי אופנועי שלג', category: 'Type' },
  { id: 10, name: 'Private Groups', nameHe: 'קבוצות סגורות', category: 'Type' },
  { id: 11, name: 'Photography', nameHe: 'טיולי צילום', category: 'Type' },
];

const MOCK_THEME_TAGS: Tag[] = [
  { id: 2, name: 'Hanukkah & Christmas Lights', nameHe: 'טיולי אורות חנוכה וכריסמס', category: 'Theme' },
  { id: 13, name: 'Extreme', nameHe: 'אקסטרים', category: 'Theme' },
  { id: 14, name: 'Wildlife', nameHe: 'בעלי חיים', category: 'Theme' },
  { id: 15, name: 'Cultural & Historical', nameHe: 'תרבות והיסטוריה', category: 'Theme' },
  { id: 17, name: 'Food & Wine', nameHe: 'אוכל ויין', category: 'Theme' },
  { id: 18, name: 'Beach & Island', nameHe: 'חופים ואיים', category: 'Theme' },
  { id: 19, name: 'Mountain', nameHe: 'הרים', category: 'Theme' },
  { id: 20, name: 'Desert', nameHe: 'מדבר', category: 'Theme' },
  { id: 21, name: 'Arctic & Snow', nameHe: 'קרח ושלג', category: 'Theme' },
  { id: 22, name: 'Tropical', nameHe: 'טרופי', category: 'Theme' },
];

const CONTINENTS = [
  { value: 'Africa', nameHe: 'אפריקה' },
  { value: 'Asia', nameHe: 'אסיה' },
  { value: 'Europe', nameHe: 'אירופה' },
  { value: 'North & Central America', nameHe: 'צפון ומרכז אמריקה' },
  { value: 'South America', nameHe: 'דרום אמריקה' },
  { value: 'Oceania', nameHe: 'אוקיאניה' },
  { value: 'Antarctica', nameHe: 'אנטארקטיקה' },
];

const MONTHS_HE = [
  'ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני',
  'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר'
];

// Icon mapping for TYPE tags
const TYPE_ICONS: Record<string, any> = {
  'Geographic Depth': Globe,
  'Carnivals & Festivals': Sparkles,
  'African Safari': PawPrint,
  'Train Tours': Train,
  'Geographic Cruises': Ship,
  'Nature Hiking': Mountain,
  'Jeep Tours': Car,
  'Snowmobile Tours': Snowflake,
  'Private Groups': Users2,
  'Photography': Camera,
};

const THEME_ICONS: Record<string, any> = {
  'Hanukkah & Christmas Lights': TreePine,
  'Extreme': TrendingUp,
  'Wildlife': PawPrint,
  'Cultural & Historical': Landmark,
  'Food & Wine': Utensils,
  'Beach & Island': Waves,
  'Mountain': Mountain,
  'Desert': Sun,
  'Arctic & Snow': Snowflake,
  'Tropical': Palmtree,
};

// Country code mapping for flags
const COUNTRY_FLAGS: Record<string, string> = {
  'South Africa': 'za',
  'Egypt': 'eg',
  'Morocco': 'ma',
  'Kenya': 'ke',
  'Tanzania': 'tz',
  'Namibia': 'na',
  'Japan': 'jp',
  'Thailand': 'th',
  'Vietnam': 'vn',
  'Nepal': 'np',
  'India': 'in',
  'Jordan': 'jo',
  'Turkey': 'tr',
  'Greece': 'gr',
  'Italy': 'it',
  'Spain': 'es',
  'France': 'fr',
  'Iceland': 'is',
  'Norway': 'no',
  'Peru': 'pe',
  'Argentina': 'ar',
  'Brazil': 'br',
  'Chile': 'cl',
  'United States': 'us',
  'Canada': 'ca',
  'Costa Rica': 'cr',
  'Australia': 'au',
  'New Zealand': 'nz',
  'Antarctica': 'aq',
};

// Continent background images
const CONTINENT_IMAGES: Record<string, string> = {
  'Europe': '/images/continents/europe.png',
  'Africa': '/images/continents/africa.png',
  'Antarctica': '/images/continents/antartica.png',
  'Oceania': '/images/continents/ocenia.png',
  'North & Central America': '/images/continents/north_america.png',
  'Asia': '/images/continents/asia.png',
  'South America': '/images/continents/south_america.png',
};

// ============================================
// HELPER: Get current/future months only
// ============================================

function getAvailableMonths(selectedYear: string): { index: number; name: string }[] {
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth(); // 0-indexed

  // If no year selected or future year, show all months
  if (selectedYear === 'all' || parseInt(selectedYear) > currentYear) {
    return MONTHS_HE.map((name, index) => ({ index: index + 1, name }));
  }

  // If current year, only show current and future months
  if (parseInt(selectedYear) === currentYear) {
    return MONTHS_HE
      .map((name, index) => ({ index: index + 1, name }))
      .filter(m => m.index > currentMonth);
  }

  // Past year - show no months (shouldn't happen with year restriction)
  return [];
}

function getAvailableYears(): string[] {
  const currentYear = new Date().getFullYear();
  return [currentYear.toString(), (currentYear + 1).toString(), (currentYear + 2).toString()];
}

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
  tag: Tag; 
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

function DualRangeSlider({
  min,
  max,
  minValue,
  maxValue,
  step = 1,
  minGap = 3,
  onChange,
  label
}: {
  min: number;
  max: number;
  minValue: number;
  maxValue: number;
  step?: number;
  minGap?: number;
  onChange: (min: number, max: number) => void;
  label: string;
}) {
  const minThumbRef = useRef<HTMLDivElement>(null);
  const maxThumbRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const [isDraggingMin, setIsDraggingMin] = useState(false);
  const [isDraggingMax, setIsDraggingMax] = useState(false);

  const getPercentage = useCallback((value: number) => {
    return ((value - min) / (max - min)) * 100;
  }, [min, max]);

  const getValue = useCallback((percentage: number) => {
    const rawValue = (percentage / 100) * (max - min) + min;
    return Math.round(rawValue / step) * step;
  }, [min, max, step]);

  const handleMouseMove = useCallback((e: MouseEvent | TouchEvent) => {
    if (!trackRef.current) return;

    const rect = trackRef.current.getBoundingClientRect();
    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
    // For RTL: calculate from right edge instead of left
    const percentage = Math.max(0, Math.min(100, ((rect.right - clientX) / rect.width) * 100));
    const newValue = getValue(percentage);

    if (isDraggingMin) {
      const maxAllowed = maxValue - minGap;
      const clampedValue = Math.min(Math.max(min, newValue), maxAllowed);
      onChange(clampedValue, maxValue);
    } else if (isDraggingMax) {
      const minAllowed = minValue + minGap;
      const clampedValue = Math.max(Math.min(max, newValue), minAllowed);
      onChange(minValue, clampedValue);
    }
  }, [isDraggingMin, isDraggingMax, minValue, maxValue, minGap, min, max, getValue, onChange]);

  const handleMouseUp = useCallback(() => {
    setIsDraggingMin(false);
    setIsDraggingMax(false);
  }, []);

  useEffect(() => {
    if (isDraggingMin || isDraggingMax) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.addEventListener('touchmove', handleMouseMove);
      document.addEventListener('touchend', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('touchmove', handleMouseMove);
      document.removeEventListener('touchend', handleMouseUp);
    };
  }, [isDraggingMin, isDraggingMax, handleMouseMove, handleMouseUp]);

  return (
    <div className="w-full">
      <label className="block text-sm font-medium mb-3 text-right">
        {label}: <span className="text-[#076839] font-bold">{minValue}-{maxValue} ימים</span>
      </label>
      
      {/* RTL Slider: Apply dir="rtl" to flip slider direction (min on right, max on left) */}
      <div className="relative h-10 flex items-center" dir="rtl">
        {/* Track Background */}
        <div 
          ref={trackRef}
          className="absolute w-full h-2 bg-gray-200 rounded-full"
        />
        
        {/* Active Track (highlighted range) - Turquoise */}
        <div 
          className="absolute h-2 bg-[#12acbe] rounded-full"
          style={{
            right: `${getPercentage(minValue)}%`,
            width: `${getPercentage(maxValue) - getPercentage(minValue)}%`
          }}
        />
        
        {/* Min Thumb - Turquoise (on right in RTL) */}
        <div
          ref={minThumbRef}
          className={clsx(
            'absolute w-6 h-6 bg-[#12acbe] rounded-full cursor-grab shadow-lg border-2 border-white',
            'flex items-center justify-center transform translate-x-1/2 transition-transform',
            isDraggingMin && 'cursor-grabbing scale-110'
          )}
          style={{ right: `${getPercentage(minValue)}%` }}
          onMouseDown={() => setIsDraggingMin(true)}
          onTouchStart={() => setIsDraggingMin(true)}
        >
          <span className="text-white text-[10px] font-bold">{minValue}</span>
        </div>
        
        {/* Max Thumb - Turquoise (on left in RTL) */}
        <div
          ref={maxThumbRef}
          className={clsx(
            'absolute w-6 h-6 bg-[#12acbe] rounded-full cursor-grab shadow-lg border-2 border-white',
            'flex items-center justify-center transform translate-x-1/2 transition-transform',
            isDraggingMax && 'cursor-grabbing scale-110'
          )}
          style={{ right: `${getPercentage(maxValue)}%` }}
          onMouseDown={() => setIsDraggingMax(true)}
          onTouchStart={() => setIsDraggingMax(true)}
        >
          <span className="text-white text-[10px] font-bold">{maxValue}</span>
        </div>
      </div>
    </div>
  );
}

// ============================================
// MAIN COMPONENT
// ============================================

function SearchPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // Countries from API
  const [countries, setCountries] = useState<Country[]>(FALLBACK_COUNTRIES);
  const [isLoadingCountries, setIsLoadingCountries] = useState(true);

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

  // Fetch countries from API on mount
  useEffect(() => {
    const fetchCountries = async () => {
      try {
        const response = await fetch(`${API_URL}/api/locations`);
        if (response.ok) {
          const data = await response.json();
          if (data.countries && data.countries.length > 0) {
            // Map API response to our Country interface
            const mappedCountries: Country[] = data.countries.map((c: any) => ({
              id: c.id,
              name: c.name,
              nameHe: c.name_he || c.nameHe || c.name,
              continent: c.continent
            }));
            setCountries(mappedCountries);
          }
        }
      } catch (error) {
        console.log('Failed to fetch countries from API, using fallback data');
      } finally {
        setIsLoadingCountries(false);
      }
    };

    fetchCountries();
  }, []);

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
    
    // Check if already selected
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

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-[#076839] text-white py-4 md:py-6 shadow-lg">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between gap-4">
            {/* Empty spacer for desktop balance */}
            <div className="hidden md:block md:w-32"></div>
            
            {/* Title - Centered */}
            <div className="flex-1 text-center">
              <h1 className="text-2xl md:text-3xl font-bold text-white">
                מצא את הטיול המושלם עבורך
              </h1>
              <p className="text-gray-100 mt-1 md:mt-2 text-sm md:text-base">
                מערכת המלצות חכמה לטיולים מאורגנים
              </p>
            </div>
            
            {/* Company Logo */}
            <div className="w-16 md:w-32 flex items-center justify-end">
              <img 
                src="/images/logo/smartrip.png" 
                alt="SmartTrip Logo" 
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
              
              {/* Countries grouped by continent */}
              {Object.entries(countriesByContinent).map(([continent, countriesList]) => {
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
              })}
              
              {/* Loading indicator */}
              {isLoadingCountries && (
                <div className="p-4 text-center text-gray-500">
                  <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                  טוען יעדים...
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
            {MOCK_TYPE_TAGS.map(tag => (
              <TagCircle
                key={tag.id}
                tag={tag}
                isSelected={selectedType === tag.id}
                onClick={() => setSelectedType(selectedType === tag.id ? null : tag.id)}
                iconMap={TYPE_ICONS}
              />
            ))}
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
            {MOCK_THEME_TAGS.map(tag => (
              <TagCircle
                key={tag.id}
                tag={tag}
                isSelected={selectedThemes.includes(tag.id)}
                onClick={() => toggleTheme(tag.id)}
                iconMap={THEME_ICONS}
              />
            ))}
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-12 h-12 text-emerald-400 animate-spin mx-auto mb-4" />
        <p className="text-white text-lg">Loading...</p>
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
