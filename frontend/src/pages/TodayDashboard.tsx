/**
 * TodayDashboard - The primary daily workflow page.
 * 
 * Combines:
 * - Top EV props across selected sports
 * - Hot/Cold players with market context
 * - Win/lose streaks
 * - Tomorrow's slate preview
 * - Quick access to My Bets
 */

import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useSportContext } from '../context/SportContext';
import { usePlayerPropPicks, useColdPlayers, useStreaks, useFullSlate } from '../api/public';
import { HotPlayersPanel } from '../components/HotPlayersPanel';

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
  const { data: propsData, isLoading: propsLoading } = usePlayerPropPicks(sportId, {
    min_ev: 0.03,
    min_confidence: 0.55,
    limit: showAllProps ? 50 : 10,
  });
  
  // Fetch cold players
  const { data: coldPlayers, isLoading: coldLoading } = useColdPlayers(sportId, 3, 5);
  
  // Fetch streaks
  const { data: streaks, isLoading: streaksLoading } = useStreaks(sportId, 3, 10);
  
  // Fetch tomorrow's slate
  const tomorrowDate = useMemo(() => getTomorrowDate(), []);
  const { data: slateData, isLoading: slateLoading } = useFullSlate(tomorrowDate, 0, 0, 20);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Today's Board</h1>
          <p className="text-gray-400 text-sm">
            {sportName} - {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
          </p>
        </div>
        <Link
          to="/props"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
        >
          All Props
        </Link>
      </div>

      <div className="space-y-6">
        {/* Top Row: Best EV Props + Hot Players */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Top EV Props */}
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <div className="p-4 border-b border-gray-700 flex items-center justify-between">
              <div>
                <h2 className="font-bold text-white">Top EV Props</h2>
                <p className="text-xs text-gray-400">Highest expected value picks today</p>
              </div>
              <Link to="/props" className="text-blue-400 text-sm hover:text-blue-300">
                See all
              </Link>
            </div>
            
            <div className="p-4">
              {propsLoading ? (
                <div className="animate-pulse space-y-3">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="h-12 bg-gray-700/50 rounded" />
                  ))}
                </div>
              ) : !propsData?.items?.length ? (
                <div className="text-center py-8 text-gray-500">
                  No high-EV props found. Check back later.
                </div>
              ) : (
                <div className="space-y-2">
                  {propsData.items.slice(0, showAllProps ? 20 : 5).map((pick) => (
                    <div
                      key={pick.pick_id}
                      className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg hover:bg-gray-700/50 transition-colors"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-white">{pick.player_name}</span>
                          <span className="text-xs text-gray-400">{pick.team}</span>
                        </div>
                        <div className="text-sm text-gray-400">
                          {pick.stat_type} {pick.side === 'over' ? 'O' : 'U'} {pick.line}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`font-bold ${pick.expected_value >= 0.05 ? 'text-green-400' : 'text-blue-400'}`}>
                          {formatEv(pick.expected_value)}
                        </div>
                        <div className="text-xs text-gray-400">
                          {formatPct(pick.model_probability)} prob
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {propsData.items.length > 5 && !showAllProps && (
                    <button
                      onClick={() => setShowAllProps(true)}
                      className="w-full py-2 text-sm text-blue-400 hover:text-blue-300"
                    >
                      Show more ({propsData.items.length - 5} more)
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Hot Players Panel */}
          <HotPlayersPanel sportId={sportId} limit={5} />
        </div>

        {/* Second Row: Streaks + Cold Players */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Streaks */}
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <div className="p-4 border-b border-gray-700">
              <h2 className="font-bold text-white">Win Streaks</h2>
              <p className="text-xs text-gray-400">Players on 3+ consecutive hits</p>
            </div>
            
            <div className="p-4">
              {streaksLoading ? (
                <div className="animate-pulse space-y-2">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-10 bg-gray-700/50 rounded" />
                  ))}
                </div>
              ) : !streaks?.hot?.length ? (
                <div className="text-center py-6 text-gray-500 text-sm">
                  No active hot streaks
                </div>
              ) : (
                <div className="space-y-2">
                  {streaks.hot.slice(0, 5).map((player) => (
                    <div
                      key={player.player_id}
                      className="flex items-center justify-between p-2 bg-gray-700/30 rounded"
                    >
                      <span className="text-white">{player.player_name}</span>
                      <span className="text-green-400 font-bold">+{player.streak}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Cold Players */}
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <div className="p-4 border-b border-gray-700">
              <h2 className="font-bold text-white">Cold Players</h2>
              <p className="text-xs text-gray-400">Consider fading these players</p>
            </div>
            
            <div className="p-4">
              {coldLoading ? (
                <div className="animate-pulse space-y-2">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-10 bg-gray-700/50 rounded" />
                  ))}
                </div>
              ) : !coldPlayers?.items?.length ? (
                <div className="text-center py-6 text-gray-500 text-sm">
                  No cold players identified
                </div>
              ) : (
                <div className="space-y-2">
                  {coldPlayers.items.slice(0, 5).map((player) => (
                    <div
                      key={player.player_id}
                      className="flex items-center justify-between p-2 bg-gray-700/30 rounded"
                    >
                      <div>
                        <span className="text-white">{player.player_name}</span>
                        {player.stat_type && (
                          <span className="ml-2 text-xs text-gray-500">
                            {player.stat_type} {player.side?.toUpperCase()}
                          </span>
                        )}
                      </div>
                      <div className="text-right">
                        <span className="text-red-400 font-bold">
                          {(player.hit_rate_7d * 100).toFixed(0)}%
                        </span>
                        <span className="text-xs text-gray-500 ml-1">
                          ({player.hits_7d}/{player.total_7d})
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Tomorrow's Slate Preview */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="p-4 border-b border-gray-700 flex items-center justify-between">
            <div>
              <h2 className="font-bold text-white">Tomorrow's Slate Preview</h2>
              <p className="text-xs text-gray-400">{tomorrowDate}</p>
            </div>
          </div>
          
          <div className="p-4">
            {slateLoading ? (
              <div className="animate-pulse h-20 bg-gray-700/50 rounded" />
            ) : !slateData?.sports?.length ? (
              <div className="text-center py-6 text-gray-500 text-sm">
                No slate data available for tomorrow yet
              </div>
            ) : (
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {slateData.sports.map((sport) => (
                  <div
                    key={sport.sport_id}
                    className="p-3 bg-gray-700/30 rounded-lg"
                  >
                    <div className="font-medium text-white">{sport.sport_name}</div>
                    <div className="text-sm text-gray-400">
                      {sport.props.length} props
                    </div>
                    {sport.props.length > 0 && (
                      <div className="mt-2 text-xs text-green-400">
                        Top EV: {formatEv(sport.props[0]?.expected_value || 0)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick Links */}
        <div className="grid sm:grid-cols-4 gap-4">
          <Link
            to="/props"
            className="p-4 bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 transition-colors"
          >
            <div className="font-medium text-white">All Props</div>
            <div className="text-sm text-gray-400">Browse full list</div>
          </Link>
          <Link
            to="/stats"
            className="p-4 bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 transition-colors"
          >
            <div className="font-medium text-white">Stats</div>
            <div className="text-sm text-gray-400">Detailed analytics</div>
          </Link>
          <Link
            to="/parlay"
            className="p-4 bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 transition-colors"
          >
            <div className="font-medium text-white">Parlay Builder</div>
            <div className="text-sm text-gray-400">Build parlays</div>
          </Link>
          <Link
            to="/my-bets"
            className="p-4 bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 transition-colors"
          >
            <div className="font-medium text-white">My Bets</div>
            <div className="text-sm text-gray-400">Track wagers</div>
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
    </div>
  );
}

export default TodayDashboard;
