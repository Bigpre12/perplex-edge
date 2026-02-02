import { useState, useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useSports, fetchPlayerPropPicks, PlayerPropFilters, PlayerPropPick } from '../api/public';
import { SPORT_CONFIG as BASE_SPORT_CONFIG, getSportConfig } from '../constants/sports';

// =============================================================================
// Live EV Feed - Scrolling list of +EV props across ALL sports
// Auto-refreshes every 30 seconds
// =============================================================================

// Add border classes to sport config for this component
const SPORT_CONFIG = Object.fromEntries(
  Object.entries(BASE_SPORT_CONFIG).map(([id, config]) => [
    id,
    {
      ...config,
      // Override color to include border class for card styling
      color: `${config.color.replace('/30', '/40')} ${config.borderColor || ''}`.trim(),
    },
  ])
);

// Format helpers
const formatPercent = (v: number | null) => v !== null ? `${(v * 100).toFixed(1)}%` : '-';
const formatOdds = (odds: number) => odds > 0 ? `+${odds}` : odds.toString();
const formatTime = (date: Date) => {
  const hours = date.getHours();
  const minutes = date.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  const h = hours % 12 || 12;
  return `${h}:${minutes.toString().padStart(2, '0')} ${ampm}`;
};

// Pick with sport info
interface EnrichedPick extends PlayerPropPick {
  sport_id: number;
  sport_name: string;
}

