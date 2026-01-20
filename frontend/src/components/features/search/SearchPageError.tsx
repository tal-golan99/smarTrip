/**
 * Search page error state - Error message with retry button.
 */
'use client';

import { X } from 'lucide-react';

interface SearchPageErrorProps {
  onRetry: () => void;
}

export function SearchPageError({ onRetry }: SearchPageErrorProps) {
  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="text-center max-w-md p-8">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <X className="w-8 h-8 text-red-600" />
        </div>
        <h2 className="text-xl font-bold text-gray-800 mb-4">
          שגיאת חיבור לשרת
        </h2>
        <div className="text-gray-600 mb-6 space-y-2 text-sm">
          <p>נסה לרענן את הדף בעוד כמה רגעים</p>
        </div>
        <button
          onClick={onRetry}
          className="w-full px-6 py-3 bg-[#076839] hover:bg-[#0ba55c] text-white rounded-xl font-medium transition-all"
        >
          נסה שוב עכשיו
        </button>
      </div>
    </div>
  );
}
