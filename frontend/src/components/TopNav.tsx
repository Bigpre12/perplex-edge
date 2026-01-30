import { useEffect } from 'react';
import { useSports } from '../api/public';
import { useSportContext } from '../context/SportContext';

export function TopNav() {
  const { sportId, sportName, setSport, setSports, setError } = useSportContext();
  const { data: sportsData, isLoading, error } = useSports();

  // Log errors for debugging
  useEffect(() => {
    if (error) {
      console.error('[TopNav] Failed to load sports:', error);
      setError(error instanceof Error ? error.message : 'Failed to load sports');
    }
  }, [error, setError]);

  // Update context when sports are loaded
  useEffect(() => {
    console.log('[TopNav] Sports data received:', sportsData?.items?.length ?? 0, 'sports');
    if (sportsData?.items) {
      setSports(sportsData.items);
    }
  }, [sportsData, setSports]);

  const handleSportChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedId = parseInt(e.target.value, 10);
    const selectedSport = sportsData?.items.find((s) => s.id === selectedId);
    if (selectedSport) {
      setSport(selectedSport.id, selectedSport.name, selectedSport.league_code);
    }
  };

  return (
    <header className="bg-gray-800 border-b border-gray-700">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo / Branding */}
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <span className="text-blue-400">⚡</span>
              Perplex Engine
            </h1>
            <p className="text-sm text-gray-400">Sports Betting Analytics</p>
          </div>

          {/* Sport Selector */}
          <div className="flex items-center gap-3">
            <label htmlFor="sport-select" className="text-sm text-gray-400">
              Sport:
            </label>
            {isLoading ? (
              <div className="bg-gray-700 text-gray-400 rounded px-4 py-2 text-sm">
                Loading...
              </div>
            ) : error ? (
              <div className="bg-red-900/50 text-red-400 rounded px-4 py-2 text-sm">
                Error loading sports
              </div>
            ) : (
              <select
                id="sport-select"
                value={sportId ?? ''}
                onChange={handleSportChange}
                className="bg-gray-700 text-white rounded px-4 py-2 text-sm font-medium 
                         border border-gray-600 hover:border-gray-500 focus:border-blue-500 
                         focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
              >
                {sportsData?.items.map((sport) => (
                  <option key={sport.id} value={sport.id}>
                    {sport.name} ({sport.league_code})
                  </option>
                ))}
              </select>
            )}

            {/* Current sport badge */}
            {sportName && (
              <span className="bg-blue-900/50 text-blue-400 text-xs px-3 py-1 rounded-full font-medium">
                {sportName}
              </span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
