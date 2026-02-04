/**
 * AuthContext - Clerk authentication with user plan management.
 * 
 * Wraps Clerk's authentication and adds:
 * - User plan info (free/trial/pro)
 * - Trial days remaining
 * - Sync user to backend on login
 */

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useUser, useAuth as useClerkAuth } from '@clerk/clerk-react';

// =============================================================================
// Types
// =============================================================================

export type UserPlan = 'free' | 'trial' | 'pro';

export interface UserInfo {
  id: string;
  email: string;
  firstName: string | null;
  lastName: string | null;
  plan: UserPlan;
  trialEndsAt: Date | null;
  createdAt: Date;
}

interface AuthContextValue {
  // Auth state
  isLoaded: boolean;
  isSignedIn: boolean;
  user: UserInfo | null;
  
  // Plan helpers
  plan: UserPlan;
  isPro: boolean;
  isTrial: boolean;
  isFree: boolean;
  trialDaysLeft: number | null;
  
  // Actions
  signOut: () => Promise<void>;
  syncUser: () => Promise<void>;
  getToken: () => Promise<string | null>;
}

// =============================================================================
// Context
// =============================================================================

const AuthContext = createContext<AuthContextValue | null>(null);

// API base URL from environment
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// =============================================================================
// Provider
// =============================================================================

export function AuthProvider({ children }: { children: ReactNode }) {
  const { isLoaded, isSignedIn, user: clerkUser } = useUser();
  const { signOut: clerkSignOut, getToken } = useClerkAuth();
  
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  // Track sync errors for debugging (not displayed to user currently)
  const [_syncError, setSyncError] = useState<string | null>(null);

  // Sync user to backend when Clerk user changes
  useEffect(() => {
    if (isLoaded && isSignedIn && clerkUser) {
      syncUserToBackend();
    } else if (isLoaded && !isSignedIn) {
      setUserInfo(null);
    }
  }, [isLoaded, isSignedIn, clerkUser?.id]);

  // Sync user data to backend
  const syncUserToBackend = async () => {
    if (!clerkUser) return;
    
    try {
      const token = await getToken();
      const response = await fetch(`${API_BASE_URL}/api/users/sync`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          clerk_id: clerkUser.id,
          email: clerkUser.primaryEmailAddress?.emailAddress || '',
          first_name: clerkUser.firstName,
          last_name: clerkUser.lastName,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setUserInfo({
          id: data.id,
          email: data.email,
          firstName: clerkUser.firstName,
          lastName: clerkUser.lastName,
          plan: data.plan || 'free',
          trialEndsAt: data.trial_ends_at ? new Date(data.trial_ends_at) : null,
          createdAt: new Date(data.created_at),
        });
        setSyncError(null);
      } else {
        // If backend sync fails, still set basic user info
        console.warn('Failed to sync user to backend:', response.status);
        setUserInfo({
          id: clerkUser.id,
          email: clerkUser.primaryEmailAddress?.emailAddress || '',
          firstName: clerkUser.firstName,
          lastName: clerkUser.lastName,
          plan: 'free',
          trialEndsAt: null,
          createdAt: new Date(),
        });
      }
    } catch (err) {
      console.error('Error syncing user:', err);
      setSyncError(err instanceof Error ? err.message : 'Sync failed');
      // Set basic user info even on error
      setUserInfo({
        id: clerkUser.id,
        email: clerkUser.primaryEmailAddress?.emailAddress || '',
        firstName: clerkUser.firstName,
        lastName: clerkUser.lastName,
        plan: 'free',
        trialEndsAt: null,
        createdAt: new Date(),
      });
    }
  };

  // Calculate trial days remaining
  const trialDaysLeft = userInfo?.trialEndsAt
    ? Math.max(0, Math.ceil((userInfo.trialEndsAt.getTime() - Date.now()) / (1000 * 60 * 60 * 24)))
    : null;

  // Plan helpers
  const plan = userInfo?.plan || 'free';
  const isPro = plan === 'pro';
  const isTrial = plan === 'trial';
  const isFree = plan === 'free';

  const value: AuthContextValue = {
    isLoaded,
    isSignedIn: isSignedIn || false,
    user: userInfo,
    plan,
    isPro,
    isTrial,
    isFree,
    trialDaysLeft,
    signOut: async () => {
      await clerkSignOut();
      setUserInfo(null);
    },
    syncUser: syncUserToBackend,
    getToken: async () => await getToken(),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// =============================================================================
// Hooks
// =============================================================================

export function useAuthContext(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
}

// Convenience hooks
export function useCurrentUser() {
  const { user, isLoaded, isSignedIn } = useAuthContext();
  return { user, isLoaded, isSignedIn };
}

export function useUserPlan() {
  const { plan, isPro, isTrial, isFree, trialDaysLeft } = useAuthContext();
  return { plan, isPro, isTrial, isFree, trialDaysLeft };
}

export function useRequireAuth() {
  const { isLoaded, isSignedIn } = useAuthContext();
  return { isLoaded, isSignedIn, requiresAuth: isLoaded && !isSignedIn };
}
