/**
 * HotPlayersPanel - Table view of hot players for dense comparison.
 * 
 * Shows each player's best-performing market (stat_type + side) with
 * columns for rank, player, market, record, hit rate, and streak.
 * 
 * Designed for "power users" who want to compare multiple players at once.
 */

import { useHotPlayers } from '../api/public';

// Stat type display labels
const STAT_LABELS: Record<string, string> = {
  PTS: 'Points',
  REB: 'Rebounds',
  AST: 'Assists',
  PRA: 'PRA',
  '3PM': '3PM',
  'P+R': 'Pts+Reb',
  'P+A': 'Pts+Ast',
  'R+A': 'Reb+Ast',
  STL: 'Steals',
  BLK: 'Blocks',
  TO: 'Turnovers',
};

interface HotPlayersPanelProps {
  sportId: number | null;
  limit?: number;
}

export function HotPlayersPanel({ sportId, limit = 15 }: HotPlayersPanelProps) {
  const { data: hotPlayers, isLoading } = useHotPlayers(sportId, 3, limit);

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
        <h3 className="font-bold text-white">Hot Players Table</h3>
        <p className="text-xs text-gray-400">
          Best-performing market per player over the last 7 days
        </p>
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
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default HotPlayersPanel;
