/**
 * TagCircle Component
 * Stateless UI component for displaying selectable tags.
 * Takes an icon component prop (not iconMap) for reusability.
 */

'use client';

import { Compass } from 'lucide-react';
import clsx from 'clsx';
import type { LucideIcon } from 'lucide-react';

interface TagCircleProps {
  label: string;
  isSelected: boolean;
  onClick: () => void;
  icon?: LucideIcon | React.ComponentType<{ className?: string }>;
  className?: string;
}

export function TagCircle({ 
  label, 
  isSelected, 
  onClick,
  icon: Icon = Compass,
  className
}: TagCircleProps) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        'flex flex-col items-center gap-2 p-3 md:p-4 rounded-xl transition-all duration-200',
        'border-2 hover:scale-105',
        isSelected 
          ? 'bg-[#076839] border-[#12acbe] text-white' 
          : 'bg-white border-gray-200 text-[#5a5a5a] hover:border-[#12acbe]',
        className
      )}
    >
      <div className={clsx(
        'w-10 h-10 md:w-12 md:h-12 rounded-full flex items-center justify-center',
        isSelected ? 'bg-[#12acbe]' : 'bg-gray-100'
      )}>
        <Icon className="w-5 h-5 md:w-6 md:h-6" />
      </div>
      <span className="text-[10px] md:text-xs font-medium text-center leading-tight">
        {label}
      </span>
    </button>
  );
}
