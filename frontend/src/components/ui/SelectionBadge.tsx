/**
 * SelectionBadge Component
 * Stateless UI component for displaying selected locations.
 * Reusable across the application.
 */

'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import clsx from 'clsx';
import { COUNTRY_FLAGS, CONTINENT_IMAGES } from '@/lib/dataStore';
import type { LocationSelection } from '@/contexts/SearchContext';

interface SelectionBadgeProps {
  selection: LocationSelection;
  onRemove: () => void;
}

export function SelectionBadge({ selection, onRemove }: SelectionBadgeProps) {
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
