"use client";
import React, { createContext, useContext, useState, useEffect } from "react";

import { SportKey as Sport } from "@/lib/sports.config";

interface SportContextType {
    selectedSport: Sport;
    setSelectedSport: (sport: Sport) => void;
}

const SportContext = createContext<SportContextType | undefined>(undefined);

import { useLucrixStore } from "@/store";

export function SportProvider({ children }: { children: React.ReactNode }) {
    const activeSport = useLucrixStore((state: any) => state.activeSport);
    const setActiveSport = useLucrixStore((state: any) => state.setActiveSport);

    return (
        <SportContext.Provider value={{ selectedSport: activeSport, setSelectedSport: setActiveSport }}>
            {children}
        </SportContext.Provider>
    );
}

export function useSport() {
    const context = useContext(SportContext);
    if (!context) {
        throw new Error("useSport must be used within a SportProvider");
    }
    return context;
}
