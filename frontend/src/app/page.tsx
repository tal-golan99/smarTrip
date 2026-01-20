/**
 * Home page - Landing page with hero section, features, and trip categories.
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { Sparkles, Star, Users, Globe, CheckCircle, MapPin, Sliders, Ship, Train, Camera, Mountain, PawPrint, Users2, Drama, LogOut } from 'lucide-react';
import { supabase, isAuthAvailable } from '@/lib/supabaseClient';
import { useUser } from '@/hooks/useUser';
import { LogoutConfirmModal } from '@/components/features/LogoutConfirmModal';

export default function Home() {
  const router = useRouter();
  const { userName, isLoading: isLoadingUser } = useUser();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  // Show logout confirmation dialog
  const handleLogout = () => {
    setShowLogoutConfirm(true);
  };

  // Confirm logout
  const confirmLogout = async () => {
    if (!isAuthAvailable() || !supabase) {
      return;
    }
    
    try {
      await supabase.auth.signOut();
      setShowLogoutConfirm(false);
      router.push('/auth?redirect=/search');
    } catch (error) {
      console.error('[Home] Error logging out:', error);
      setShowLogoutConfirm(false);
    }
  };

  // Cancel logout
  const cancelLogout = () => {
    setShowLogoutConfirm(false);
  };

  const handleStartJourney = async (e: React.MouseEvent<HTMLButtonElement | HTMLAnchorElement>) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('[Home] Button clicked, navigating...');
    
    // If user is already logged in, go directly to search
    if (isAuthAvailable() && supabase) {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session) {
          router.push('/search');
          return;
        }
      } catch (error) {
        console.error('[Home] Error checking session:', error);
      }
    }
    
    // Otherwise, go to auth page
    window.location.href = '/auth?redirect=/search';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#076839] via-[#0ba55c] to-[#12acbe] flex items-center justify-center px-4 py-8 md:p-4 relative overflow-hidden">
      {/* Logout Confirmation Dialog */}
      <LogoutConfirmModal
        isOpen={showLogoutConfirm}
        onConfirm={confirmLogout}
        onCancel={cancelLogout}
      />

      {/* Logout Button - Top Right */}
      {isAuthAvailable() && userName && (
        <button
          onClick={handleLogout}
          className="absolute top-4 right-4 flex items-center gap-2 px-3 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all duration-200 group z-40"
          title="התנתק"
          type="button"
        >
          <LogOut className="w-5 h-5 group-hover:scale-110 transition-transform" />
        </button>
      )}

      {/* Decorative background elements - Optimized */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-white/5 rounded-full blur-2xl transform-gpu"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-white/5 rounded-full blur-2xl transform-gpu"></div>
        <Sparkles className="absolute bottom-1/3 left-1/4 w-6 h-6 text-white/10 animate-pulse transform-gpu" style={{ animationDelay: '1s' }} />
      </div>

      {/* Main content */}
      <div className="text-center z-10 max-w-4xl mx-auto w-full relative">
        {/* Logo */}
        <div className="mb-4 md:mb-8 animate-fade-in">
          <Image 
            src="/images/logo/smartrip.png" 
            alt="SmartTrip Logo" 
            width={200} 
            height={200} 
            className="mx-auto drop-shadow-2xl w-[100px] md:w-[200px] h-auto"
            priority
          />
        </div>

        {/* Title */}
        <h1 className="text-5xl sm:text-6xl md:text-6xl lg:text-7xl font-bold text-white mb-4 md:mb-6 animate-fade-in-up px-2" style={{ animationDelay: '0.2s' }}>
          SmarTrip
        </h1>

        {/* Subtitle */}
        <h2 className="text-lg sm:text-xl md:text-2xl lg:text-3xl font-medium text-white/95 mb-6 md:mb-8 max-w-3xl mx-auto leading-relaxed animate-fade-in-up px-4" style={{ animationDelay: '0.4s' }}>
          במקום לבזבז שעות על חיפושים, תן לנו להתאים לך חוויה בלתי נשכחת שתפורה בדיוק למידות, לרצונות ולתקציב שלך
        </h2>

        {/* Call to Action Button */}
        <div className="animate-fade-in-up px-4 relative z-20" style={{ animationDelay: '0.6s' }}>
          <Link
            href="/auth?redirect=/search"
            onClick={handleStartJourney}
            className="relative inline-flex items-center justify-center px-8 py-4 md:px-12 md:py-5 bg-white text-[#076839] rounded-2xl font-bold text-lg md:text-xl lg:text-2xl shadow-2xl hover:shadow-[0_20px_60px_rgba(255,255,255,0.5)] transition-all duration-300 hover:scale-105 active:scale-95 w-full max-w-md transform-gpu cursor-pointer no-underline"
            style={{ position: 'relative', zIndex: 30, pointerEvents: 'auto', display: 'inline-flex' }}
          >
            בוא נגלה לאן טסים
          </Link>
        </div>

        {/* Social Proof / Trust Indicators */}
        <div className="mt-8 md:mt-12 flex flex-row items-center justify-center gap-4 sm:gap-6 md:gap-8 text-white animate-fade-in-up px-2" style={{ animationDelay: '0.8s' }}>
          <div className="text-center flex-1">
            <div className="text-xl sm:text-2xl md:text-4xl font-bold mb-1">500+</div>
            <div className="text-white/80 text-[10px] sm:text-xs md:text-sm leading-tight">טיולים מאורגנים</div>
          </div>
          <div className="w-px h-10 md:h-12 bg-white/20"></div>
          <div className="text-center flex-1">
            <div className="text-xl sm:text-2xl md:text-4xl font-bold mb-1">10,000+</div>
            <div className="text-white/80 text-[10px] sm:text-xs md:text-sm leading-tight">מטיילים מרוצים</div>
          </div>
          <div className="w-px h-10 md:h-12 bg-white/20"></div>
          <div className="text-center flex-1">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Star className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 fill-yellow-300 text-yellow-300" />
              <span className="text-xl sm:text-2xl md:text-4xl font-bold">4.9</span>
            </div>
            <div className="text-white/80 text-[10px] sm:text-xs md:text-sm leading-tight">דירוג ממוצע</div>
          </div>
        </div>

        {/* How It Works Section */}
        <div className="mt-12 md:mt-20 max-w-4xl mx-auto animate-fade-in-up px-4" style={{ animationDelay: '1s' }}>
          <h3 className="text-xl sm:text-2xl md:text-3xl font-bold text-white mb-8 md:mb-12 text-center">איך זה עובד?</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
            {/* Step 1 */}
            <div className="text-center">
              <div className="w-14 h-14 md:w-16 md:h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-3 md:mb-4 backdrop-blur-sm">
                <Sliders className="w-7 h-7 md:w-8 md:h-8 text-white" />
              </div>
              <div className="text-lg md:text-xl font-bold text-white mb-2">שלב 1: מה הסגנון שלך?</div>
              <p className="text-white/80 text-sm leading-relaxed">ספר לנו מה התקציב, תאריכים רצויים ומה מעניין אותך.</p>
            </div>
            
            {/* Step 2 */}
            <div className="text-center">
              <div className="w-14 h-14 md:w-16 md:h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-3 md:mb-4 backdrop-blur-sm">
                <Sparkles className="w-7 h-7 md:w-8 md:h-8 text-white" />
              </div>
              <div className="text-lg md:text-xl font-bold text-white mb-2">שלב 2: הקסם קורה</div>
              <p className="text-white/80 text-sm leading-relaxed">המערכת שלנו סורקת ובונָה עבורך את האפשרויות המדויקות ביותר.</p>
            </div>
            
            {/* Step 3 */}
            <div className="text-center">
              <div className="w-14 h-14 md:w-16 md:h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-3 md:mb-4 backdrop-blur-sm">
                <CheckCircle className="w-7 h-7 md:w-8 md:h-8 text-white" />
              </div>
              <div className="text-lg md:text-xl font-bold text-white mb-2">שלב 3: אורזים וטסים</div>
              <p className="text-white/80 text-sm leading-relaxed">בוחרים את ההצעה המנצחת ומתחילים את החוויה.</p>
            </div>
          </div>
        </div>

        {/* Why Choose SmarTrip */}
        <div className="mt-12 md:mt-20 max-w-3xl mx-auto text-center animate-fade-in-up px-4" style={{ animationDelay: '1.2s' }}>
          <h3 className="text-xl sm:text-2xl md:text-3xl font-bold text-white mb-4 md:mb-6">למה לבחור ב-SmarTrip?</h3>
          <p className="text-white/90 text-base md:text-lg leading-relaxed">
            במקום לעבור על מאות אתרים ולהשוות ידנית, המערכת שלנו משתמשת באלגוריתמים מתקדמים כדי למצוא בדיוק את מה שמתאים לך. 
            חוסכים זמן, כסף ומאמץ - ומקבלים את הטיול המושלם.
          </p>
        </div>

        {/* Types of Trips Available */}
        <div className="mt-12 md:mt-16 max-w-5xl mx-auto animate-fade-in-up px-4" style={{ animationDelay: '1.4s' }}>
          <h3 className="text-lg sm:text-xl md:text-2xl font-bold text-white mb-6 md:mb-8 text-center">מצא את סגנון הטיול שלך</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
            {/* Safari */}
            <div className="group relative overflow-hidden rounded-xl md:rounded-2xl bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-sm active:from-white/30 active:to-white/10 md:hover:from-white/30 md:hover:to-white/10 transition-all duration-300 md:hover:scale-105 active:scale-95 cursor-pointer flex flex-col justify-center items-center gap-2 md:gap-3 p-4 md:p-6 min-h-[100px] md:min-h-[120px] transform-gpu">
              <PawPrint className="w-7 h-7 md:w-8 md:h-8 flex-shrink-0 text-white md:group-hover:scale-110 transition-transform transform-gpu" />
              <div className="text-white font-medium text-xs md:text-sm text-center leading-tight">ספארי באפריקה</div>
            </div>
            
            {/* Geographic Depth */}
            <div className="group relative overflow-hidden rounded-xl md:rounded-2xl bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-sm active:from-white/30 active:to-white/10 md:hover:from-white/30 md:hover:to-white/10 transition-all duration-300 md:hover:scale-105 active:scale-95 cursor-pointer flex flex-col justify-center items-center gap-2 md:gap-3 p-4 md:p-6 min-h-[100px] md:min-h-[120px] transform-gpu">
              <Globe className="w-7 h-7 md:w-8 md:h-8 flex-shrink-0 text-white md:group-hover:scale-110 transition-transform transform-gpu" />
              <div className="text-white font-medium text-xs md:text-sm text-center leading-tight">טיולי עומק</div>
            </div>
            
            {/* Cruises */}
            <div className="group relative overflow-hidden rounded-xl md:rounded-2xl bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-sm active:from-white/30 active:to-white/10 md:hover:from-white/30 md:hover:to-white/10 transition-all duration-300 md:hover:scale-105 active:scale-95 cursor-pointer flex flex-col justify-center items-center gap-2 md:gap-3 p-4 md:p-6 min-h-[100px] md:min-h-[120px] transform-gpu">
              <Ship className="w-7 h-7 md:w-8 md:h-8 flex-shrink-0 text-white md:group-hover:scale-110 transition-transform transform-gpu" />
              <div className="text-white font-medium text-xs md:text-sm text-center leading-tight">שייט גיאוגרפי</div>
            </div>
            
            {/* Train Tours */}
            <div className="group relative overflow-hidden rounded-xl md:rounded-2xl bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-sm active:from-white/30 active:to-white/10 md:hover:from-white/30 md:hover:to-white/10 transition-all duration-300 md:hover:scale-105 active:scale-95 cursor-pointer flex flex-col justify-center items-center gap-2 md:gap-3 p-4 md:p-6 min-h-[100px] md:min-h-[120px] transform-gpu">
              <Train className="w-7 h-7 md:w-8 md:h-8 flex-shrink-0 text-white md:group-hover:scale-110 transition-transform transform-gpu" />
              <div className="text-white font-medium text-xs md:text-sm text-center leading-tight">טיולי רכבות</div>
            </div>
            
            {/* Carnivals */}
            <div className="group relative overflow-hidden rounded-xl md:rounded-2xl bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-sm active:from-white/30 active:to-white/10 md:hover:from-white/30 md:hover:to-white/10 transition-all duration-300 md:hover:scale-105 active:scale-95 cursor-pointer flex flex-col justify-center items-center gap-2 md:gap-3 p-4 md:p-6 min-h-[100px] md:min-h-[120px] transform-gpu">
              <Drama className="w-7 h-7 md:w-8 md:h-8 flex-shrink-0 text-white md:group-hover:scale-110 transition-transform transform-gpu" />
              <div className="text-white font-medium text-xs md:text-sm text-center leading-tight">קרנבלים ופסטיבלים</div>
            </div>
            
            {/* Photography */}
            <div className="group relative overflow-hidden rounded-xl md:rounded-2xl bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-sm active:from-white/30 active:to-white/10 md:hover:from-white/30 md:hover:to-white/10 transition-all duration-300 md:hover:scale-105 active:scale-95 cursor-pointer flex flex-col justify-center items-center gap-2 md:gap-3 p-4 md:p-6 min-h-[100px] md:min-h-[120px] transform-gpu">
              <Camera className="w-7 h-7 md:w-8 md:h-8 flex-shrink-0 text-white md:group-hover:scale-110 transition-transform transform-gpu" />
              <div className="text-white font-medium text-xs md:text-sm text-center leading-tight">טיולי צילום</div>
            </div>
            
            {/* Nature Hiking */}
            <div className="group relative overflow-hidden rounded-xl md:rounded-2xl bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-sm active:from-white/30 active:to-white/10 md:hover:from-white/30 md:hover:to-white/10 transition-all duration-300 md:hover:scale-105 active:scale-95 cursor-pointer flex flex-col justify-center items-center gap-2 md:gap-3 p-4 md:p-6 min-h-[100px] md:min-h-[120px] transform-gpu">
              <Mountain className="w-7 h-7 md:w-8 md:h-8 flex-shrink-0 text-white md:group-hover:scale-110 transition-transform transform-gpu" />
              <div className="text-white font-medium text-xs md:text-sm text-center leading-tight">הליכות בטבע</div>
            </div>
            
            {/* Private Groups */}
            <div className="group relative overflow-hidden rounded-xl md:rounded-2xl bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-sm active:from-white/30 active:to-white/10 md:hover:from-white/30 md:hover:to-white/10 transition-all duration-300 md:hover:scale-105 active:scale-95 cursor-pointer flex flex-col justify-center items-center gap-2 md:gap-3 p-4 md:p-6 min-h-[100px] md:min-h-[120px] transform-gpu">
              <Users2 className="w-7 h-7 md:w-8 md:h-8 flex-shrink-0 text-white md:group-hover:scale-110 transition-transform transform-gpu" />
              <div className="text-white font-medium text-xs md:text-sm text-center leading-tight">קבוצות פרטיות</div>
            </div>
          </div>
        </div>

        {/* Second CTA - Bottom of Page */}
        <div className="mt-12 md:mt-20 text-center animate-fade-in-up px-4 relative z-20" style={{ animationDelay: '1.6s' }}>
          <Link
            href="/auth?redirect=/search"
            onClick={handleStartJourney}
            className="relative inline-flex items-center justify-center px-8 py-4 md:px-12 md:py-5 bg-white text-[#076839] rounded-2xl font-bold text-lg md:text-xl lg:text-2xl shadow-2xl hover:shadow-[0_20px_60px_rgba(255,255,255,0.5)] transition-all duration-300 hover:scale-105 active:scale-95 w-full max-w-md transform-gpu cursor-pointer no-underline"
            style={{ position: 'relative', zIndex: 30, pointerEvents: 'auto', display: 'inline-flex' }}
          >
            בוא נגלה לאן טסים
          </Link>
        </div>

        {/* Footer */}
        <div className="mt-12 md:mt-16 pt-6 md:pt-8 border-t border-white/20 text-center text-white/70 text-sm animate-fade-in-up px-4" style={{ animationDelay: '1.8s' }}>
          <p className="mb-2">© {new Date().getFullYear()} SmarTrip. כל הזכויות שמורות.</p>
          <p className="text-xs text-white/50">מערכת המלצות חכמה לטיולים מאורגנים</p>
        </div>
      </div>

      {/* CSS Animations - Optimized for smooth scrolling */}
      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translate3d(0, 20px, 0);
          }
          to {
            opacity: 1;
            transform: translate3d(0, 0, 0);
          }
        }

        .animate-fade-in {
          animation: fade-in 0.8s ease-out forwards;
          will-change: opacity;
        }

        .animate-fade-in-up {
          animation: fade-in-up 0.8s ease-out forwards;
          opacity: 0;
          will-change: opacity, transform;
        }

        /* Remove will-change after animation completes */
        .animate-fade-in.animation-complete,
        .animate-fade-in-up.animation-complete {
          will-change: auto;
        }
      `}</style>
    </div>
  );
}
