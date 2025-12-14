'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const router = useRouter();

  useEffect(() => {
    console.error('Search error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
        <div className="text-red-500 text-6xl mb-4">⚠️</div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          משהו השתבש
        </h2>
        <p className="text-gray-600 mb-6" dir="rtl">
          אירעה שגיאה בטעינת עמוד החיפוש. נסה לרענן את הדף.
        </p>
        <div className="flex gap-4 justify-center">
          <button
            onClick={() => reset()}
            className="px-6 py-3 bg-[#076839] text-white rounded-lg font-bold hover:bg-[#0ba55c] transition-all"
          >
            נסה שוב
          </button>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg font-bold hover:bg-gray-300 transition-all"
          >
            חזור לדף הבית
          </button>
        </div>
      </div>
    </div>
  );
}

