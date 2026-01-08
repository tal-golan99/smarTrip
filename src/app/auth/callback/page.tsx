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
        window.location.href = redirectTo;
        return;
      }
      
      try {
        // Check if we're on the wrong domain (Supabase redirect issue)
        // If URL contains Supabase domain + our domain, it's a misconfiguration
        if (typeof window !== 'undefined' && window.location.hostname.includes('supabase.co')) {
          // Check if pathname contains our domain (misconfigured redirect)
          const pathname = window.location.pathname;
          if (pathname.includes('vercel.app') || pathname.includes('smartrip')) {
            console.error('[Auth] Invalid redirect URL detected. Supabase Dashboard URLs must include https://');
            console.error('[Auth] Current URL:', window.location.href);
            
            // Extract hash and search params before redirecting
            const hash = window.location.hash;
            const search = window.location.search;
            
            // Redirect to correct domain with all params
            const correctUrl = `https://smartrip-alpha.vercel.app/auth/callback${search}${hash}`;
            console.log('[Auth] Redirecting to correct URL:', correctUrl);
            window.location.href = correctUrl;
            return;
          }
        }
        
        // First, try to get session immediately (might already be ready)
        const { data: { session: initialSession }, error: initialError } = await supabase.auth.getSession();
        
        if (initialError) {
          console.error('[Auth] Callback error:', initialError);
          window.location.href = '/auth?error=authentication_failed';
          return;
        }
        
        if (initialSession) {
          // Session already ready - redirect immediately
          const redirectTo = searchParams.get('redirect') || '/search';
          console.log('[Auth] Session ready, redirecting to:', redirectTo);
          window.location.href = redirectTo;
          return;
        }
        
        // Session not ready yet - use onAuthStateChange listener to wait for it
        // This is more reliable than polling with retries
        console.log('[Auth] Session not ready, waiting for SIGNED_IN event...');
        
        const redirectTo = searchParams.get('redirect') || '/search';
        const SESSION_TIMEOUT = 5000; // 5 second timeout
        let timeoutId: NodeJS.Timeout | null = null;
        let subscription: { unsubscribe: () => void } | null = null;
        
        // Cleanup function
        const cleanup = () => {
          if (timeoutId) {
            clearTimeout(timeoutId);
            timeoutId = null;
          }
          if (subscription) {
            subscription.unsubscribe();
            subscription = null;
          }
        };
        
        // Listen for auth state changes
        const { data: { subscription: authSubscription } } = supabase.auth.onAuthStateChange((event, session) => {
          if (event === 'SIGNED_IN' && session) {
            cleanup();
            console.log('[Auth] SIGNED_IN event received, redirecting to:', redirectTo);
            // Use window.location.href for more reliable redirect after OAuth
            window.location.href = redirectTo;
          } else if (event === 'SIGNED_OUT') {
            cleanup();
            console.error('[Auth] SIGNED_OUT event received');
            window.location.href = '/auth?error=authentication_failed';
          } else if (event === 'TOKEN_REFRESHED' && session) {
            // Token refreshed - we have a valid session now
            cleanup();
            console.log('[Auth] TOKEN_REFRESHED event received, redirecting to:', redirectTo);
            window.location.href = redirectTo;
          }
        });
        
        subscription = authSubscription;
        
        // Set timeout for session wait
        timeoutId = setTimeout(() => {
          cleanup();
          console.error('[Auth] Session timeout - redirecting to auth page');
          window.location.href = '/auth?error=session_timeout';
        }, SESSION_TIMEOUT);
        
        // Fallback: If we still don't have a session after setting up listener,
        // do a few retries with getSession() as backup
        let retryCount = 0;
        const MAX_SESSION_RETRIES = 3;
        const SESSION_RETRY_DELAY = 500;
        
        const retrySession = async () => {
          // Ensure supabase is available (TypeScript guard)
          const supabaseClient = supabase;
          if (!supabaseClient) {
            return;
          }
          
          while (retryCount < MAX_SESSION_RETRIES) {
            await new Promise(resolve => setTimeout(resolve, SESSION_RETRY_DELAY));
            
            const { data: { session: retrySession } } = await supabaseClient.auth.getSession();
            if (retrySession) {
              cleanup();
              console.log('[Auth] Session found on retry, redirecting to:', redirectTo);
              window.location.href = redirectTo;
              return;
            }
            
            retryCount++;
          }
        };
        
        // Start retry as backup (timeout will handle if this doesn't work)
        retrySession();
        
      } catch (err) {
        console.error('[Auth] Callback exception:', err);
        window.location.href = '/auth?error=unexpected_error';
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



