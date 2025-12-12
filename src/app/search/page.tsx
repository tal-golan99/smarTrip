'use client';

import { useState, useEffect, useMemo, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { 
  Search, X, ChevronDown, MapPin, Calendar, DollarSign, 
  TrendingUp, Compass, Ship, Camera, Mountain, Palmtree,
  Plane, Train, Users, Snowflake, Car, Sparkles, Globe,
  Utensils, Landmark, TreePine, Waves, Sun, PawPrint, Loader2
} from 'lucide-react';
import clsx from 'clsx';

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
// MOCK DATA (Based on seed.py)
// ============================================

const MOCK_COUNTRIES: Country[] = [
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
  { id: 3, name: 'Carnivals & Festivals', nameHe: 'טיולי קרנבלים ופסטיבלים', category: 'Type' },
  { id: 4, name: 'African Safari', nameHe: 'טיולי ספארי אפריקה', category: 'Type' },
  { id: 5, name: 'Train Tours', nameHe: 'טיולי רכבות', category: 'Type' },
  { id: 6, name: 'Geographic Cruises', nameHe: 'טיולי שייט גיאוגרפיים', category: 'Type' },
  { id: 7, name: 'Nature Hiking', nameHe: 'טיולי הליכות בטבע', category: 'Type' },
  { id: 9, name: 'Jeep Tours', nameHe: 'טיולי ג\'יפים', category: 'Type' },
  { id: 10, name: 'Snowmobile Tours', nameHe: 'טיולי אופנועי שלג', category: 'Type' },
  { id: 12, name: 'Photography', nameHe: 'צילום', category: 'Type' },
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
// IMPORTANT: Place these image files in public/images/continents/ folder
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

  // World map SVG for continents (simplified two-color representation)
  const getContinentMapSVG = (continent: string) => {
    const baseColor = '#e5e7eb'; // Light gray for map background
    const highlightColor = '#12acbe'; // Turquoise for highlighted continent
    
    // Simplified SVG paths for each continent (approximation)
    const continentPaths: Record<string, string> = {
      'Africa': 'M50,35 L55,30 L60,32 L62,40 L58,50 L52,48 Z',
      'Asia': 'M60,25 L75,22 L80,30 L78,40 L70,42 L62,35 Z',
      'Europe': 'M48,20 L58,18 L62,25 L58,30 L50,28 Z',
      'North & Central America': 'M20,15 L35,12 L40,25 L35,35 L25,30 Z',
      'South America': 'M30,45 L38,42 L40,55 L35,65 L28,58 Z',
      'Oceania': 'M75,50 L85,48 L88,55 L82,58 L76,55 Z',
      'Antarctica': 'M35,75 L65,75 L60,82 L40,82 Z'
    };

    return `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle cx="50" cy="50" r="48" fill="${baseColor}"/>
      <path d="${continentPaths[continent] || continentPaths['Africa']}" fill="${highlightColor}"/>
    </svg>`;
  };

  // Use uploaded continent images instead of SVG
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
          'w-24 h-24 rounded-full flex items-center justify-center relative overflow-hidden',
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
        'flex flex-col items-center gap-2 p-4 rounded-xl transition-all duration-200',
        'border-2 hover:scale-105',
        isSelected 
          ? 'bg-[#076839] border-[#12acbe] text-white' 
          : 'bg-white border-gray-200 text-[#5a5a5a] hover:border-[#12acbe]'
      )}
    >
      <div className={clsx(
        'w-12 h-12 rounded-full flex items-center justify-center',
        isSelected ? 'bg-[#12acbe]' : 'bg-gray-100'
      )}>
        <Icon className="w-6 h-6" />
      </div>
      <span className="text-xs font-medium text-center leading-tight">
        {tag.nameHe}
      </span>
    </button>
  );
}

// ============================================
// MAIN COMPONENT
// ============================================

function SearchPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // Location search state
  const [locationSearch, setLocationSearch] = useState('');
  const [isLocationDropdownOpen, setIsLocationDropdownOpen] = useState(false);
  const [selectedLocations, setSelectedLocations] = useState<LocationSelection[]>([]);

  // Tag selection state
  const [selectedType, setSelectedType] = useState<number | null>(null);
  const [selectedThemes, setSelectedThemes] = useState<number[]>([]);

  // Date filters
  const [selectedYear, setSelectedYear] = useState<string>('all');
  const [selectedMonth, setSelectedMonth] = useState<string>('all');

  // Range filters with proper defaults
  const [minDuration, setMinDuration] = useState(5);
  const [maxDuration, setMaxDuration] = useState(30);
  const [maxBudget, setMaxBudget] = useState(15000); // Set to maximum
  const [difficulty, setDifficulty] = useState<number>(2);
  
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
           difficulty !== 2;
  }, [selectedLocations, selectedType, selectedThemes, selectedYear, selectedMonth, minDuration, maxDuration, maxBudget, difficulty]);

  // Load state from URL params (for back button) - prevent duplicates
  useEffect(() => {
    // Scroll to top when returning to search
    window.scrollTo({ top: 0, behavior: 'smooth' });

    const countries = searchParams.get('countries');
    const continents = searchParams.get('continents');
    const type = searchParams.get('type');
    const themes = searchParams.get('themes');
    const year = searchParams.get('year');
    const month = searchParams.get('month');
    const minDur = searchParams.get('minDuration');
    const maxDur = searchParams.get('maxDuration');
    const budget = searchParams.get('budget');
    const diff = searchParams.get('difficulty');

    // Only load from URL if there are params
    const hasUrlParams = countries || continents || type || themes;
    
    if (hasUrlParams) {
      const newLocations: LocationSelection[] = [];
      const existingIds = new Set(selectedLocations.map(l => `${l.type}-${l.id}`));

      if (countries) {
        const countryIds = countries.split(',').map(Number);
        countryIds.forEach(id => {
          const country = MOCK_COUNTRIES.find(c => c.id === id);
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

      if (continents) {
        const continentNames = continents.split(',');
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
  }, [searchParams]);

  // Filter countries and continents by search
  const filteredCountries = useMemo(() => {
    if (!locationSearch) return MOCK_COUNTRIES;
    
    const searchLower = locationSearch.toLowerCase();
    return MOCK_COUNTRIES.filter(c => 
      c.name.toLowerCase().includes(searchLower) ||
      c.nameHe.includes(locationSearch) ||
      c.continent.toLowerCase().includes(searchLower)
    );
  }, [locationSearch]);

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

  // Handle search submission - navigate to results page with query params
  const handleSearch = () => {
    const countries = selectedLocations
      .filter(s => s.type === 'country')
      .map(s => s.id as number)
      .join(',');
    
    const continents = selectedLocations
      .filter(s => s.type === 'continent')
      .map(s => s.name)
      .join(',');

    const params = new URLSearchParams();
    if (countries) params.set('countries', countries);
    if (continents) params.set('continents', continents);
    if (selectedType) params.set('type', selectedType.toString());
    if (selectedThemes.length) params.set('themes', selectedThemes.join(','));
    if (selectedYear !== 'all') params.set('year', selectedYear);
    if (selectedMonth !== 'all') params.set('month', selectedMonth);
    params.set('minDuration', minDuration.toString());
    params.set('maxDuration', maxDuration.toString());
    params.set('budget', maxBudget.toString());
    params.set('difficulty', difficulty.toString());

    router.push(`/search/results?${params.toString()}`);
  };

  // Clear all filters - reset to defaults
  const handleClearSearch = () => {
    if (!hasActiveFilters) return; // Don't do anything if already at defaults
    
    setSelectedLocations([]);
    setSelectedType(null);
    setSelectedThemes([]);
    setSelectedYear('all');
    setSelectedMonth('all');
    setMinDuration(5);
    setMaxDuration(30);
    setMaxBudget(15000);
    setDifficulty(2);
    setLocationSearch('');
  };
  
  // Handle duration changes - allow typing without forcing, clamp on blur
  const handleMinDurationChange = (value: number) => {
    setMinDuration(value); // Allow any input temporarily
  };
  
  const handleMaxDurationChange = (value: number) => {
    setMaxDuration(value); // Allow any input temporarily
  };
  
  const handleMinDurationBlur = () => {
    // Clamp to valid range on blur
    let clamped = Math.max(5, Math.min(minDuration, 30));
    
    // Ensure min doesn't exceed max
    if (clamped > maxDuration) {
      setMaxDuration(clamped);
    }
    
    setMinDuration(clamped);
  };
  
  const handleMaxDurationBlur = () => {
    // Clamp to valid range on blur
    let clamped = Math.min(30, Math.max(maxDuration, 5));
    
    // Ensure max isn't less than min
    if (clamped < minDuration) {
      clamped = minDuration;
    }
    
    setMaxDuration(clamped);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-[#076839] text-white py-6 shadow-lg">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between">
            <button
              onClick={handleClearSearch}
              disabled={!hasActiveFilters}
              className={clsx(
                'px-4 py-2 rounded-lg font-medium transition-all text-sm border',
                hasActiveFilters
                  ? 'bg-white text-[#0a192f] border-white hover:bg-gray-50 cursor-pointer shadow-md'
                  : 'bg-gray-300 text-gray-400 border-gray-300 cursor-not-allowed'
              )}
            >
              ניקוי חיפוש
            </button>
            
            <div className="flex-1 text-center">
              <h1 className="text-3xl font-bold text-white">
                מצא את הטיול המושלם עבורך
              </h1>
              <p className="text-gray-100 mt-2">
                מערכת המלצות חכמה לטיולים מאורגנים
              </p>
            </div>
            
            {/* Company Logo */}
            <div className="w-32 flex items-center justify-end">
              <img 
                src="/images/logo/smartrip.png" 
                alt="SmartTrip Logo" 
                className="h-16 w-auto object-contain"
              />
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* ============================================ */}
        {/* LOCATION SEARCH */}
        {/* ============================================ */}
        <section className="bg-white rounded-xl shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-[#5a5a5a]">
            <MapPin className="text-[#12acbe]" />
            לאן תרצה לנסוע?
          </h2>

          {/* Search Input */}
          <div className="relative">
            <input
              type="text"
              value={locationSearch}
              onChange={(e) => setLocationSearch(e.target.value)}
              onFocus={() => setIsLocationDropdownOpen(true)}
              placeholder="חפש יעד או יבשת..."
              className="w-full px-4 py-3 pr-12 pl-12 border-2 border-gray-200 rounded-lg focus:border-[#12acbe] focus:outline-none text-right"
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
          </div>

          {/* Dropdown */}
          {isLocationDropdownOpen && (
            <div className="absolute z-10 w-full max-w-2xl mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl max-h-96 overflow-y-auto">
              {/* Show matching continents first if searching */}
              {locationSearch && filteredContinents.length > 0 && (
                <div className="border-b">
                  <div className="px-4 py-2 bg-gray-100 text-xs font-bold text-gray-600">יבשות</div>
                  {filteredContinents.map(continent => (
                    <button
                      key={continent.value}
                      onClick={() => addLocation('continent', continent.value, continent.value, continent.nameHe)}
                      className="w-full px-4 py-3 text-right hover:bg-[#12acbe]/10 text-[#076839] font-bold transition-colors"
                    >
                      {continent.nameHe}
                    </button>
                  ))}
                </div>
              )}
              
              {/* Countries grouped by continent */}
              {Object.entries(countriesByContinent).map(([continent, countries]) => {
                const continentInfo = CONTINENTS.find(c => c.value === continent);
                
                return (
                  <div key={continent} className="border-b last:border-b-0">
                    {/* Continent Header */}
                    <button
                      onClick={() => addLocation('continent', continent, continent, continentInfo?.nameHe || continent)}
                      className="w-full px-4 py-3 bg-gray-50 hover:bg-[#12acbe]/10 text-right font-bold text-[#076839] flex items-center justify-end gap-2"
                    >
                      <span>{continentInfo?.nameHe || continent}</span>
                      <ChevronDown className="w-4 h-4" />
                    </button>
                    
                    {/* Countries */}
                    <div className="bg-white">
                      {countries.map(country => (
                        <button
                          key={country.id}
                          onClick={() => addLocation('country', country.id, country.name, country.nameHe)}
                          className="w-full px-6 py-2 text-right hover:bg-gray-50 text-[#5a5a5a] hover:text-[#12acbe] transition-colors"
                        >
                          {country.nameHe}
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Selected Locations (Circle Badges) */}
          {selectedLocations.length > 0 && (
            <div className="mt-6">
              <p className="text-sm text-gray-600 mb-3">יעדים נבחרים:</p>
              <div className="flex flex-wrap gap-4">
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
        <section className="bg-white rounded-xl shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-[#5a5a5a]">
            <Compass className="text-[#12acbe]" />
            סגנון הטיול
          </h2>
          <p className="text-sm text-gray-600 mb-4">בחר סגנון טיול אחד</p>

          <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
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
          
          <div className="mt-6">
            <a
              href="https://wa.me/972500000000?text=שלום, אני מעוניין בטיול בוטיק בתפירה אישית"
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full text-center py-3 px-6 border-2 border-[#12acbe] text-[#12acbe] hover:bg-[#12acbe] hover:text-white rounded-xl font-medium transition-all"
            >
              אני רוצה לצאת לטיול בוטיק בתפירה אישית במקום
            </a>
          </div>
        </section>

        {/* ============================================ */}
        {/* TRIP THEMES */}
        {/* ============================================ */}
        <section className="bg-white rounded-xl shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-[#5a5a5a]">
            <Sparkles className="text-[#12acbe]" />
            תחומי עניין
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            בחר עד 3 תחומי עניין ({selectedThemes.length}/3)
          </p>

          <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
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
        <section className="bg-white rounded-xl shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-[#5a5a5a]">
            <Calendar className="text-[#12acbe]" />
            מתי תרצה לנסוע?
          </h2>

          <div className="grid grid-cols-2 gap-4">
            {/* Year */}
            <div>
              <label className="block text-sm font-medium mb-2">שנה</label>
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-[#ff9402] focus:outline-none text-right"
              >
                <option value="all">כל השנים</option>
                <option value="2025">2025</option>
                <option value="2026">2026</option>
                <option value="2027">2027</option>
              </select>
            </div>

            {/* Month */}
            <div>
              <label className="block text-sm font-medium mb-2">חודש</label>
              <select
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-[#12acbe] focus:outline-none text-right"
              >
                <option value="all">כל השנה</option>
                {MONTHS_HE.map((month, index) => (
                  <option key={index} value={String(index + 1)}>
                    {month}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </section>

        {/* ============================================ */}
        {/* SLIDERS & RANGES */}
        {/* ============================================ */}
        <section className="bg-white rounded-xl shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2 text-[#5a5a5a]">
            <TrendingUp className="text-[#12acbe]" />
            העדפות נוספות
          </h2>

          {/* Duration */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-3">
              משך הטיול: {minDuration}-{maxDuration} ימים (5-30)
            </label>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-gray-600 mb-1">מינימום (5 ימים)</label>
                <input
                  type="number"
                  value={minDuration}
                  onChange={(e) => handleMinDurationChange(Number(e.target.value))}
                  onBlur={handleMinDurationBlur}
                  className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:border-[#12acbe] focus:outline-none text-center"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">מקסימום (30 ימים)</label>
                <input
                  type="number"
                  value={maxDuration}
                  onChange={(e) => handleMaxDurationChange(Number(e.target.value))}
                  onBlur={handleMaxDurationBlur}
                  className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:border-[#12acbe] focus:outline-none text-center"
                />
              </div>
            </div>
          </div>

          {/* Budget */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-3 flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-[#12acbe]" />
              תקציב מקסימלי: 
              <span className="text-[#076839] font-bold">
                ${maxBudget.toLocaleString()}
              </span>
            </label>
            <input
              type="range"
              min="2000"
              max="15000"
              step="500"
              value={maxBudget}
              onChange={(e) => setMaxBudget(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#076839]"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>$2,000</span>
              <span>$15,000+</span>
            </div>
          </div>

          {/* Difficulty */}
          <div>
            <label className="block text-sm font-medium mb-3">רמת קושי</label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 1, label: 'קל', labelEn: 'Easy' },
                { value: 2, label: 'בינוני', labelEn: 'Moderate' },
                { value: 3, label: 'מאתגר', labelEn: 'Hard' }
              ].map(({ value, label, labelEn }) => (
                <button
                  key={value}
                  onClick={() => setDifficulty(value)}
                  className={clsx(
                    'py-3 px-4 rounded-lg font-medium transition-all',
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
        <div className="flex gap-4">
          <button
            onClick={handleSearch}
            className="flex-1 bg-[#076839] text-white py-4 px-8 rounded-xl font-bold text-xl hover:bg-[#0ba55c] transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
          >
            <Search className="w-6 h-6" />
            מצא את הטיול שלי
          </button>
          
          <button
            onClick={handleClearSearch}
            disabled={!hasActiveFilters}
            className={clsx(
              'px-8 py-4 rounded-xl font-medium transition-all border',
              hasActiveFilters
                ? 'bg-white text-[#0a192f] border-white hover:bg-gray-50 cursor-pointer shadow-md'
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

