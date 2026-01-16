'use client';

import { useCallback } from 'react';
import { TrendingUp, DollarSign } from 'lucide-react';
import clsx from 'clsx';
import { useSearch } from '@/hooks/useSearch';
import { DualRangeSlider } from '@/components/ui/DualRangeSlider';

export function RangeFiltersSection() {
  const search = useSearch();

  // Handle duration change - use search hook
  const handleDurationChange = useCallback((newMin: number, newMax: number) => {
    search.setDuration(newMin, newMax);
  }, [search]);

  return (
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
          minValue={search.filters.minDuration}
          maxValue={search.filters.maxDuration}
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
            ${search.filters.maxBudget.toLocaleString()}
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
            value={search.filters.maxBudget}
            onChange={(e) => {
              e.preventDefault();
              e.stopPropagation();
              search.setBudget(Number(e.target.value));
            }}
            onMouseDown={(e) => e.stopPropagation()}
            onTouchStart={(e) => e.stopPropagation()}
            style={{
              background: `linear-gradient(to left, #12acbe 0%, #12acbe ${((search.filters.maxBudget - 2000) / (15000 - 2000)) * 100}%, #e5e7eb ${((search.filters.maxBudget - 2000) / (15000 - 2000)) * 100}%, #e5e7eb 100%)`
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
              onClick={() => search.setDifficulty(value)}
              className={clsx(
                'py-3 px-3 md:px-4 rounded-lg font-medium transition-all text-sm md:text-base',
                'border-2',
                search.filters.difficulty === value
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
  );
}
