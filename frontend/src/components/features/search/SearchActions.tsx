/**
 * Search action buttons - Search and clear filters buttons.
 */
'use client';

import { Search } from 'lucide-react';
import { ClearFiltersButton } from '@/components/ui/ClearFiltersButton';

interface SearchActionsProps {
  onSearch: () => void;
  onClear: () => void;
  hasActiveFilters: boolean;
  onClearLocationSearch?: () => void;
}

export function SearchActions({ onSearch, onClear, hasActiveFilters, onClearLocationSearch }: SearchActionsProps) {
  const handleClear = () => {
    onClear();
    if (onClearLocationSearch) {
      onClearLocationSearch();
    }
  };

  return (
    <div className="flex flex-col md:flex-row gap-3 md:gap-4">
      <button
        onClick={onSearch}
        className="flex-1 bg-[#076839] text-white py-4 px-6 md:px-8 rounded-xl font-bold text-lg md:text-xl hover:bg-[#0ba55c] transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
      >
        <Search className="w-5 h-5 md:w-6 md:h-6" />
        מצא את הטיול שלי
      </button>
      
      <ClearFiltersButton
        hasActiveFilters={hasActiveFilters}
        onClick={handleClear}
        className="px-6 md:px-8 py-4 text-base"
      />
    </div>
  );
}
