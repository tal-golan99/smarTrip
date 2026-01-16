'use client';

import { Search, ChevronDown, Loader2 } from 'lucide-react';
import { CONTINENTS, type Country } from '@/lib/dataStore';

interface LocationDropdownProps {
  locationSearch: string;
  isOpen: boolean;
  filteredContinents: { value: string; nameHe: string }[];
  countriesByContinent: Record<string, Country[]>;
  isLoadingCountries: boolean;
  onLocationSelect: (type: 'continent' | 'country', id: string | number, name: string, nameHe: string) => void;
  onToggle: () => void;
}

export function LocationDropdown({
  locationSearch,
  isOpen,
  filteredContinents,
  countriesByContinent,
  isLoadingCountries,
  onLocationSelect,
  onToggle,
}: LocationDropdownProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="absolute z-50 left-0 right-0 mt-2 bg-white border-2 border-gray-200 rounded-lg shadow-xl max-h-[70vh] md:max-h-96 overflow-y-auto overscroll-contain" dir="rtl">
      {/* Show matching continents first if searching */}
      {locationSearch && filteredContinents.length > 0 && (
        <div className="border-b">
          <div className="px-4 py-3 bg-gray-100 text-sm font-bold text-gray-600 text-right sticky top-0">יבשות</div>
          {filteredContinents.map(continent => (
            <button
              key={continent.value}
              onClick={() => onLocationSelect('continent', continent.value, continent.value, continent.nameHe)}
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
                onClick={() => onLocationSelect('continent', continent, continent, continentInfo?.nameHe || continent)}
                className="w-full px-4 py-3 bg-gray-50 hover:bg-[#12acbe]/10 font-bold text-[#076839] flex items-center justify-between"
              >
                <ChevronDown className="w-4 h-4 flex-shrink-0" />
                <span className="flex-1 text-right">{continentInfo?.nameHe || continent}</span>
              </button>
              
              {/* Countries */}
              <div className="bg-white">
                {countriesList
                  .filter(country => country.name !== 'Antarctica' && country.nameHe !== 'אנטארקטיקה')
                  .map(country => (
                    <button
                      key={country.id}
                      onClick={() => onLocationSelect('country', country.id, country.name, country.nameHe || country.name)}
                      className="w-full px-6 py-3 md:py-2 text-right hover:bg-gray-50 active:bg-gray-100 text-[#5a5a5a] hover:text-[#12acbe] transition-colors touch-manipulation"
                    >
                      {country.nameHe || country.name}
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
  );
}
