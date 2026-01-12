/**
 * Supabase Client for Authentication
 * ===================================
 * 
 * Provides a singleton Supabase client instance for:
 * - User authentication (email/password, Google OAuth)
 * - Session management
 * - User profile access
 * 
 * Note: If environment variables are not set, auth features will be disabled
 * but the app will continue to work (guest mode only).
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Debug: Log environment variables (only in development, only once)
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  const debugKey = 'supabase_env_debug';
  if (!sessionStorage.getItem(debugKey)) {
    console.group('[Auth Debug] Environment Variables');
    console.log('NEXT_PUBLIC_SUPABASE_URL:', supabaseUrl || '❌ MISSING');
    console.log('NEXT_PUBLIC_SUPABASE_ANON_KEY:', supabaseAnonKey ? `✅ SET (${supabaseAnonKey.length} chars)` : '❌ MISSING');
    console.log('isSupabaseConfigured:', !!(supabaseUrl && supabaseAnonKey));
    console.log('File location check: .env.local should be in frontend/ directory');
    console.groupEnd();
    sessionStorage.setItem(debugKey, 'true');
  }
}

// Check if Supabase is configured
const isSupabaseConfigured = !!(supabaseUrl && supabaseAnonKey);

// Create Supabase client only if configured, otherwise create a mock client
let supabase: SupabaseClient | null = null;

// Wrap in try-catch to prevent module initialization errors from breaking the app
try {
  if (isSupabaseConfigured) {
    supabase = createClient(supabaseUrl!, supabaseAnonKey!, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    });
  } else {
    // In development, log a warning but don't break the app
    // Only log once to avoid console spam
    if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
      const hasLogged = sessionStorage.getItem('supabase_warning_logged');
      if (!hasLogged) {
        console.warn(
          '[Auth] Supabase not configured. ' +
          'Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY ' +
          'to enable authentication. App will work in guest mode.'
        );
        sessionStorage.setItem('supabase_warning_logged', 'true');
      }
    }
  }
} catch (error) {
  // If Supabase client creation fails, continue without auth
  console.error('[Auth] Failed to initialize Supabase client:', error);
  supabase = null;
}

/**
 * Get current user session
 * Returns null if user is not authenticated or Supabase is not configured
 */
export async function getCurrentSession() {
  if (!supabase) {
    return null;
  }
  
  try {
    const { data, error } = await supabase.auth.getSession();
    if (error) {
      console.error('[Auth] Error getting session:', error);
      return null;
    }
    return data.session;
  } catch (error) {
    console.error('[Auth] Exception getting session:', error);
    return null;
  }
}

/**
 * Get current authenticated user
 * Returns null if user is not authenticated or Supabase is not configured
 */
export async function getCurrentUser() {
  if (!supabase) {
    return null;
  }
  
  try {
    // First check if there's a session to avoid AuthSessionMissingError
    const session = await getCurrentSession();
    if (!session) {
      // No session - user is not authenticated (this is normal, not an error)
      return null;
    }
    
    // If we have a session, get the user
    const { data, error } = await supabase.auth.getUser();
    if (error) {
      // Only log unexpected errors (not AuthSessionMissingError)
      if (error.name !== 'AuthSessionMissingError') {
        console.error('[Auth] Error getting user:', error);
      }
      return null;
    }
    return data.user;
  } catch (error: any) {
    // Only log unexpected errors (not AuthSessionMissingError)
    if (error?.name !== 'AuthSessionMissingError' && error?.message !== 'Auth session missing!') {
      console.error('[Auth] Exception getting user:', error);
    }
    return null;
  }
}

/**
 * Get access token for API requests
 * Returns null if user is not authenticated or Supabase is not configured
 */
export async function getAccessToken(): Promise<string | null> {
  if (!supabase) {
    return null;
  }
  
  const session = await getCurrentSession();
  return session?.access_token || null;
}

/**
 * Check if Supabase is configured
 */
export function isAuthAvailable(): boolean {
  return isSupabaseConfigured && supabase !== null;
}

// Export supabase client (may be null if not configured)
export { supabase };



