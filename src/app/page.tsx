'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/search');
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a192f]">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#e8c47c] mx-auto mb-4"></div>
        <p className="text-white text-lg">Loading SmarTrip...</p>
      </div>
    </div>
  );
}
