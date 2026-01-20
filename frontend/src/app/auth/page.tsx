/**
 * Authentication page - Handles Google OAuth login and user registration.
 */
'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { supabase, isAuthAvailable } from '@/lib/supabaseClient';
import Image from 'next/image';
import { Home } from 'lucide-react';

function AuthPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  // Check if user is already logged in
  useEffect(() => {
    if (!isAuthAvailable() || !supabase) {
      // Supabase not configured - allow guest access
      return;
    }
    
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        // Already logged in, redirect to search
        const redirectTo = searchParams.get('redirect') || '/search';
        router.push(redirectTo);
      }
    });
  }, [router, searchParams]);

  // Validate password format
  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 6) {
      return 'הסיסמה חייבת להכיל לפחות 6 תווים';
    }
    if (pwd.length > 12) {
      return 'הסיסמה יכולה להכיל עד 12 תווים';
    }
    // Only English letters and numbers
    if (!/^[a-zA-Z0-9]+$/.test(pwd)) {
      return 'הסיסמה יכולה להכיל רק אותיות באנגלית וספרות';
    }
    return null;
  };

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isAuthAvailable() || !supabase) {
      setError('אימות לא מוגדר. אנא הגדר את משתני הסביבה של Supabase.');
      return;
    }
    
    setError(null);
    setMessage(null);
    setPasswordError(null);
    setLoading(true);

    try {
      if (isSignUp) {
        // Validate password format
        const pwdError = validatePassword(password);
        if (pwdError) {
          setPasswordError(pwdError);
          setLoading(false);
          return;
        }

        // Check if passwords match
        if (password !== confirmPassword) {
          setPasswordError('הסיסמאות לא תואמות');
          setLoading(false);
          return;
        }

        // Sign up
        // Get the correct origin (production or localhost)
        const origin = typeof window !== 'undefined' ? window.location.origin : '';
        const { data, error: signUpError } = await supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: `${origin}/auth?redirect=/search`,
          },
        });

        if (signUpError) throw signUpError;

        if (data.user && !data.session) {
          // Email confirmation required (configured in Supabase Dashboard)
          setMessage('נא לבדוק את האימייל שלך לאישור החשבון');
          // Clear form
          setEmail('');
          setPassword('');
          setConfirmPassword('');
        } else if (data.session) {
          // Auto-signed in (email confirmation disabled in Supabase)
          const redirectTo = searchParams.get('redirect') || '/search';
          router.push(redirectTo);
        }
      } else {
        // Sign in
        const { data, error: signInError } = await supabase.auth.signInWithPassword({
          email,
          password,
        });

        if (signInError) throw signInError;

        if (data.session) {
          const redirectTo = searchParams.get('redirect') || '/search';
          router.push(redirectTo);
        }
      }
    } catch (err: any) {
      setError(err.message || 'שגיאה בהתחברות');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleAuth = async () => {
    if (!isAuthAvailable() || !supabase) {
      setError('אימות לא מוגדר. אנא הגדר את משתני הסביבה של Supabase.');
      return;
    }
    
    setError(null);
    setLoading(true);

    try {
      const redirectTo = searchParams.get('redirect') || '/search';
      
      // Get the correct origin (production or localhost)
      // In production, window.location.origin will be the Vercel URL
      // In development, it will be http://localhost:3000
      const origin = typeof window !== 'undefined' ? window.location.origin : '';
      
      // Build the callback URL - must match one of the URLs configured in Supabase Dashboard
      const callbackUrl = `${origin}/auth/callback?redirect=${encodeURIComponent(redirectTo)}`;
      
      const { error: oauthError } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: callbackUrl,
        },
      });

      if (oauthError) throw oauthError;
      // OAuth will redirect, so we don't need to do anything else
    } catch (err: any) {
      setError(err.message || 'שגיאה בהתחברות עם Google');
      setLoading(false);
    }
  };

  const handleContinueAsGuest = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const redirectTo = searchParams.get('redirect') || '/search';
    // Use window.location for more reliable navigation
    window.location.href = redirectTo;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#076839] via-[#0ba55c] to-[#12acbe] flex items-center justify-center px-4 py-8">
      <div className="max-w-md w-full bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl p-8 md:p-10 relative">
        {/* Home Button */}
        <Link
          href="/"
          className="absolute top-4 right-4 flex items-center gap-2 px-3 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all duration-200 group"
          title="חזרה לדף הבית"
        >
          <Home className="w-5 h-5 group-hover:scale-110 transition-transform" />
        </Link>

        {/* Logo */}
        <div className="text-center mb-8">
          <Image
            src="/images/logo/smartrip.png"
            alt="SmartTrip Logo"
            width={120}
            height={120}
            className="mx-auto mb-4 brightness-0 h-auto"
            style={{ width: 'auto' }}
            priority
          />
          <p className="text-gray-600 text-sm mb-4">
            התחבר או המשך כאורח כדי להתחיל לחפש טיולים
          </p>
        </div>

        {/* Error/Message Display */}
        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-sm text-center">
            {error}
          </div>
        )}

        {message && (
          <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded-lg text-sm text-center">
            {message}
          </div>
        )}

        {/* Email/Password Form */}
        {isAuthAvailable() ? (
        <form onSubmit={handleEmailAuth} className="space-y-4 mb-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              אימייל
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#076839] focus:border-transparent"
              placeholder="your@email.com"
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              סיסמה
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setPasswordError(null);
              }}
              required
              minLength={6}
              maxLength={12}
              pattern="[a-zA-Z0-9]+"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-[#076839] focus:border-transparent ${
                passwordError ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder={isSignUp ? '6-12 תווים, אותיות וספרות בלבד' : '••••••••'}
              disabled={loading}
            />
            {isSignUp && (
              <p className="mt-1 text-xs text-gray-500">
                6-12 תווים, אותיות באנגלית וספרות בלבד
              </p>
            )}
            {passwordError && (
              <p className="mt-1 text-xs text-red-600">{passwordError}</p>
            )}
          </div>

          {isSignUp && (
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                אימות סיסמה
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  setPasswordError(null);
                }}
                required={isSignUp}
                minLength={6}
                maxLength={12}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-[#076839] focus:border-transparent ${
                  passwordError ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="הזן שוב את הסיסמה"
                disabled={loading}
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#076839] text-white py-3 rounded-lg font-semibold hover:bg-[#065a2e] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'מעבד...' : isSignUp ? 'צור חשבון' : 'התחבר'}
          </button>
        </form>
        ) : (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-center text-sm">
            <p className="text-yellow-800 font-medium mb-1">אימות לא מוגדר</p>
            <p className="text-yellow-700 text-xs">המשך כאורח כדי להתחיל לחפש טיולים</p>
          </div>
        )}

        {/* Toggle Sign Up/Sign In */}
        {isAuthAvailable() && (
        <div className="text-center mb-6">
          <button
            type="button"
            onClick={() => {
              setIsSignUp(!isSignUp);
              setError(null);
              setMessage(null);
              setPasswordError(null);
              setPassword('');
              setConfirmPassword('');
            }}
            className="text-sm text-[#076839] hover:underline"
            disabled={loading}
          >
            {isSignUp
              ? 'כבר יש לך חשבון? התחבר'
              : 'אין לך חשבון? צור חשבון חדש'}
          </button>
        </div>
        )}

        {/* Divider */}
        {isAuthAvailable() && (
        <div className="relative mb-6">
          <div className="flex items-center">
            <div className="flex-1 border-t border-gray-300"></div>
            <span className="px-3 text-sm text-gray-500">או</span>
            <div className="flex-1 border-t border-gray-300"></div>
          </div>
        </div>
        )}

        {/* Google Sign In */}
        {isAuthAvailable() && (
        <button
          onClick={handleGoogleAuth}
          disabled={loading}
          className="w-full flex items-center justify-center gap-3 bg-white border-2 border-gray-300 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mb-6"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          המשך עם Google
        </button>
        )}

        {/* Continue as Guest */}
        <div className="mt-6 text-center">
          <Link
            href={searchParams.get('redirect') || '/search'}
            onClick={handleContinueAsGuest}
            className="text-sm text-gray-600 hover:text-[#076839] hover:underline transition-colors disabled:opacity-50 cursor-pointer no-underline inline-block"
            style={{ pointerEvents: loading ? 'none' : 'auto' }}
          >
            המשך כאורח
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function AuthPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-[#076839] via-[#0ba55c] to-[#12acbe] flex items-center justify-center">
        <div className="text-center text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-lg">טוען...</p>
        </div>
      </div>
    }>
      <AuthPageContent />
    </Suspense>
  );
}



