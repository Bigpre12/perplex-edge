import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SportKey } from '@/lib/sports.config';

interface LucrixStore {
    activeSport: SportKey;
    setActiveSport: (s: SportKey) => void;
    backendOnline: boolean;
    setBackendOnline: (v: boolean) => void;
    parlayLegs: any[];
    addLeg: (leg: any) => void;
    removeLeg: (id: string) => void;
    clearParlay: () => void;
    favoriteProps: string[];
    toggleFavProp: (id: string) => void;
    unreadAlerts: number;
    setUnreadAlerts: (n: number) => void;
}

export const useLucrixStore = create<LucrixStore>()(
    persist(
        (set) => ({
            activeSport: 'basketball_nba',
            setActiveSport: (s) => set({ activeSport: s }),

            backendOnline: false,
            setBackendOnline: (v) => set({ backendOnline: v }),

            parlayLegs: [],
            addLeg: (leg) => set(s => ({
                parlayLegs: s.parlayLegs.find((l: any) => l.id === leg.id)
                    ? s.parlayLegs
                    : [...s.parlayLegs, leg]
            })),
            removeLeg: (id) => set(s => ({ parlayLegs: s.parlayLegs.filter((l: any) => l.id !== id) })),
            clearParlay: () => set({ parlayLegs: [] }),

            favoriteProps: [],
            toggleFavProp: (id) => set(s => ({
                favoriteProps: s.favoriteProps.includes(id)
                    ? s.favoriteProps.filter(i => i !== id)
                    : [...s.favoriteProps, id]
            })),

            unreadAlerts: 0,
            setUnreadAlerts: (n) => set({ unreadAlerts: n }),
        }),
        {
            name: 'lucrix-store',
            storage: createJSONStorage(() => AsyncStorage),
        }
    )
);
