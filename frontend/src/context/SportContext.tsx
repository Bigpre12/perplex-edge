import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Types
export interface Sport {
  id: number;
  name: string;
  league_code: string;
  key: string;
}

interface SportContextType {
  sportId: number | null;
  sportName: string;
  leagueCode: string;
  setSport: (id: number, name: string, leagueCode: string) => void;
  sports: Sport[];
  setSports: (sports: Sport[]) => void;
  isLoading: boolean;
  error: string | null;
  setError: (error: string | null) => void;
}

const SportContext = createContext<SportContextType | undefined>(undefined);

interface SportProviderProps {
  children: ReactNode;
}

export function SportProvider({ children }: SportProviderProps) {
  const [sportId, setSportId] = useState<number | null>(null);
  const [sportName, setSportName] = useState<string>('');
  const [leagueCode, setLeagueCode] = useState<string>('');
  const [sports, setSportsState] = useState<Sport[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Set default sport when sports are loaded
  useEffect(() => {
    if (import.meta.env.DEV) console.log('[SportContext] Sports updated:', sports.length, 'sportId:', sportId);
    
    if (sports.length > 0 && sportId === null) {
      const defaultSport = sports[0];
      if (import.meta.env.DEV) console.log('[SportContext] Setting default sport:', defaultSport);
      setSportId(defaultSport.id);
      setSportName(defaultSport.name);
      setLeagueCode(defaultSport.league_code);
      // Only set loading to false AFTER setting the sport
      setIsLoading(false);
    }
  }, [sports, sportId]);

  const setSport = (id: number, name: string, code: string) => {
    if (import.meta.env.DEV) console.log('[SportContext] setSport called:', id, name, code);
    setSportId(id);
    setSportName(name);
    setLeagueCode(code);
  };

  const setSports = (newSports: Sport[]) => {
    if (import.meta.env.DEV) console.log('[SportContext] setSports called with:', newSports.length, 'sports');
    setSportsState(newSports);
    // Don't set isLoading=false here - wait for useEffect to set default sport
  };

  return (
    <SportContext.Provider
      value={{
        sportId,
        sportName,
        leagueCode,
        setSport,
        sports,
        setSports,
        isLoading,
        error,
        setError,
      }}
    >
      {children}
    </SportContext.Provider>
  );
}

export function useSportContext() {
  const context = useContext(SportContext);
  if (context === undefined) {
    throw new Error('useSportContext must be used within a SportProvider');
  }
  return context;
}
