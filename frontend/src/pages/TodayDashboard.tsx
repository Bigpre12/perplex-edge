/**
 * TodayDashboard - The primary daily workflow page.
 * 
 * Combines:
 * - Top EV props across selected sports (left 2/3)
 * - Hot players panel (right sidebar)
 * - Win/lose streaks (right sidebar)
 * - Tomorrow's full slate preview
 * - Quick access links
 */

import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useSportContext } from '../context/SportContext';
import { usePlayerPropPicks, useFullSlate } from '../api/public';
import { HotPlayersPanel } from '../components/HotPlayersPanel';
import { StreaksPanel } from '../components/StreaksPanel';
import { FullSlateReview } from '../components/FullSlateReview';

// Get tomorrow's date in ISO format
function getTomorrowDate(): string {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return tomorrow.toISOString().split('T')[0];
}

// Format confidence as percentage
function formatPct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

// Format EV as percentage
function formatEv(value: number): string {
  const pct = value * 100;
  return pct >= 0 ? `+${pct.toFixed(1)}%` : `${pct.toFixed(1)}%`;
}

export function TodayDashboard() {
  const { sportId, sportName } = useSportContext();
  const [showAllProps, setShowAllProps] = useState(false);
  
  // Fetch top EV props for current sport
  const { data: propsData, isLoading: propsLoading, error: propsError } = usePlayerPropPicks(sportId, {
    min_ev: 0.03,
    min_confidence: 0.55,
    limit: showAllProps ? 50 : 25,
  });
  
  // Fetch tomorrow's slate
  const tomorrowDate = useMemo(() => getTomorrowDate(), []);
  const { data: slateData, isLoading: slateLoading, error: slateError } = useFullSlate(tomorrowDate, 0, 0, 20);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Today's Board</h1>
          <p className="text-gray-400 text-sm">
            {sportName} - {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
            <span className="text-gray-500 ml-2">· Tomorrow's preview: {tomorrowDate}</span>
          </p>
        </div>
        <Link
          to="/props"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
        >
          All Props
        </Link>
      </header>

      {/* Main Grid: 3 columns on large screens */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Section: Top EV Props (spans 2 columns) */}
        <section className="lg:col-span-2 bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="p-4 border-b border-gray-700 flex items-center justify-between">
            <div>
              <h2 className="font-bold text-white">Top EV Player Props</h2>
              <p className="text-xs text-gray-400">Highest expected value picks today</p>
            </div>
            <Link to="/props" className="text-blue-400 text-sm hover:text-blue-300">
              See all →
            </Link>
          </div>
          
          <div className="p-4">
            {propsLoading ? (
              <div className="animate-pulse space-y-3">
                {[...Array(8)].map((_, i) => (
                  <div key={i} className="h-14 bg-gray-700/50 rounded" />
                ))}
              </div>
            ) : propsError ? (
              <div className="text-center py-8 text-red-400 text-sm">
                Could not load props. Please try again.
              </div>
            ) : !propsData?.items?.length ? (
              <div className="text-center py-8 text-gray-500">
                No high-EV props found for {sportName}. Check back later.
              </div>
            ) : (
              <div className="space-y-2">
                {propsData.items.slice(0, showAllProps ? 25 : 10).map((pick) => (
                  <div
                    key={pick.pick_id}
                    className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg hover:bg-gray-700/50 transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-white truncate">{pick.player_name}</span>
                        <span className="text-xs text-gray-500">{pick.team_abbr || pick.team}</span>
                        {pick.opponent_abbr && (
                          <span className="text-xs text-gray-600">vs {pick.opponent_abbr}</span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-400 mt-0.5">
                        <span>{pick.stat_type}</span>
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                          pick.side === 'over' 
                            ? 'bg-green-900/50 text-green-400' 
                            : 'bg-red-900/50 text-red-400'
                        }`}>
                          {pick.side.toUpperCase()} {pick.line}
                        </span>
                        <span className="text-gray-500">{pick.odds > 0 ? `+${pick.odds}` : pick.odds}</span>
                      </div>
                    </div>
                    <div className="text-right ml-4">
                      <div className={`font-bold ${pick.expected_value >= 0.05 ? 'text-green-400' : 'text-blue-400'}`}>
                        {formatEv(pick.expected_value)}
                      </div>
                      <div className="text-xs text-gray-500">
                        {formatPct(pick.model_probability)} prob
                      </div>
                    </div>
                  </div>
                ))}
                
                {propsData.items.length > 10 && !showAllProps && (
                  <button
                    onClick={() => setShowAllProps(true)}
                    className="w-full py-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    Show more ({propsData.items.length - 10} more)
                  </button>
                )}
                
                {showAllProps && propsData.items.length > 10 && (
                  <button
                    onClick={() => setShowAllProps(false)}
                    className="w-full py-2 text-sm text-gray-400 hover:text-gray-300 transition-colors"
                  >
                    Show less
                  </button>
                )}
              </div>
            )}
          </div>
        </section>

        {/* Right Sidebar: Hot Players + Streaks */}
        <section className="space-y-6">
          {/* Hot Players Panel */}
          <HotPlayersPanel sportId={sportId} limit={5} />
          
          {/* Streaks Panel */}
          <StreaksPanel sportId={sportId} minStreak={3} limit={10} />
        </section>
      </div>

      {/* Tomorrow's Slate - Full Width */}
      <section className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <div>
            <h2 className="font-bold text-white">Tomorrow's Slate Preview</h2>
            <p className="text-xs text-gray-400">All sports for {tomorrowDate}</p>
          </div>
          <Link to="/all-sports" className="text-blue-400 text-sm hover:text-blue-300">
            Full slate →
          </Link>
        </div>
        
        <div className="p-4">
          {slateLoading ? (
            <div className="animate-pulse space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-16 bg-gray-700/50 rounded" />
              ))}
            </div>
          ) : slateError ? (
            <div className="text-center py-6 text-red-400 text-sm">
              Could not load tomorrow's slate. Please try again.
            </div>
          ) : !slateData || slateData.total_props === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-3xl mb-2">📋</div>
              <p>No slate data available for tomorrow yet</p>
              <p className="text-xs text-gray-600 mt-1">Lines may not be posted yet</p>
            </div>
          ) : (
            <FullSlateReview date={tomorrowDate} minEv={0} minConfidence={0} />
          )}
        </div>
      </section>

      {/* Quick Links */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link
          to="/props"
          className="p-4 bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 transition-colors group"
        >
          <div className="font-medium text-white group-hover:text-blue-400 transition-colors">All Props</div>
          <div className="text-sm text-gray-400">Browse full prop list</div>
        </Link>
        <Link
          to="/stats"
          className="p-4 bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 transition-colors group"
        >
          <div className="font-medium text-white group-hover:text-blue-400 transition-colors">Stats Dashboard</div>
          <div className="text-sm text-gray-400">Player analytics</div>
        </Link>
        <Link
          to="/parlay"
          className="p-4 bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 transition-colors group"
        >
          <div className="font-medium text-white group-hover:text-blue-400 transition-colors">Parlay Builder</div>
          <div className="text-sm text-gray-400">Build multi-leg bets</div>
        </Link>
        <Link
          to="/my-bets"
          className="p-4 bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 transition-colors group"
        >
          <div className="font-medium text-white group-hover:text-blue-400 transition-colors">My Bets</div>
          <div className="text-sm text-gray-400">Track your wagers</div>
        </Link>
      </div>

      {/* Discord CTA */}
      <div className="bg-gradient-to-r from-indigo-900/50 to-purple-900/50 rounded-lg border border-indigo-700/50 p-6">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-indigo-600/30 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-indigo-400" viewBox="0 0 24 24" fill="currentColor">
                <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
              </svg>
            </div>
            <div>
              <h3 className="font-bold text-white">Join the Community</h3>
              <p className="text-sm text-gray-400">
                Share picks, discuss edges, and get daily board updates
              </p>
            </div>
          </div>
          <a
            href={import.meta.env.VITE_DISCORD_INVITE_URL || 'https://discord.gg/qRMrfn9d'}
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-lg transition-colors whitespace-nowrap"
          >
            Join Discord
          </a>
        </div>
      </div>
    </div>
  );
}

export default TodayDashboard;
