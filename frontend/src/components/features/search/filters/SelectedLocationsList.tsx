/**
 * Selected locations list - Displays currently selected countries/continents as removable badges.
 */
'use client';

import { SelectionBadge } from '@/components/ui/SelectionBadge';
import type { LocationSelection } from '@/schemas/search';

interface SelectedLocationsListProps {
  locations: LocationSelection[];
  onRemove: (index: number) => void;
}

export function SelectedLocationsList({ locations, onRemove }: SelectedLocationsListProps) {
  if (locations.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 md:mt-6" dir="rtl">
      <p className="text-sm text-gray-600 mb-3">יעדים נבחרים:</p>
      <div className="flex flex-wrap gap-3 md:gap-4 max-h-48 overflow-y-auto py-2">
        {locations.map((selection, index) => (
          <SelectionBadge
            key={`${selection.type}-${selection.id}`}
            selection={selection}
            onRemove={() => onRemove(index)}
          />
        ))}
      </div>
    </div>
  );
}
