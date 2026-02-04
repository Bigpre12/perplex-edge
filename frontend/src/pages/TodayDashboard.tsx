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
      </div>
    </div>
  );
}

export default TodayDashboard;
