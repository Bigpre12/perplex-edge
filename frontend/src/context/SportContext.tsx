import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Types
export interface Sport {
  id: number;
  name: string;
  league_code: string;
}

interface SportContextType {
  sportId: number | null;
  sportName: string;
  leagueCode: string;
  setSport: (id: number, name: string, leagueCode: string) => void;
  sports: Sport[];
  setSports: (sports: Sport[]) => void;
  isLoading: boolean;
}

const SportContext = createContext<SportContextType | undefined>(undefined);

interface SportProviderProps {
  children: ReactNode;
}

export function SportProvider({ children }: SportProviderProps) {
  const [sportId, setSportId] = useState<number | null>(null);
  const [sportName, setSportName] = useState<string>('');
  const [leagueCode, setLeagueCode] = useState<string>('');
  const [sports, setSports] = useState<Sport[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Set default sport when sports are loaded
  useEffect(() => {
    if (sports.length > 0 && sportId === null) {
      const defaultSport = sports[0];
      setSportId(defaultSport.id);
      setSportName(defaultSport.name);
      setLeagueCode(defaultSport.league_code);
      setIsLoading(false);
    }
  }, [sports, sportId]);

  const setSport = (id: number, name: string, code: string) => {
    setSportId(id);
    setSportName(name);
    setLeagueCode(code);
  };

  const handleSetSports = (newSports: Sport[]) => {
    setSports(newSports);
    if (newSports.length > 0 && sportId === null) {
      setIsLoading(false);
    }
  };

  return (
    <SportContext.Provider
      value={{
        sportId,
        sportName,
        leagueCode,
        setSport,
        sports,
        setSports: handleSetSports,
        isLoading,
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
