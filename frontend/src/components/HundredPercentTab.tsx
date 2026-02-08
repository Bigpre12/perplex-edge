import { useState } from 'react';
import { use100PercentProps, HundredPercentProp } from '../api/public';
import { useSportContext } from '../context/SportContext';
import { ConfidenceBadge } from './ConfidenceBadge';
import { DEFAULT_100PCT_FILTERS, METRIC_EXPLAINERS } from '../constants/presets';

// Window selector buttons
const WINDOW_OPTIONS = [
  { value: 'last_5', label: 'Last 5 Games', short: 'L5' },
  { value: 'last_10', label: 'Last 10 Games', short: 'L10' },
  { value: 'season', label: 'Season', short: 'SZN' },
];

// Badge showing 100% status
function PerfectBadge({ is100: isHundred, games }: { is100: boolean; games: number }) {
  if (!isHundred || games < 3) {
    return null;
  }
  
  return (
    <span className="ml-1 px-1.5 py-0.5 text-xs font-bold bg-green-500 text-white rounded">
      100% ({games}g)
    </span>
  );
}

// Hit rate bar visualization
function HitRateBar({ rate, games }: { rate: number | null; games: number }) {
  if (rate === null || games === 0) {
    return <span className="text-gray-500">-</span>;
  }
  
  const percentage = Math.round(rate * 100);
  const width = Math.min(100, percentage);
  const colorClass = percentage >= 100 
    ? 'bg-green-500' 
    : percentage >= 80 
    ? 'bg-green-600' 
    : percentage >= 60 
    ? 'bg-yellow-500' 
    : 'bg-red-500';
  
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
        <div 
          className={`h-full ${colorClass}`} 
          style={{ width: `${width}%` }}
        />
      </div>
      <span className={`text-xs font-medium ${percentage === 100 ? 'text-green-400' : 'text-gray-300'}`}>
        {percentage}%
      </span>
      <span className="text-xs text-gray-500">({games}g)</span>
    </div>
  );
}

