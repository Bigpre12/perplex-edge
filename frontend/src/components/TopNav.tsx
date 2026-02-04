import { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useSports } from '../api/public';
import { useSportContext } from '../context/SportContext';

// Navigation links
const NAV_LINKS = [
  { to: '/today', label: 'Today' },
  { to: '/props', label: 'Props' },
  { to: '/stats', label: 'Stats' },
  { to: '/parlay', label: 'Parlay' },
  { to: '/my-edge', label: 'My Edge' },
  { to: '/my-bets', label: 'My Bets' },
];

// More dropdown links
const MORE_LINKS = [
  { to: '/all-sports', label: 'All Sports' },
  { to: '/live-ev', label: 'Live EV' },
  { to: '/game-lines', label: 'Game Lines' },
  { to: '/100-hits', label: '100% Hits' },
  { to: '/model-performance', label: 'Model Performance' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/backtest', label: 'Backtest' },
  { to: '/admin', label: 'Admin' },
];

export function TopNav() {
  const location = useLocation();
  const { sportId, setSport, setSports, setError } = useSportContext();
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

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="bg-gray-800 border-b border-gray-700">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo / Branding */}
          <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <span className="text-blue-400 text-xl">⚡</span>
            <span className="text-xl font-bold text-white">Perplex</span>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive(link.to)
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`}
              >
                {link.label}
              </Link>
            ))}
            
            {/* More dropdown */}
            <div className="relative group">
              <button className="px-3 py-2 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-700 transition-colors flex items-center gap-1">
                More
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <div className="absolute right-0 mt-1 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                {MORE_LINKS.map((link) => (
                  <Link
                    key={link.to}
                    to={link.to}
                    className={`block px-4 py-2 text-sm ${
                      isActive(link.to)
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-300 hover:text-white hover:bg-gray-700'
                    } first:rounded-t-lg last:rounded-b-lg`}
                  >
                    {link.label}
                  </Link>
                ))}
              </div>
            </div>
          </nav>

          {/* Sport Selector */}
          <div className="flex items-center gap-3">
            {isLoading ? (
              <div className="bg-gray-700 text-gray-400 rounded px-3 py-1.5 text-sm">
                Loading...
              </div>
            ) : error ? (
              <div className="bg-red-900/50 text-red-400 rounded px-3 py-1.5 text-sm">
                Error
              </div>
            ) : (
              <select
                id="sport-select"
                value={sportId ?? ''}
                onChange={handleSportChange}
                className="bg-gray-700 text-white rounded px-3 py-1.5 text-sm font-medium 
                         border border-gray-600 hover:border-gray-500 focus:border-blue-500 
                         focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
              >
                {sportsData?.items.map((sport) => (
                  <option key={sport.id} value={sport.id}>
                    {sport.name}
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
