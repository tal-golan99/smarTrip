/**
 * Search page header - Logo, navigation, and user authentication controls.
 */
'use client';

import { Home, LogOut } from 'lucide-react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { isAuthAvailable } from '@/lib/supabaseClient';

interface SearchPageHeaderProps {
  userName: string | null;
  isLoadingUser: boolean;
  onLogout: () => void;
}

export function SearchPageHeader({ userName, isLoadingUser, onLogout }: SearchPageHeaderProps) {
  const router = useRouter();

  return (
    <header className="bg-[#076839] text-white py-4 md:py-6 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between gap-4">
          {/* Return to Home Button and Logout */}
          <div className="w-16 md:w-32 flex items-center justify-start gap-2">
            <button
              onClick={() => router.push('/')}
              className="flex items-center gap-2 px-3 py-2 md:px-4 md:py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all duration-200 group"
              title="חזרה לדף הבית"
            >
              <Home className="w-5 h-5 md:w-6 md:h-6 group-hover:scale-110 transition-transform" />
            </button>
            {isAuthAvailable() && userName && (
              <button
                onClick={onLogout}
                className="flex items-center gap-2 px-3 py-2 md:px-4 md:py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all duration-200 group"
                title="התנתק"
                type="button"
              >
                <LogOut className="w-5 h-5 md:w-6 md:h-6 group-hover:scale-110 transition-transform" />
              </button>
            )}
          </div>
          
          {/* Title - Centered */}
          <div className="flex-1 text-center">
            <h1 className="text-2xl md:text-3xl font-bold text-white">
              מצא את הטיול המושלם עבורך
            </h1>
            <p className="text-gray-100 mt-1 md:mt-2 text-sm md:text-base">
              {isLoadingUser ? (
                'טוען...'
              ) : userName ? (
                <span className="font-medium">שלום {userName}!</span>
              ) : null}
            </p>
          </div>
          
          {/* Company Logo */}
          <div className="w-16 md:w-32 flex items-center justify-end">
            <Image 
              src="/images/logo/smartrip.png" 
              alt="SmartTrip Logo" 
              width={128}
              height={64}
              className="h-10 md:h-16 w-auto object-contain"
            />
          </div>
        </div>
      </div>
    </header>
  );
}