export function HundredPercentTab() {
  const { sportId, isLoading: sportLoading } = useSportContext();
  const [window, setWindow] = useState(DEFAULT_100PCT_FILTERS.window);
  
  // Reset to default filters
  const resetToDefault = () => {
    setWindow(DEFAULT_100PCT_FILTERS.window);
  };
  
  // Fetch 100% hit rate props
  const queryResult = use100PercentProps(sportId, window, 50);
  const { data, isLoading, error, isFetching, status, fetchStatus } = queryResult;
  
  // CRITICAL: Derive display state with explicit null checks
  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  
  // Simple state machine:
  // 1. isLoading=true → show spinner (initial fetch, no cache)
  // 2. isLoading=false + error → show error
  // 3. isLoading=false + no error + items.length=0 → show empty state
  // 4. isLoading=false + no error + items.length>0 → show data
  const showSpinner = isLoading;
  const showError = !isLoading && !!error;
  const showEmpty = !isLoading && !error && items.length === 0;
  const showData = !isLoading && !error && items.length > 0;
  
  // Debug logging - log every render to help diagnose
  if (import.meta.env.DEV) console.log('[HundredPercentTab] Render:', {
    sportId,
    window,
    status,
    fetchStatus,
    isLoading,
    isFetching,
    error: error?.message ?? null,
    dataExists: !!data,
    itemCount: items.length,
    total,
    // What we'll show
    showSpinner,
    showError,
    showEmpty,
    showData,
  });
  
  // Format odds
  const formatOdds = (odds: number) => (odds > 0 ? `+${odds}` : odds.toString());
  
  // Format time (handles null/undefined)
  const formatTime = (dateStr: string | null | undefined) => {
    if (!dateStr) return 'TBD';
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return 'TBD';
      return date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        timeZoneName: 'short'
      });
    } catch {
      return 'TBD';
    }
  };
  
  
  if (sportLoading || !sportId) {
    return (
      <div className="p-8 text-center text-gray-400">
        Loading sports...
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      {/* Header with window selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">
            High Hit Rate Props
            <span 
              className="ml-2 text-sm text-gray-500 cursor-help" 
              title={METRIC_EXPLAINERS.hitRate.long}
            >
              ⓘ
            </span>
          </h2>
          <p className="text-sm text-gray-400">
            Props with the highest hit rates - 100% when available, 80%+ otherwise.
            <span className="text-gray-500 ml-1">({METRIC_EXPLAINERS.hitRate.example})</span>
          </p>
        </div>
        
        {/* Window selector + Reset */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">Window:</span>
            <div className="flex bg-gray-800 rounded-lg p-1">
              {WINDOW_OPTIONS.map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setWindow(opt.value)}
                  className={`px-3 py-1.5 text-sm font-medium rounded transition-colors ${
                    window === opt.value
                      ? 'bg-green-600 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-gray-700'
                  }`}
                >
                  {opt.short}
                </button>
              ))}
            </div>
          </div>
          <button
            onClick={resetToDefault}
            className="px-3 py-1.5 text-sm text-gray-400 hover:text-white border border-gray-600 rounded-lg hover:border-gray-500 transition-colors"
            title="Reset to default (Last 5 games)"
          >
            ↺ Reset
          </button>
        </div>
      </div>
      
      {/* Loading state - spinner during initial fetch */}
      {showSpinner && (
        <div className="p-8 text-center text-gray-400">
          <div className="animate-spin inline-block w-6 h-6 border-2 border-gray-400 border-t-transparent rounded-full mr-2" />
          Finding high hit rate props...
        </div>
      )}
      
      {/* Refetching indicator - subtle indicator when refreshing with existing data */}
      {isFetching && !isLoading && (
        <div className="text-center text-sm text-gray-500 py-1">
          <span className="animate-pulse">Refreshing...</span>
        </div>
      )}
      
      {/* Error state */}
      {showError && (
        <div className="p-8 text-center text-red-400">
          <div className="text-2xl mb-2">⚠️</div>
          <div>Error loading props: {error?.message ?? 'Unknown error'}</div>
          <div className="text-sm text-gray-500 mt-2">
            Check browser console for details
          </div>
        </div>
      )}
      
      {/* Empty state - distinguish "no props loaded" vs "no high hit rate props" */}
      {showEmpty && (
        <div className="p-8 text-center">
          {total === 0 ? (
            // No props loaded for this sport at all
            <>
              <div className="text-5xl mb-4">📭</div>
              <div className="text-gray-400 text-lg">No props loaded for this sport</div>
              <div className="text-gray-500 text-sm mt-2">
                Check back closer to game time or try another sport
              </div>
            </>
          ) : (
            // Props exist but none meet the hit rate threshold
            <>
              <div className="text-5xl mb-4">🎯</div>
              <div className="text-gray-400 text-lg">No high hit rate props found</div>
              <div className="text-gray-500 text-sm mt-2">
                No props with 70%+ hit rates available. Try a different time window or check back later.
              </div>
            </>
          )}
        </div>
      )}
      
      {/* Props table - only show when we have actual data */}
      {showData && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-800/50 text-gray-400 text-xs uppercase">
              <tr>
                <th className="px-3 py-3 text-left">Player</th>
                <th className="px-3 py-3 text-left">Stat</th>
                <th className="px-3 py-3 text-center">Line</th>
                <th className="px-3 py-3 text-center">Side</th>
                <th className="px-3 py-3 text-right">Odds</th>
                <th className="px-3 py-3 text-center">L5 Rate</th>
                <th className="px-3 py-3 text-center">L10 Rate</th>
                <th className="px-3 py-3 text-center">Season</th>
                <th className="px-3 py-3 text-right">Model</th>
                <th className="px-3 py-3 text-right">EV</th>
                <th className="px-3 py-3 text-left">Game</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {items.map((prop: HundredPercentProp) => (
                <tr 
                  key={prop.pick_id} 
                  className="hover:bg-gray-700/50 transition-colors"
                >
                  {/* Player */}
                  <td className="px-3 py-3">
                    <div className="font-medium text-white">{prop.player_name}</div>
                    <div className="text-xs text-gray-500">
                      {prop.team_abbr || prop.team}
                    </div>
                  </td>
                  
                  {/* Stat Type */}
                  <td className="px-3 py-3 text-gray-300">
                    {prop.stat_type.replace('player_', '').replace(/_/g, ' ').toUpperCase()}
                  </td>
                  
                  {/* Line */}
                  <td className="px-3 py-3 text-center text-white font-medium">
                    {prop.line}
                  </td>
                  
                  {/* Side */}
                  <td className="px-3 py-3 text-center">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      prop.side === 'over' 
                        ? 'bg-green-900/50 text-green-400' 
                        : 'bg-red-900/50 text-red-400'
                    }`}>
                      {prop.side.toUpperCase()}
                    </span>
                  </td>
                  
                  {/* Odds */}
                  <td className="px-3 py-3 text-right text-white">
                    {formatOdds(prop.odds)}
                  </td>
                  
                  {/* Last 5 Hit Rate */}
                  <td className="px-3 py-3 text-center">
                    <HitRateBar rate={prop.hit_rate_last_5} games={prop.games_last_5} />
                    <PerfectBadge is100={prop.is_100_last_5} games={prop.games_last_5} />
                  </td>
                  
                  {/* Last 10 Hit Rate */}
                  <td className="px-3 py-3 text-center">
                    <HitRateBar rate={prop.hit_rate_last_10} games={prop.games_last_10} />
                    <PerfectBadge is100={prop.is_100_last_10} games={prop.games_last_10} />
                  </td>
                  
                  {/* Season Hit Rate */}
                  <td className="px-3 py-3 text-center">
                    <HitRateBar rate={prop.hit_rate_season} games={prop.games_season} />
                    <PerfectBadge is100={prop.is_100_season} games={prop.games_season} />
                  </td>
                  
                  {/* Model Probability */}
                  <td className="px-3 py-3 text-right">
                    <ConfidenceBadge score={prop.model_probability} />
                  </td>
                  
                  {/* EV */}
                  <td className={`px-3 py-3 text-right font-medium ${
                    prop.expected_value > 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {prop.expected_value > 0 ? '+' : ''}{(prop.expected_value * 100).toFixed(1)}%
                  </td>
                  
                  {/* Game Info */}
                  <td className="px-3 py-3">
                    <div className="text-xs text-gray-400">
                      vs {prop.opponent_abbr || prop.opponent_team}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatTime(prop.game_start_time)}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Summary */}
      {showData && (
        <div className="text-center text-sm text-gray-500 py-2">
          Showing {items.length} of {total || items.length} high hit rate props ({WINDOW_OPTIONS.find(o => o.value === window)?.label})
        </div>
      )}
    </div>
  );
}

export default HundredPercentTab;
