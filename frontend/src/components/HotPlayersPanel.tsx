/**
 * HotPlayersPanel - Table view of hot players for dense comparison.
 * 
 * Shows each player's best-performing market (stat_type + side) with
 * columns for rank, player, market, record, hit rate, and streak.
 * 
 * Designed for "power users" who want to compare multiple players at once.
 * Clicking a row navigates to Player Props tab with filters pre-applied.
 */

import { useState } from 'react';
import { useHotPlayers } from '../api/public';

// Stat type display labels
const STAT_LABELS: Record<string, string> = {
  PTS: 'Points',
  REB: 'Rebounds',
  AST: 'Assists',
  PRA: 'PRA',
  'P+R': 'Pts+Reb',
  'P+A': 'Pts+Ast',
  'R+A': 'Reb+Ast',
  TO: 'Turnovers',
};

// Available markets for filter dropdown
const MARKET_OPTIONS = [
  { value: '', label: 'All Markets' },
  { value: 'PTS', label: 'Points' },
  { value: 'REB', label: 'Rebounds' },
  { value: 'AST', label: 'Assists' },
  { value: 'PRA', label: 'PRA' },
];

// Trust tag styling
const TRUST_TAG_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  strong: { bg: 'bg-emerald-900/50', text: 'text-emerald-400', label: 'Strong' },
  ok: { bg: 'bg-blue-900/50', text: 'text-blue-400', label: 'OK' },
  thin: { bg: 'bg-amber-900/50', text: 'text-amber-400', label: 'Thin' },
  weak: { bg: 'bg-gray-800', text: 'text-gray-400', label: 'Weak' },
};

interface HotPlayersPanelProps {
  sportId: number | null;
  limit?: number;
  onViewProps?: (playerId: number, market?: string, side?: string) => void;
}

