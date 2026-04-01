import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { SportKey } from '@/lib/sports.config';
import { Tier as UserTier } from '@/lib/permissions';

interface LucrixState {
    // Core State
    activeSport: SportKey;
    userTier: UserTier;

    // UI & Status
    backendOnline: boolean;
    isConnecting: boolean;
    unreadAlerts: number;

    // Tools State (Parlay)
    parlayLegs: any[];
    favoriteProps: string[];

    // Actions
    setActiveSport: (sport: SportKey) => void;
    setUserTier: (tier: UserTier) => void;
    setBackendOnline: (status: boolean) => void;
    setIsConnecting: (status: boolean) => void;
    setUnreadAlerts: (count: number) => void;

    // Parlay Actions
    addLeg: (leg: any) => void;
    removeLeg: (id: string) => void;
    clearParlay: () => void;

    // Prefs Actions
    toggleFavProp: (id: string) => void;
}

export const useLucrixStore = create<LucrixState>()(
    persist(
        (set) => ({
            // Defaults
            activeSport: 'basketball_nba',
            userTier: 'free',
            backendOnline: false,
            isConnecting: false,
            unreadAlerts: 0,
            parlayLegs: [],
            favoriteProps: [],

            // Core Actions
            setActiveSport: (activeSport) => set({ activeSport }),
            setUserTier: (userTier) => set({ userTier }),
            setBackendOnline: (backendOnline) => set({ backendOnline }),
            setIsConnecting: (isConnecting) => set({ isConnecting }),
            setUnreadAlerts: (unreadAlerts) => set({ unreadAlerts }),

            // Parlay Actions
            addLeg: (leg) => set((state) => ({
                parlayLegs: state.parlayLegs.find((l: any) => l.id === leg.id)
                    ? state.parlayLegs
                    : [...state.parlayLegs, leg]
            })),
            removeLeg: (id) => set((state) => ({
                parlayLegs: state.parlayLegs.filter((l: any) => l.id !== id)
            })),
            clearParlay: () => set({ parlayLegs: [] }),

            // Prefs
            toggleFavProp: (id) => set((state) => ({
                favoriteProps: state.favoriteProps.includes(id)
                    ? state.favoriteProps.filter(i => i !== id)
                    : [...state.favoriteProps, id]
            })),
        }),
        {
            name: 'lucrix-storage',
            // Only persist core preferences, not transient status
            partialize: (state) => ({
                activeSport: state.activeSport,
                userTier: state.userTier,
                favoriteProps: state.favoriteProps,
                parlayLegs: state.parlayLegs
            }),
        }
    )
);
