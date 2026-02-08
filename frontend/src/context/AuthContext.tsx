/**
 * AuthContext - Clerk authentication with user plan management.
 * 
 * Wraps Clerk's authentication and adds:
 * - User plan info (free/trial/pro)
 * - Trial days remaining
 * - Sync user to backend on login
 * 
 * When Clerk is not configured (no VITE_CLERK_PUBLISHABLE_KEY),
 * provides default "not authenticated" values so the app still works.
 */

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useUser, useAuth as useClerkAuth } from '@clerk/clerk-react';
import { setAuthTokenProvider } from '../api/client';

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
  
  // Auth availability
  clerkEnabled: boolean;
  
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
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://railway-engine-production.up.railway.app';

// =============================================================================
// Provider (with Clerk)
// =============================================================================

function AuthProviderWithClerk({ children }: { children: ReactNode }) {
  const { isLoaded, isSignedIn, user: clerkUser } = useUser();
  const { signOut: clerkSignOut, getToken } = useClerkAuth();
  
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);

  // Register auth token provider for API client
  useEffect(() => {
    if (isLoaded && isSignedIn) {
      setAuthTokenProvider(() => getToken());
    }
  }, [isLoaded, isSignedIn, getToken]);

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
    clerkEnabled: true,
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
// Provider (without Clerk - fallback)
// =============================================================================

function AuthProviderWithoutClerk({ children }: { children: ReactNode }) {
  // Default "not authenticated" state
  const value: AuthContextValue = {
    isLoaded: true,
    isSignedIn: false,
    user: null,
    plan: 'free',
    isPro: false,
    isTrial: false,
    isFree: true,
    trialDaysLeft: null,
    clerkEnabled: false,
    signOut: async () => {
      console.warn('Auth not configured - signOut is a no-op');
    },
    syncUser: async () => {
      console.warn('Auth not configured - syncUser is a no-op');
    },
    getToken: async () => null,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// =============================================================================
// Main Provider (chooses based on clerkEnabled prop)
// =============================================================================

interface AuthProviderProps {
  children: ReactNode;
  clerkEnabled: boolean;
}

export function AuthProvider({ children, clerkEnabled }: AuthProviderProps) {
  if (clerkEnabled) {
    return <AuthProviderWithClerk>{children}</AuthProviderWithClerk>;
  }
  return <AuthProviderWithoutClerk>{children}</AuthProviderWithoutClerk>;
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
