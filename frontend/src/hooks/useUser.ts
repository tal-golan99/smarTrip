/**
 * useUser hook - Manages current user authentication state and profile data.
 */
'use client';

import { useState, useEffect } from 'react';
import { getCurrentUser, supabase, isAuthAvailable } from '@/lib/supabaseClient';

export function useUser() {
  const [userName, setUserName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<any | null>(null);

  useEffect(() => {
    const loadUser = async () => {
      if (!isAuthAvailable() || !supabase) {
        setIsLoading(false);
        return;
      }
      
      try {
        const user = await getCurrentUser();
        if (user) {
          setUser(user);
          // Extract full name from user metadata or email
          const metadata = user.user_metadata || {};
          let fullName = null;
          if (metadata.full_name) {
            fullName = metadata.full_name;
          } else if (metadata.name) {
            fullName = metadata.name;
          } else if (metadata.first_name && metadata.last_name) {
            fullName = `${metadata.first_name} ${metadata.last_name}`;
          } else if (metadata.first_name) {
            fullName = metadata.first_name;
          } else if (metadata.last_name) {
            fullName = metadata.last_name;
          } else if (user.email && user.email.split('@')[0]) {
            fullName = user.email.split('@')[0];
          }
          setUserName(fullName);
        } else {
          setUserName(null);
        }
      } catch (error) {
        console.error('[useUser] Error loading user:', error);
        setUserName(null);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadUser();
    
    // Listen for auth state changes
    if (supabase) {
      const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
        if (session?.user) {
          loadUser();
        } else {
          setUserName(null);
          setUser(null);
          setIsLoading(false);
        }
      });
      
      return () => {
        subscription.unsubscribe();
      };
    }
  }, []);

  return { userName, isLoading, user };
}