export function LiveEVFeed() {
  const queryClient = useQueryClient();
  const { data: sportsData, isLoading: sportsLoading } = useSports();
  
  // Filters
  const [minEv, setMinEv] = useState(0.03); // 3% EV default
  const [minConfidence, setMinConfidence] = useState(0.55); // 55% confidence default
  const [selectedSport, setSelectedSport] = useState<number | null>(null); // null = all sports
  const [selectedMarket, setSelectedMarket] = useState<string | null>(null); // null = all markets
  const [isLive, setIsLive] = useState(true); // Auto-refresh toggle
  
  // Last refresh timestamp for display
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  
  // Filters for API
  const filters: PlayerPropFilters = useMemo(() => ({
    min_ev: minEv,
    min_confidence: minConfidence,
    fresh_only: false,
    limit: 100,
  }), [minEv, minConfidence]);
  
  // Get active sports (for filtering)
  const activeSports = useMemo(() => {
    if (!sportsData?.items) return [];
    return sportsData.items;
  }, [sportsData]);
  
  // Fetch props from all sports in parallel
  const feedQuery = useQuery({
    queryKey: ['liveEvFeed', activeSports.map(s => s.id), filters],
    queryFn: async () => {
      if (activeSports.length === 0) return [];
      
      const results = await Promise.all(
        activeSports.map(async (sport) => {
          try {
            const data = await fetchPlayerPropPicks(sport.id, filters);
            return data.items.map(pick => ({
              ...pick,
              sport_id: sport.id,
              sport_name: SPORT_CONFIG[sport.id]?.name || sport.name,
            }));
          } catch (e) {
            console.warn(`[LiveEVFeed] Failed to fetch sport ${sport.id}:`, e);
            return [];
          }
        })
      );
      
      setLastRefresh(new Date());
      return results.flat();
    },
    enabled: activeSports.length > 0,
    staleTime: 30000, // 30 seconds
    refetchInterval: isLive ? 30000 : false, // Auto-refresh every 30s if live
  });
  
  // Extract unique markets for filter dropdown
  const uniqueMarkets = useMemo(() => {
    if (!feedQuery.data) return [];
    const markets = new Set<string>();
    feedQuery.data.forEach(p => markets.add(p.stat_type));
    return Array.from(markets).sort();
  }, [feedQuery.data]);
  
  // Sort and filter picks
  const sortedPicks = useMemo(() => {
    if (!feedQuery.data) return [];
    
    let picks = [...feedQuery.data] as EnrichedPick[];
    
    // Filter by sport if selected
    if (selectedSport !== null) {
      picks = picks.filter(p => p.sport_id === selectedSport);
    }
    
    // Filter by market if selected
    if (selectedMarket !== null) {
      picks = picks.filter(p => p.stat_type === selectedMarket);
    }
    
    // Sort by EV descending
    picks.sort((a, b) => b.expected_value - a.expected_value);
    
    return picks;
  }, [feedQuery.data, selectedSport, selectedMarket]);
  
  // Stats
  const feedStats = useMemo(() => {
    if (sortedPicks.length === 0) return null;
    
    const avgEv = sortedPicks.reduce((sum, p) => sum + p.expected_value, 0) / sortedPicks.length;
    const maxEv = Math.max(...sortedPicks.map(p => p.expected_value));
    const sportBreakdown = new Map<string, number>();
    sortedPicks.forEach(p => {
      sportBreakdown.set(p.sport_name, (sportBreakdown.get(p.sport_name) || 0) + 1);
    });
    
    return { avgEv, maxEv, sportBreakdown };
  }, [sortedPicks]);
  
  // Manual refresh
  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['liveEvFeed'] });
  };
  
  const isLoading = sportsLoading || feedQuery.isLoading;
  
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-white">Live EV Feed</h2>
            <span className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${
              isLive ? 'bg-green-900/50 text-green-400' : 'bg-gray-700 text-gray-400'
            }`}>
              <span className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-400 animate-pulse' : 'bg-gray-500'}`} />
              {isLive ? 'LIVE' : 'PAUSED'}
            </span>
          </div>
          <p className="text-sm text-gray-400 mt-1">
            Top +EV props across all sports • Auto-refreshes every 30 seconds
          </p>
        </div>
        
        {/* Refresh controls */}
        <div className="flex items-center gap-4">
          <div className="text-xs text-gray-500">
            Updated: {formatTime(lastRefresh)}
          </div>
          <button
            onClick={handleRefresh}
            disabled={feedQuery.isFetching}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors disabled:opacity-50"
            title="Refresh now"
          >
            <svg className={`w-5 h-5 ${feedQuery.isFetching ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          <button
            onClick={() => setIsLive(!isLive)}
            className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
              isLive 
                ? 'bg-green-600 hover:bg-green-700 text-white' 
                : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
            }`}
          >
            {isLive ? 'Pause' : 'Resume'}
          </button>
        </div>
      </div>
      
      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex flex-wrap gap-4 items-end">
          {/* Sport Filter */}
          <div>
            <label className="block text-xs text-gray-400 mb-1">Sport</label>
            <select
              value={selectedSport ?? 'all'}
              onChange={(e) => setSelectedSport(e.target.value === 'all' ? null : Number(e.target.value))}
              className="bg-gray-700 text-white rounded px-3 py-1.5 text-sm border border-gray-600 min-w-[120px]"
            >
              <option value="all">All Sports</option>
              {activeSports.map(s => {
                const config = SPORT_CONFIG[s.id];
                return (
                  <option key={s.id} value={s.id}>
                    {config?.icon} {config?.name || s.name}
                  </option>
                );
              })}
            </select>
          </div>
          
          {/* Market Filter */}
          <div>
            <label className="block text-xs text-gray-400 mb-1">Market</label>
            <select
              value={selectedMarket ?? 'all'}
              onChange={(e) => setSelectedMarket(e.target.value === 'all' ? null : e.target.value)}
              className="bg-gray-700 text-white rounded px-3 py-1.5 text-sm border border-gray-600 min-w-[120px]"
            >
              <option value="all">All Markets</option>
              {uniqueMarkets.map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>
          
          {/* Min EV */}
          <div className="min-w-[140px]">
            <label className="block text-xs text-gray-400 mb-1">
              Min EV: <span className="text-green-400">{(minEv * 100).toFixed(0)}%+</span>
            </label>
            <input
              type="range"
              min="0"
              max="0.15"
              step="0.01"
              value={minEv}
              onChange={(e) => setMinEv(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-green-500"
            />
          </div>
          
          {/* Min Confidence */}
          <div className="min-w-[140px]">
            <label className="block text-xs text-gray-400 mb-1">
              Min Conf: <span className="text-blue-400">{(minConfidence * 100).toFixed(0)}%+</span>
            </label>
            <input
              type="range"
              min="0.5"
              max="0.75"
              step="0.05"
              value={minConfidence}
              onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>
        </div>
      </div>
      
      {/* Stats Bar */}
      {feedStats && sortedPicks.length > 0 && (
        <div className="bg-gradient-to-r from-green-900/20 to-blue-900/20 border border-green-700/30 rounded-lg px-4 py-3">
          <div className="flex flex-wrap items-center gap-6 text-sm">
            <div>
              <span className="text-gray-400">Props:</span>
              <span className="ml-2 text-white font-bold">{sortedPicks.length}</span>
            </div>
            <div>
              <span className="text-gray-400">Best EV:</span>
              <span className="ml-2 text-green-400 font-bold">+{formatPercent(feedStats.maxEv)}</span>
            </div>
            <div>
              <span className="text-gray-400">Avg EV:</span>
              <span className="ml-2 text-green-400">+{formatPercent(feedStats.avgEv)}</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              {Array.from(feedStats.sportBreakdown.entries()).map(([sport, count]) => (
                <span key={sport} className="px-2 py-0.5 bg-gray-700/80 rounded text-gray-300">
                  {sport}: {count}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin h-8 w-8 border-2 border-green-500 border-t-transparent rounded-full" />
        </div>
      )}
      
      {/* Feed List */}
      {!isLoading && sortedPicks.length > 0 && (
        <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
          {sortedPicks.map((pick, idx) => {
            const sportConfig = SPORT_CONFIG[pick.sport_id] || { 
              icon: '🎮', 
              color: 'bg-gray-800 border-gray-700 text-gray-300' 
            };
            const gameTime = new Date(pick.game_start_time);
            
            return (
              <div
                key={`${pick.sport_id}-${pick.pick_id}-${idx}`}
                className="bg-gray-800 border border-gray-700 rounded-lg p-3 hover:border-gray-600 transition-colors"
              >
                <div className="flex items-center justify-between gap-4">
                  {/* Left: Sport badge + Player info */}
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    {/* Sport badge */}
                    <span className={`px-2 py-1 rounded text-xs font-medium border ${sportConfig.color}`}>
                      {sportConfig.icon}
                    </span>
                    
                    {/* Player + Prop */}
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-white font-medium truncate">{pick.player_name}</span>
                        <span className="text-xs text-gray-500">
                          {pick.team_abbr || pick.team} vs {pick.opponent_abbr || pick.opponent_team}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-gray-400">{pick.stat_type}</span>
                        <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${
                          pick.side === 'over' ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'
                        }`}>
                          {pick.side.toUpperCase()} {pick.line}
                        </span>
                        <span className="text-gray-500">{formatOdds(pick.odds)}</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Right: EV + Game time */}
                  <div className="flex items-center gap-4 text-right">
                    {/* EV */}
                    <div>
                      <div className="text-green-400 font-bold text-lg">
                        +{formatPercent(pick.expected_value)}
                      </div>
                      <div className="text-xs text-gray-500">
                        {formatPercent(pick.model_probability)} conf
                      </div>
                    </div>
                    
                    {/* Game time */}
                    <div className="text-xs text-gray-500 w-16 text-right">
                      {formatTime(gameTime)}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {/* Empty State */}
      {!isLoading && sortedPicks.length === 0 && (
        <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
          <div className="text-4xl mb-3">📊</div>
          <p className="text-gray-400 text-lg">No +EV props found</p>
          <p className="text-sm text-gray-500 mt-2">
            {feedQuery.data && feedQuery.data.length > 0
              ? `${feedQuery.data.length} props available but filtered out`
              : 'Check back later for new opportunities'}
          </p>
          <button
            onClick={() => {
              setMinEv(0);
              setMinConfidence(0.5);
              setSelectedSport(null);
              setSelectedMarket(null);
            }}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg"
          >
            Reset Filters
          </button>
        </div>
      )}
    </div>
  );
}