export function HotPlayersPanel({ sportId, limit = 15, onViewProps }: HotPlayersPanelProps) {
  // Filter state
  const [marketFilter, setMarketFilter] = useState<string>('');
  const [sideFilter, setSideFilter] = useState<string>('');
  const [minPicks, setMinPicks] = useState<number>(3);

  // Pass filters to hook
  const { data: hotPlayers, isLoading } = useHotPlayers(
    sportId,
    minPicks,
    limit,
    true,  // includeMarket
    marketFilter || undefined,
    sideFilter || undefined
  );

  // Navigate to Props tab with filters
  const handleViewProps = (playerId: number, market?: string | null, side?: string | null) => {
    if (onViewProps) {
      onViewProps(playerId, market ?? undefined, side ?? undefined);
    } else {
      // Fallback: Update URL params to trigger navigation
      const params = new URLSearchParams(window.location.search);
      params.set('tab', 'props');
      if (sportId) params.set('sportId', sportId.toString());
      params.set('playerId', playerId.toString());
      if (market) params.set('market', market);
      if (side) params.set('side', side);
      window.history.pushState({}, '', `?${params.toString()}`);
      window.dispatchEvent(new PopStateEvent('popstate'));
    }
  };

  // Format hit rate percentage
  const formatHitRate = (rate: number) => {
    // Rate comes as decimal (0-1), convert to percentage
    const pct = rate <= 1 ? rate * 100 : rate;
    return `${pct.toFixed(1)}%`;
  };

  // Format streak with + prefix for positive
  const formatStreak = (streak: number) => {
    if (streak > 0) return `+${streak}`;
    return streak.toString();
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="bg-gray-800/30 rounded-lg p-4">
        <h3 className="font-bold text-white mb-4">Hot Players Table</h3>
        <div className="animate-pulse space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-10 bg-gray-700/50 rounded" />
          ))}
        </div>
      </div>
    );
  }

  // Empty state
  if (!hotPlayers?.items || hotPlayers.items.length === 0) {
    return (
      <div className="bg-gray-800/30 rounded-lg p-4">
        <h3 className="font-bold text-white mb-4">Hot Players Table</h3>
        <div className="text-gray-500 text-center py-8">
          No hot players in the last 7 days. Results will appear after games settle.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800/30 rounded-lg overflow-hidden">
      <div className="p-4 border-b border-gray-700">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h3 className="font-bold text-white">Hot Players Table</h3>
            <p className="text-xs text-gray-400">
              Best-performing market per player over the last 7 days
            </p>
          </div>
          
          {/* Filter controls */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Market dropdown */}
            <select
              value={marketFilter}
              onChange={(e) => setMarketFilter(e.target.value)}
              className="px-2 py-1 text-xs bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {MARKET_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
            
            {/* Side toggle */}
            <div className="flex rounded overflow-hidden border border-gray-600">
              {['', 'over', 'under'].map((s) => (
                <button
                  key={s}
                  onClick={() => setSideFilter(s)}
                  className={`px-2 py-1 text-xs transition-colors ${
                    sideFilter === s
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {s === '' ? 'All' : s === 'over' ? 'Over' : 'Under'}
                </button>
              ))}
            </div>
            
            {/* Min picks */}
            <div className="flex items-center gap-1">
              <span className="text-xs text-gray-400">Min:</span>
              <select
                value={minPicks}
                onChange={(e) => setMinPicks(parseInt(e.target.value, 10))}
                className="px-1 py-1 text-xs bg-gray-700 border border-gray-600 rounded text-white focus:outline-none"
              >
                <option value={3}>3+</option>
                <option value={5}>5+</option>
                <option value={10}>10+</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-800/50">
            <tr>
              <th className="text-left py-2 px-4 text-xs text-gray-400 font-medium w-10">#</th>
              <th className="text-left py-2 px-4 text-xs text-gray-400 font-medium">Player</th>
              <th className="text-left py-2 px-4 text-xs text-gray-400 font-medium">Market</th>
              <th className="text-center py-2 px-4 text-xs text-gray-400 font-medium">Record</th>
              <th className="text-center py-2 px-4 text-xs text-gray-400 font-medium">Hit %</th>
              <th className="text-center py-2 px-4 text-xs text-gray-400 font-medium">Streak</th>
              <th className="text-center py-2 px-4 text-xs text-gray-400 font-medium">Trust</th>
              <th className="text-center py-2 px-4 text-xs text-gray-400 font-medium w-20"></th>
            </tr>
          </thead>
          <tbody>
            {hotPlayers.items.map((player, idx) => (
              <tr
                key={`${player.player_id}-${player.stat_type}-${player.side}`}
                className="border-b border-gray-700/50 hover:bg-gray-800/30 transition-colors"
              >
                {/* Rank */}
                <td className="py-3 px-4">
                  <span className={`font-bold ${idx < 3 ? 'text-orange-400' : 'text-gray-500'}`}>
                    {idx + 1}
                  </span>
                </td>

                {/* Player Name */}
                <td className="py-3 px-4">
                  <span className="text-white font-medium">{player.player_name}</span>
                </td>

                {/* Market (stat_type + side badge) */}
                <td className="py-3 px-4">
                  {player.stat_type && player.side ? (
                    <span className="inline-flex items-center gap-2">
                      <span className="text-gray-200">
                        {STAT_LABELS[player.stat_type] ?? player.stat_type}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          player.side === 'over'
                            ? 'bg-emerald-900 text-emerald-300'
                            : 'bg-red-900 text-red-300'
                        }`}
                      >
                        {player.side === 'over' ? 'OVER' : 'UNDER'}
                      </span>
                    </span>
                  ) : (
                    <span className="text-gray-500">-</span>
                  )}
                </td>

                {/* Record */}
                <td className="py-3 px-4 text-center text-gray-300">
                  {player.hits_7d}/{player.total_7d} picks
                </td>

                {/* Hit Rate */}
                <td className="py-3 px-4 text-center">
                  <span className="text-green-400 font-medium">
                    {formatHitRate(player.hit_rate_7d)}
                  </span>
                </td>

                {/* Streak */}
                <td className="py-3 px-4 text-center">
                  <span
                    className={`font-medium ${
                      player.current_streak > 0 ? 'text-green-400' : 'text-red-400'
                    }`}
                  >
                    {formatStreak(player.current_streak)}
                  </span>
                </td>

                {/* Trust Tag */}
                <td className="py-3 px-4 text-center">
                  {player.trust_tag && (
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                        TRUST_TAG_STYLES[player.trust_tag]?.bg || 'bg-gray-800'
                      } ${TRUST_TAG_STYLES[player.trust_tag]?.text || 'text-gray-400'}`}
                      title={`Sample size: ${player.total_7d} picks`}
                    >
                      {TRUST_TAG_STYLES[player.trust_tag]?.label || player.trust_tag}
                    </span>
                  )}
                </td>

                {/* View Props Action */}
                <td className="py-3 px-4 text-center">
                  <button
                    onClick={() => handleViewProps(player.player_id, player.stat_type, player.side)}
                    className="px-2 py-1 text-xs bg-blue-600 hover:bg-blue-500 text-white rounded transition-colors"
                    title="View live props for this player"
                  >
                    Props
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default HotPlayersPanel;
