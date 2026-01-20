/**
 * Utility functions - Trip status labels, icons, and formatting helpers.
 */
import { CheckCircle, AlertCircle, Clock, XCircle } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

// ============================================
// TRIP UTILITIES
// ============================================

export function getStatusLabel(status?: string): string {
  const statusMap: Record<string, string> = {
    'GUARANTEED': 'יציאה מובטחת',
    'LAST_PLACES': 'מקומות אחרונים',
    'OPEN': 'הרשמה פתוחה',
    'FULL': 'מלא',
    'CANCELLED': 'בוטל',
  };
  const statusNormalized = status?.toUpperCase().replace(/\s+/g, '_');
  return statusNormalized ? statusMap[statusNormalized] || 'הרשמה פתוחה' : 'הרשמה פתוחה';
}

export function getDifficultyLabel(level?: number): string {
  if (level === 1) {
    return 'קל';
  }
  if (level === 2) {
    return 'בינוני';
  }
  if (level === 3) {
    return 'מאתגר';
  }
  return 'בינוני';
}

export function getStatusIconUrl(status?: string): string | null {
  const statusNormalized = status?.toUpperCase().replace(/\s+/g, '_');
  if (statusNormalized === 'GUARANTEED') {
    return '/images/trip status/guaranteed.svg';
  }
  if (statusNormalized === 'LAST_PLACES') {
    return '/images/trip status/last places.svg';
  }
  if (statusNormalized === 'OPEN') {
    return '/images/trip status/open.svg';
  }
  if (statusNormalized === 'FULL') {
    return '/images/trip status/full.png';
  }
  return null;
}

export function getStatusIcon(status?: string): LucideIcon {
  const statusNormalized = status?.toUpperCase().replace(/\s+/g, '_');
  if (statusNormalized === 'GUARANTEED') {
    return CheckCircle;
  }
  if (statusNormalized === 'LAST_PLACES') {
    return AlertCircle;
  }
  if (statusNormalized === 'OPEN') {
    return Clock;
  }
  if (statusNormalized === 'FULL') {
    return XCircle;
  }
  return Clock;
}

// ============================================
// DATE UTILITIES
// ============================================

export function formatDate(dateString?: string): string {
  if (!dateString) {
    return '';
  }
  return new Date(dateString).toLocaleDateString('en-GB').replace(/\//g, '.');
}

export function calculateDuration(startDate?: string, endDate?: string): number {
  if (!startDate || !endDate) {
    return 0;
  }
  const start = new Date(startDate);
  const end = new Date(endDate);
  const diffTime = Math.abs(end.getTime() - start.getTime());
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

const MONTHS_HE = [
  'ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני',
  'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר'
];

export function getAvailableMonths(selectedYear: string): { index: number; name: string }[] {
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth();

  if (selectedYear === 'all' || parseInt(selectedYear) > currentYear) {
    return MONTHS_HE.map((name, index) => ({ index: index + 1, name }));
  }

  if (parseInt(selectedYear) === currentYear) {
    return MONTHS_HE
      .map((name, index) => ({ index: index + 1, name }))
      .filter(m => m.index > currentMonth);
  }

  return [];
}

export function getAvailableYears(): string[] {
  const currentYear = new Date().getFullYear();
  return [currentYear.toString(), (currentYear + 1).toString()];
}

// ============================================
// SCORE UTILITIES
// ============================================

export interface ScoreThresholds {
  HIGH: number;
  MID: number;
}

export function getScoreColor(score: number, thresholds: ScoreThresholds): 'high' | 'mid' | 'low' {
  if (score >= thresholds.HIGH) {
    return 'high';
  }
  if (score >= thresholds.MID) {
    return 'mid';
  }
  return 'low';
}

export function getScoreBgClass(colorLevel: 'high' | 'mid' | 'low'): string {
  if (colorLevel === 'high') {
    return 'bg-[#12acbe]';
  }
  if (colorLevel === 'mid') {
    return 'bg-[#f59e0b]';
  }
  return 'bg-[#ef4444]';
}
