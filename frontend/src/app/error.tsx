/**
 * Global error boundary - Catches and displays errors from any page component.
 */
'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Application error:', error);
  }, [error]);

  return (
    <html lang="he" dir="rtl">
      <body>
        <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="text-red-500 text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              משהו השתבש
            </h2>
            <p className="text-gray-600 mb-6" dir="rtl">
              אירעה שגיאה באפליקציה. נסה לרענן את הדף.
            </p>
            <button
              onClick={() => reset()}
              className="px-6 py-3 bg-[#076839] text-white rounded-lg font-bold hover:bg-[#0ba55c] transition-all"
            >
              נסה שוב
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}

