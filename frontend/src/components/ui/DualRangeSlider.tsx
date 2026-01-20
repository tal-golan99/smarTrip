/**
 * Dual range slider - Interactive two-thumb slider for min/max range selection.
 */
'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import clsx from 'clsx';

interface DualRangeSliderProps {
  min: number;
  max: number;
  minValue: number;
  maxValue: number;
  step?: number;
  minGap?: number;
  onChange: (min: number, max: number) => void;
  label: string;
}

export function DualRangeSlider({
  min,
  max,
  minValue,
  maxValue,
  step = 1,
  minGap = 3,
  onChange,
  label
}: DualRangeSliderProps) {
  const minThumbRef = useRef<HTMLDivElement>(null);
  const maxThumbRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const [isDraggingMin, setIsDraggingMin] = useState(false);
  const [isDraggingMax, setIsDraggingMax] = useState(false);

  const getPercentage = useCallback((value: number) => {
    return ((value - min) / (max - min)) * 100;
  }, [min, max]);

  const getValue = useCallback((percentage: number) => {
    const rawValue = (percentage / 100) * (max - min) + min;
    return Math.round(rawValue / step) * step;
  }, [min, max, step]);

  const handleMouseMove = useCallback((e: MouseEvent | TouchEvent) => {
    if (!trackRef.current) {
      return;
    }
    
    if ('touches' in e) {
      e.preventDefault();
    }

    const rect = trackRef.current.getBoundingClientRect();
    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
    const percentage = Math.max(0, Math.min(100, ((rect.right - clientX) / rect.width) * 100));
    const newValue = getValue(percentage);

    if (isDraggingMin) {
      const maxAllowed = maxValue - minGap;
      const clampedValue = Math.min(Math.max(min, newValue), maxAllowed);
      onChange(clampedValue, maxValue);
    } else if (isDraggingMax) {
      const minAllowed = minValue + minGap;
      const clampedValue = Math.max(Math.min(max, newValue), minAllowed);
      onChange(minValue, clampedValue);
    }
  }, [isDraggingMin, isDraggingMax, minValue, maxValue, minGap, min, max, getValue, onChange]);

  const handleMouseUp = useCallback(() => {
    setIsDraggingMin(false);
    setIsDraggingMax(false);
  }, []);

  useEffect(() => {
    if (isDraggingMin || isDraggingMax) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.addEventListener('touchmove', handleMouseMove, { passive: false });
      document.addEventListener('touchend', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('touchmove', handleMouseMove as EventListener);
      document.removeEventListener('touchend', handleMouseUp);
    };
  }, [isDraggingMin, isDraggingMax, handleMouseMove, handleMouseUp]);

  return (
    <div className="w-full">
      <label className="block text-sm font-medium mb-3 text-right">
        {label}: <span className="text-[#076839] font-bold">{minValue}-{maxValue} ימים</span>
      </label>
      
      <div className="relative h-10 flex items-center" dir="rtl">
        <div 
          ref={trackRef}
          className="absolute w-full h-2 bg-gray-200 rounded-full"
        />
        
        <div 
          className="absolute h-2 bg-[#12acbe] rounded-full"
          style={{
            right: `${getPercentage(minValue)}%`,
            width: `${getPercentage(maxValue) - getPercentage(minValue)}%`
          }}
        />
        
        <div
          ref={minThumbRef}
          className={clsx(
            'absolute w-6 h-6 bg-[#12acbe] rounded-full cursor-grab shadow-lg border-2 border-white',
            'flex items-center justify-center transform translate-x-1/2 transition-transform touch-none',
            isDraggingMin && 'cursor-grabbing scale-110'
          )}
          style={{ right: `${getPercentage(minValue)}%` }}
          onMouseDown={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDraggingMin(true);
          }}
          onTouchStart={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDraggingMin(true);
          }}
        >
          <span className="text-white text-[10px] font-bold">{minValue}</span>
        </div>
        
        <div
          ref={maxThumbRef}
          className={clsx(
            'absolute w-6 h-6 bg-[#12acbe] rounded-full cursor-grab shadow-lg border-2 border-white',
            'flex items-center justify-center transform translate-x-1/2 transition-transform touch-none',
            isDraggingMax && 'cursor-grabbing scale-110'
          )}
          style={{ right: `${getPercentage(maxValue)}%` }}
          onMouseDown={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDraggingMax(true);
          }}
          onTouchStart={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDraggingMax(true);
          }}
        >
          <span className="text-white text-[10px] font-bold">{maxValue}</span>
        </div>
      </div>
    </div>
  );
}
