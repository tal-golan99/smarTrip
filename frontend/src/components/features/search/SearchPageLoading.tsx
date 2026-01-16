'use client';

import { Loader2 } from 'lucide-react';
import Image from 'next/image';

export function SearchPageLoading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#076839] via-[#0ba55c] to-[#12acbe] flex items-center justify-center p-4">
      <div className="text-center">
        <div className="mb-6">
          <Image 
            src="/images/logo/smartrip.png" 
            alt="SmartTrip Logo" 
            width={180} 
            height={180} 
            className="mx-auto h-auto"
            style={{ width: 'auto' }}
            priority
          />
        </div>
        <Loader2 className="w-12 h-12 animate-spin text-white mx-auto mb-4" />
        <p className="text-white text-xl font-medium mb-2">טוען...</p>
        <p className="text-white/80 text-sm">טעינה ראשונית עשויה לקחת מספר רגעים</p>
      </div>
    </div>
  );
}
