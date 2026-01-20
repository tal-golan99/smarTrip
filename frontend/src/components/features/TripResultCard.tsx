/**
 * Trip result card component - Displays trip info with tracking for impressions and clicks.
 */
'use client';

import { useImpressionTracking, ClickSource } from '@/hooks/useTracking';

interface TripResultCardProps {
  tripId: number | undefined;
  position: number;
  score: number;
  source: ClickSource;
  onClick: () => void;
  className?: string;
  children: React.ReactNode;
}

/**
 * Trip result card wrapper with impression tracking.
 * Fires impression event when card is 50% visible.
 */
export function TripResultCard({
  tripId,
  position,
  score,
  source,
  onClick,
  className,
  children,
}: TripResultCardProps) {
  const impressionRef = useImpressionTracking(tripId, position, score, source);
  
  return (
    <div
      ref={impressionRef}
      onClick={onClick}
      className={className}
    >
      {children}
    </div>
  );
}
