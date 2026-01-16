'use client';

import { Compass } from 'lucide-react';
import { useSearch } from '@/hooks/useSearch';
import { useTripTypes } from '@/lib/dataStore';
import { TRIP_TYPE_ICONS } from '@/lib/dataStore';
import { TagCircle } from '@/components/ui/TagCircle';

interface SearchTag {
  id: number;
  name: string;
  nameHe: string;
  category: 'Type' | 'Theme';
}

export function TripTypeFilterSection() {
  const search = useSearch();
  const { tripTypes: tripTypesData, isLoading: isLoadingTripTypes } = useTripTypes();

  // Map DataStore types to SearchTag format for compatibility
  const tripTypes: SearchTag[] = tripTypesData.map(t => ({
    id: t.id,
    name: t.name,
    nameHe: t.nameHe || t.name,
    category: 'Type' as const
  }));

  return (
    <section className="bg-white rounded-xl shadow-md p-4 md:p-6 mb-4 md:mb-6">
      <h2 className="text-xl md:text-2xl font-bold mb-3 md:mb-4 flex items-center gap-2 text-[#5a5a5a]">
        <Compass className="text-[#12acbe]" />
        סגנון הטיול
      </h2>
      <p className="text-sm text-gray-600 mb-3 md:mb-4 text-right">בחר סגנון טיול אחד</p>

      <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2 md:gap-4">
        {tripTypes.length > 0 ? tripTypes.map(tag => {
          const Icon = TRIP_TYPE_ICONS[tag.name] || Compass;
          return (
            <TagCircle
              key={tag.id}
              label={tag.nameHe}
              isSelected={search.filters.selectedType === tag.id}
              onClick={() => search.setTripType(tag.id)}
              icon={Icon}
            />
          );
        }) : (
          <div className="col-span-full text-center text-gray-500 py-4 text-sm">
            {isLoadingTripTypes ? 'טוען סגנונות טיול...' : 'לא ניתן לטעון סגנונות טיול'}
          </div>
        )}
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
  );
}
