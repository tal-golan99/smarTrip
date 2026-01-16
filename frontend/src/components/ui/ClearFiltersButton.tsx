/**
 * ClearFiltersButton Component
 * Stateless UI component for clearing search filters.
 */

'use client';

import clsx from 'clsx';

interface ClearFiltersButtonProps {
  hasActiveFilters: boolean;
  onClick: () => void;
  className?: string;
}

export function ClearFiltersButton({ 
  hasActiveFilters, 
  onClick,
  className 
}: ClearFiltersButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={!hasActiveFilters}
      className={clsx(
        'px-6 py-3 rounded-lg font-medium transition-all text-sm border',
        hasActiveFilters
          ? 'bg-white text-[#0a192f] border-gray-300 hover:bg-gray-50 cursor-pointer shadow-md'
          : 'bg-gray-200 text-gray-400 border-gray-300 cursor-not-allowed',
        className
      )}
    >
      ניקוי חיפוש
    </button>
  );
}
