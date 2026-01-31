import { useState, useMemo, useEffect } from 'react';
import { usePlayerPropPicks, STAT_TYPE_OPTIONS, PlayerPropFilters, BookLine } from '../api/public';
import { useSportContext } from '../context/SportContext';
import { ConfidenceBadge } from './ConfidenceBadge';

// Component to show per-book line comparison
function BookLinesPopover({ bookLines, bestBook }: { bookLines: BookLine[] | null; bestBook: string | null }) {
  const [isOpen, setIsOpen] = useState(false);
  
  if (!bookLines || bookLines.length === 0) {
    return <span className="text-gray-500">-</span>;
  }
  
  const formatOdds = (odds: number) => (odds > 0 ? `+${odds}` : odds.toString());
  const formatEv = (ev: number | null) => ev !== null ? `${(ev * 100).toFixed(1)}%` : '-';
  
  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="text-blue-400 hover:text-blue-300 underline text-xs"
      >
        {bookLines.length} book{bookLines.length > 1 ? 's' : ''}
      </button>
      
      {isOpen && (
        <div className="absolute z-50 right-0 mt-1 bg-gray-900 border border-gray-600 rounded-lg shadow-xl p-3 min-w-[280px]">
          <div className="text-xs text-gray-400 mb-2 font-medium">Sportsbook Comparison</div>
          <table className="w-full text-xs">
            <thead>
              <tr className="text-gray-500">
                <th className="text-left pb-1">Book</th>
                <th className="text-right pb-1">Line</th>
                <th className="text-right pb-1">Odds</th>
                <th className="text-right pb-1">EV</th>
              </tr>
            </thead>
            <tbody>
              {bookLines.map((bl, idx) => (
                <tr 
                  key={idx} 
                  className={bl.sportsbook === bestBook ? 'text-green-400' : 'text-gray-300'}
                >
                  <td className="py-0.5">
                    {bl.sportsbook}
                    {bl.sportsbook === bestBook && (
                      <span className="ml-1 text-green-500">★</span>
                    )}
                  </td>
                  <td className="text-right py-0.5">{bl.line ?? '-'}</td>
                  <td className="text-right py-0.5">{formatOdds(bl.odds)}</td>
                  <td className={`text-right py-0.5 ${(bl.ev ?? 0) > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {formatEv(bl.ev)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button
            onClick={() => setIsOpen(false)}
            className="mt-2 text-xs text-gray-500 hover:text-gray-400"
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}

// Badge for line variance (off-market indicator)
function LineVarianceBadge({ variance }: { variance: number | null }) {
  if (variance === null || variance === 0) {
    return null;
  }
  
  // Green if tight (< 0.5), Yellow if moderate (0.5-1.0), Red if high (> 1.0)
  const colorClass = variance < 0.5 
    ? 'bg-green-900/50 text-green-400' 
    : variance < 1.0 
      ? 'bg-yellow-900/50 text-yellow-400' 
      : 'bg-red-900/50 text-red-400';
  
  return (
    <span className={`ml-1 text-xs px-1 py-0.5 rounded ${colorClass}`} title="Line variance across books">
      ±{variance}
    </span>
  );
}

export function PlayerPropsTab() {
  const { sportId, isLoading: sportLoading } = useSportContext();

  // Filter state
  const [statType, setStatType] = useState<string>('');
  const [minConfidence, setMinConfidence] = useState<number>(0);
  const [minEv, setMinEv] = useState<number>(0);

  // Build filters object
  const filters: PlayerPropFilters = useMemo(
    () => ({
      stat_type: statType || undefined,
      min_confidence: minConfidence > 0 ? minConfidence : undefined,
      min_ev: minEv > 0 ? minEv : undefined,
      fresh_only: true,  // Only show picks for games that haven't started
      limit: 100,
    }),
    [statType, minConfidence, minEv]
  );

  // Fetch data with React Query
  const { data, isLoading, error, isFetching } = usePlayerPropPicks(sportId, filters);

  // Debug logging
  useEffect(() => {
    console.log('[PlayerPropsTab] State:', { 
      sportId, 
      sportLoading, 
      dataTotal: data?.total, 
      itemCount: data?.items?.length,
      isLoading,
      error: error?.message 
    });
  }, [sportId, sportLoading, data, isLoading, error]);

  // Format helpers
  const formatOdds = (odds: number) => (odds > 0 ? `+${odds}` : odds.toString());
  const formatPercent = (value: number | null) =>
    value !== null ? `${(value * 100).toFixed(1)}%` : '-';
  const formatTime = (iso: string) => {
    const date = new Date(iso);
    return date.toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex flex-wrap gap-6 items-end">
          {/* Stat Type Dropdown */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Stat Type</label>
            <select
              value={statType}
              onChange={(e) => setStatType(e.target.value)}
              className="bg-gray-700 text-white rounded px-3 py-2 border border-gray-600 
                       hover:border-gray-500 focus:border-blue-500 focus:outline-none min-w-[160px]"
            >
              {STAT_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Min Confidence Slider */}
          <div className="flex-1 min-w-[200px] max-w-[300px]">
            <label className="block text-sm text-gray-400 mb-1">
              Min Confidence: <span className="text-white font-medium">{(minConfidence * 100).toFixed(0)}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={minConfidence}
              onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer
                       accent-blue-500"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>

          {/* Min EV Input */}
          <div className="min-w-[140px]">
            <label className="block text-sm text-gray-400 mb-1">
              Min EV: <span className="text-white font-medium">{(minEv * 100).toFixed(0)}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="0.2"
              step="0.01"
              value={minEv}
              onChange={(e) => setMinEv(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer
                       accent-blue-500"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0%</span>
              <span>10%</span>
              <span>20%</span>
            </div>
          </div>

          {/* Results count */}
          <div className="text-sm text-gray-400">
            {isFetching && <span className="animate-pulse">Updating...</span>}
            {data && !isFetching && (
              <span>
                <span className="text-white font-medium">{data.total}</span> picks found
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-4 text-red-400">
          Failed to load player prop picks. Please try again.
        </div>
      )}

      {/* Data Table */}
      {data && data.items.length > 0 && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-900 text-gray-400 text-xs uppercase">
                <tr>
                  <th className="px-3 py-3 text-left">Player</th>
                  <th className="px-3 py-3 text-left">Team</th>
                  <th className="px-3 py-3 text-left">Opponent</th>
                  <th className="px-3 py-3 text-left">Stat</th>
                  <th className="px-3 py-3 text-right">Line</th>
                  <th className="px-3 py-3 text-center">Side</th>
                  <th className="px-3 py-3 text-right">Odds</th>
                  <th className="px-3 py-3 text-center">Books</th>
                  <th className="px-3 py-3 text-right">Model</th>
                  <th className="px-3 py-3 text-right">Implied</th>
                  <th className="px-3 py-3 text-right">EV</th>
                  <th className="px-3 py-3 text-right">Hit 10g</th>
                  <th className="px-3 py-3 text-center">Confidence</th>
                  <th className="px-3 py-3 text-left">Start Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {data.items.map((pick) => (
                  <tr
                    key={pick.pick_id}
                    className="hover:bg-gray-700/50 transition-colors"
                  >
                    <td className="px-3 py-3 text-white font-medium">{pick.player_name}</td>
                    <td className="px-3 py-3 text-gray-300">
                      {pick.team_abbr || pick.team}
                    </td>
                    <td className="px-3 py-3 text-gray-400">
                      vs {pick.opponent_abbr || pick.opponent_team}
                    </td>
                    <td className="px-3 py-3">
                      <span className="bg-blue-900/50 text-blue-400 text-xs px-2 py-0.5 rounded">
                        {pick.stat_type}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-right text-white font-medium">
                      {pick.line}
                      <LineVarianceBadge variance={pick.line_variance} />
                    </td>
                    <td className="px-3 py-3 text-center">
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-medium ${
                          pick.side === 'over'
                            ? 'bg-green-900/50 text-green-400'
                            : 'bg-red-900/50 text-red-400'
                        }`}
                      >
                        {pick.side.toUpperCase()}
                      </span>
                    </td>
                    <td
                      className={`px-3 py-3 text-right font-medium ${
                        pick.odds > 0 ? 'text-green-400' : 'text-white'
                      }`}
                    >
                      {formatOdds(pick.odds)}
                    </td>
                    <td className="px-3 py-3 text-center">
                      <BookLinesPopover bookLines={pick.book_lines} bestBook={pick.best_book} />
                    </td>
                    <td className="px-3 py-3 text-right text-green-400">
                      {formatPercent(pick.model_probability)}
                    </td>
                    <td className="px-3 py-3 text-right text-gray-400">
                      {formatPercent(pick.implied_probability)}
                    </td>
                    <td
                      className={`px-3 py-3 text-right font-medium ${
                        pick.expected_value > 0 ? 'text-green-400' : 'text-red-400'
                      }`}
                    >
                      {formatPercent(pick.expected_value)}
                    </td>
                    <td className="px-3 py-3 text-right text-gray-300">
                      {formatPercent(pick.hit_rate_10g)}
                    </td>
                    <td className="px-3 py-3 text-center">
                      <ConfidenceBadge score={pick.confidence_score} />
                    </td>
                    <td className="px-3 py-3 text-gray-400 text-xs">
                      {formatTime(pick.game_start_time)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty State */}
      {data && data.items.length === 0 && (
        <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
          <p className="text-gray-400">No player prop picks found</p>
          <p className="text-sm text-gray-500 mt-2">
            Try adjusting your filters or check back later for new picks
          </p>
        </div>
      )}
    </div>
  );
}
