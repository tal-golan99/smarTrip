'use client';

import { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { supabase, isAuthAvailable } from '@/lib/supabaseClient';

/**
 * OAuth Callback Page
 * Handles redirect from Google OAuth
 */
function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const handleCallback = async () => {
      // If Supabase is not configured, redirect to search
      if (!isAuthAvailable() || !supabase) {
        const redirectTo = searchParams.get('redirect') || '/search';
        router.push(redirectTo);
        return;
      }
      
      try {
        // Supabase handles the OAuth callback automatically
        const { data, error } = await supabase.auth.getSession();

        if (error) {
          console.error('[Auth] Callback error:', error);
          router.push('/auth?error=authentication_failed');
          return;
        }

        if (data.session) {
          // Successfully authenticated
          const redirectTo = searchParams.get('redirect') || '/search';
          router.push(redirectTo);
        } else {
          // No session (shouldn't happen, but handle gracefully)
          router.push('/auth?error=no_session');
        }
      } catch (err) {
        console.error('[Auth] Callback exception:', err);
        router.push('/auth?error=unexpected_error');
      }
    };

    handleCallback();
  }, [router, searchParams]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#076839] via-[#0ba55c] to-[#12acbe] flex items-center justify-center">
      <div className="text-center text-white">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
        <p className="text-lg">מתחבר...</p>
      </div>
    </div>
  );
}

export default function AuthCallback() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-[#076839] via-[#0ba55c] to-[#12acbe] flex items-center justify-center">
        <div className="text-center text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-lg">טוען...</p>
        </div>
      </div>
    }>
      <AuthCallbackContent />
    </Suspense>
  );
}



