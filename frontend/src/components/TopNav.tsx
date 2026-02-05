import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useSports } from '../api/public';
import { useSportContext } from '../context/SportContext';

// Discord invite link (set in environment)
const DISCORD_INVITE_URL = import.meta.env.VITE_DISCORD_INVITE_URL || 'https://discord.gg/qRMrfn9d';

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
      if (import.meta.env.DEV) console.error('[TopNav] Failed to load sports:', error);
      setError(error instanceof Error ? error.message : 'Failed to load sports');
    }
  }, [error, setError]);

  // Update context when sports are loaded
  useEffect(() => {
    if (import.meta.env.DEV) console.log('[TopNav] Sports data received:', sportsData?.items?.length ?? 0, 'sports');
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

  const [mobileOpen, setMobileOpen] = useState(false);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

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

          {/* Mobile Hamburger Button */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
            aria-label="Toggle menu"
          >
            {mobileOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>

          {/* Desktop Navigation Links */}
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
            
            {/* Discord Link */}
            <a
              href={DISCORD_INVITE_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-2 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-700 transition-colors flex items-center gap-1.5"
              title="Join our Discord community"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
              </svg>
              <span className="hidden lg:inline">Discord</span>
            </a>
          </nav>

          {/* Sport Selector (desktop) */}
          <div className="hidden md:flex items-center gap-3">
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

      {/* Mobile Slide-Out Menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-gray-700">
          <div className="px-4 py-3 space-y-1">
            {/* Sport Selector (mobile) */}
            <div className="pb-3 mb-2 border-b border-gray-700">
              {isLoading ? (
                <div className="bg-gray-700 text-gray-400 rounded px-3 py-2 text-sm">Loading sports...</div>
              ) : error ? (
                <div className="bg-red-900/50 text-red-400 rounded px-3 py-2 text-sm">Failed to load sports</div>
              ) : (
                <select
                  value={sportId ?? ''}
                  onChange={handleSportChange}
                  className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm font-medium 
                           border border-gray-600 focus:border-blue-500 focus:outline-none"
                >
                  {sportsData?.items.map((sport) => (
                    <option key={sport.id} value={sport.id}>{sport.name}</option>
                  ))}
                </select>
              )}
            </div>

            {/* Nav Links */}
            {NAV_LINKS.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive(link.to)
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`}
              >
                {link.label}
              </Link>
            ))}

            {/* More Links */}
            <div className="pt-2 mt-2 border-t border-gray-700">
              <div className="px-3 py-1 text-xs font-semibold text-gray-500 uppercase">More</div>
              {MORE_LINKS.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive(link.to)
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-gray-700'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </div>

            {/* Discord Link (mobile) */}
            <div className="pt-2 mt-2 border-t border-gray-700">
              <a
                href={DISCORD_INVITE_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-700 transition-colors"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
                </svg>
                Join Discord
              </a>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
