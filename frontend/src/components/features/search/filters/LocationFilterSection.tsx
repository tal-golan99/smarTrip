'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import { Search, ChevronDown, MapPin } from 'lucide-react';
import clsx from 'clsx';
import { useSearch } from '@/hooks/useSearch';
import { useCountries } from '@/lib/dataStore';
import { CONTINENTS } from '@/lib/dataStore';
import type { Country } from '@/lib/dataStore';
import { LocationDropdown } from './LocationDropdown';
import { SelectedLocationsList } from './SelectedLocationsList';

export function LocationFilterSection() {
  const search = useSearch();
  const { countries, isLoading: isLoadingCountries } = useCountries();
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  const [locationSearch, setLocationSearch] = useState('');
  const [isLocationDropdownOpen, setIsLocationDropdownOpen] = useState(false);

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

  // Filter countries by search - exclude Antarctica (only show as continent)
  const filteredCountries = useMemo(() => {
    // Filter out Antarctica from countries (it should only appear as a continent)
    const countriesWithoutAntarctica = countries.filter(c => 
      c.name !== 'Antarctica' && c.nameHe !== 'אנטארקטיקה'
    );
    
    if (!locationSearch) return countriesWithoutAntarctica;
    
    const searchLower = locationSearch.toLowerCase();
    return countriesWithoutAntarctica.filter(c => 
      c.name.toLowerCase().includes(searchLower) ||
      (c.nameHe && c.nameHe.includes(locationSearch)) ||
      c.continent.toLowerCase().includes(searchLower)
    );
  }, [locationSearch, countries]);

  // Filter continents by search
  const filteredContinents = useMemo(() => {
    if (!locationSearch) return [...CONTINENTS];
    
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
  const handleLocationSelect = (type: 'continent' | 'country', id: string | number, name: string, nameHe: string) => {
    search.addLocation({ type, id, name, nameHe });
    setIsLocationDropdownOpen(false);
    setLocationSearch('');
  };

  return (
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

        <LocationDropdown
          locationSearch={locationSearch}
          isOpen={isLocationDropdownOpen}
          filteredContinents={filteredContinents}
          countriesByContinent={countriesByContinent}
          isLoadingCountries={isLoadingCountries}
          onLocationSelect={handleLocationSelect}
          onToggle={() => setIsLocationDropdownOpen(!isLocationDropdownOpen)}
        />
      </div>

      <SelectedLocationsList
        locations={search.filters.selectedLocations}
        onRemove={search.removeLocation}
      />
    </section>
  );
}
