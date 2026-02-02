import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSports, fetchPlayerPropPicks, PlayerPropFilters } from '../api/public';
import { TonightDashboard } from './TonightDashboard';

// ============================================================================
// Multi-Sport Slate View
// Shows top picks across ALL sports sorted by EV for cross-sport DFS building
// ============================================================================

// Sport display names and icons
const SPORT_CONFIG: Record<number, { name: string; icon: string; color: string }> = {
  30: { name: 'NBA', icon: '🏀', color: 'bg-orange-900/30 text-orange-400' },
  31: { name: 'NFL', icon: '🏈', color: 'bg-green-900/30 text-green-400' },
  32: { name: 'NCAAB', icon: '🏀', color: 'bg-blue-900/30 text-blue-400' },
  40: { name: 'MLB', icon: '⚾', color: 'bg-red-900/30 text-red-400' },
  41: { name: 'NCAAF', icon: '🏈', color: 'bg-purple-900/30 text-purple-400' },
  50: { name: 'ATP', icon: '🎾', color: 'bg-yellow-900/30 text-yellow-400' },
  51: { name: 'WTA', icon: '🎾', color: 'bg-pink-900/30 text-pink-400' },
};

// Confidence tier helper
type ConfidenceTier = 'green' | 'yellow' | 'red';

function getConfidenceTier(modelProb: number, ev: number): ConfidenceTier {
  if (modelProb >= 0.6 && ev >= 0.05) return 'green';
  if (ev < 0) return 'red';
  return 'yellow';
}

function ConfidenceTierDot({ tier }: { tier: ConfidenceTier }) {
  const config = {
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
  }[tier];
  
  return <span className={`inline-block w-2.5 h-2.5 rounded-full ${config}`} />;
}

// Format helpers
const formatPercent = (v: number | null) => v !== null ? `${(v * 100).toFixed(1)}%` : '-';
const formatOdds = (odds: number) => odds > 0 ? `+${odds}` : odds.toString();

export function MultiSportSlate() {
  const { data: sportsData, isLoading: sportsLoading } = useSports();
  
  // Filter state
  const [minEv, setMinEv] = useState(0.03);
  const [minConfidence, setMinConfidence] = useState(0.55);
  const [selectedSports, setSelectedSports] = useState<Set<number>>(new Set());
  const [onlyGreenTier, setOnlyGreenTier] = useState(false);
  const [maxPicks, setMaxPicks] = useState(50);
  
  // Reset all filters to show everything
  const resetFiltersToDefault = () => {
    setMinEv(0);
    setMinConfidence(0);
    setSelectedSports(new Set());
    setOnlyGreenTier(false);
    setMaxPicks(100);
  };
  
  // Get active sports (ones with data)
  const activeSports = useMemo(() => {
    if (!sportsData?.items) return [];
    return sportsData.items.filter(s => 
      selectedSports.size === 0 || selectedSports.has(s.id)
    );
  }, [sportsData, selectedSports]);
  
  // Filters for fetching
  const filters: PlayerPropFilters = useMemo(() => ({
    min_ev: minEv,
    min_confidence: minConfidence,
    fresh_only: false,
    limit: 50,
  }), [minEv, minConfidence]);
  
  // Fetch picks from all active sports in parallel
  const allSportsQuery = useQuery({
    queryKey: ['multiSportSlate', activeSports.map(s => s.id), filters],
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
            console.warn(`Failed to fetch picks for sport ${sport.id}:`, e);
            return [];
          }
        })
      );
      
      return results.flat();
    },
    enabled: activeSports.length > 0,
    staleTime: 60000, // 1 minute
  });
  
  // Sort and filter picks
  const sortedPicks = useMemo(() => {
    if (!allSportsQuery.data) return [];
    
    let picks = [...allSportsQuery.data];
    
    // Filter to green tier only if enabled
    if (onlyGreenTier) {
      picks = picks.filter(p => 
        getConfidenceTier(p.model_probability, p.expected_value) === 'green'
      );
    }
    
    // Sort by EV descending
    picks.sort((a, b) => b.expected_value - a.expected_value);
    
    // Limit results
    return picks.slice(0, maxPicks);
  }, [allSportsQuery.data, onlyGreenTier, maxPicks]);
  
  // Stats
  const stats = useMemo(() => {
    if (sortedPicks.length === 0) return null;
    const avgEv = sortedPicks.reduce((sum, p) => sum + p.expected_value, 0) / sortedPicks.length;
    const greenCount = sortedPicks.filter(p => 
      getConfidenceTier(p.model_probability, p.expected_value) === 'green'
    ).length;
    const sportCounts = new Map<string, number>();
    sortedPicks.forEach(p => {
      sportCounts.set(p.sport_name, (sportCounts.get(p.sport_name) || 0) + 1);
    });
    return { avgEv, greenCount, sportCounts };
  }, [sortedPicks]);
  
  const toggleSport = (sportId: number) => {
    setSelectedSports(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sportId)) newSet.delete(sportId);
      else newSet.add(sportId);
      return newSet;
    });
  };
  
  const isLoading = sportsLoading || allSportsQuery.isLoading;
  
  // Handle sport selection from TonightDashboard
  const handleSelectSportFromDashboard = (sportId: number) => {
    // Toggle this sport on (add to filter) 
    setSelectedSports(new Set([sportId]));
  };
  
  return (
    <div className="space-y-4">
      {/* Tonight's Dashboard */}
      <TonightDashboard onSelectSport={handleSelectSportFromDashboard} />
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-6 pt-6 border-t border-gray-700">
        <div>
          <h2 className="text-xl font-bold text-white">Multi-Sport Slate</h2>
          <p className="text-sm text-gray-400">
            Top picks across all sports, sorted by EV for cross-sport DFS entries
          </p>
        </div>
      </div>
      
      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex flex-wrap gap-4 items-end">
          {/* Sport Toggles */}
          <div>
            <label className="block text-xs text-gray-400 mb-2">Sports</label>
            <div className="flex flex-wrap gap-1">
              {sportsData?.items.map(sport => {
                const config = SPORT_CONFIG[sport.id] || { name: sport.name, icon: '🎮', color: 'bg-gray-700 text-gray-300' };
                const isSelected = selectedSports.size === 0 || selectedSports.has(sport.id);
                return (
                  <button
                    key={sport.id}
                    onClick={() => toggleSport(sport.id)}
                    className={`px-2 py-1 text-xs rounded border transition-colors ${
                      isSelected
                        ? config.color + ' border-current'
                        : 'bg-gray-800 border-gray-700 text-gray-500'
                    }`}
                  >
                    {config.icon} {config.name}
                  </button>
                );
              })}
              {selectedSports.size > 0 && (
                <button
                  onClick={() => setSelectedSports(new Set())}
                  className="px-2 py-1 text-xs text-gray-500 hover:text-gray-400"
                >
                  Show All
                </button>
              )}
            </div>
          </div>
          
          {/* Min EV */}
          <div className="min-w-[120px]">
            <label className="block text-xs text-gray-400 mb-1">
              Min EV: {(minEv * 100).toFixed(0)}%
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
          <div className="min-w-[120px]">
            <label className="block text-xs text-gray-400 mb-1">
              Min Conf: {(minConfidence * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0.5"
              max="0.8"
              step="0.05"
              value={minConfidence}
              onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>
          
          {/* Green Tier Only */}
          <button
            onClick={() => setOnlyGreenTier(!onlyGreenTier)}
            className={`px-3 py-1.5 text-xs rounded border transition-colors ${
              onlyGreenTier
                ? 'bg-green-900/30 border-green-600 text-green-400'
                : 'bg-gray-700 border-gray-600 text-gray-400'
            }`}
          >
            {onlyGreenTier ? '✓' : '○'} Green Only
          </button>
          
          {/* Max Picks */}
          <div>
            <label className="block text-xs text-gray-400 mb-1">Show</label>
            <select
              value={maxPicks}
              onChange={(e) => setMaxPicks(Number(e.target.value))}
              className="bg-gray-700 text-white rounded px-2 py-1.5 text-sm border border-gray-600"
            >
              <option value={25}>Top 25</option>
              <option value={50}>Top 50</option>
              <option value={100}>Top 100</option>
            </select>
          </div>
        </div>
      </div>
      
      {/* All Picks Hidden Warning */}
      {!isLoading && sortedPicks.length === 0 && allSportsQuery.data && allSportsQuery.data.length > 0 && (
        <div className="bg-orange-900/20 border border-orange-700 rounded-lg p-3 flex items-center justify-between">
          <span className="text-sm text-orange-400">
            All {allSportsQuery.data.length} picks are hidden by your current filters
          </span>
          <button 
            onClick={resetFiltersToDefault}
            className="text-sm text-orange-400 hover:text-orange-300 underline"
          >
            Show all picks
          </button>
        </div>
      )}
      
      {/* Stats Summary */}
      {stats && sortedPicks.length > 0 && (
        <div className="bg-gradient-to-r from-green-900/20 to-blue-900/20 border border-green-700/30 rounded-lg p-4">
          <div className="flex flex-wrap items-center gap-6 text-sm">
            <div>
              <span className="text-gray-400">Total Picks:</span>
              <span className="ml-2 text-white font-bold">{sortedPicks.length}</span>
            </div>
            <div>
              <span className="text-gray-400">Avg EV:</span>
              <span className="ml-2 text-green-400 font-bold">+{formatPercent(stats.avgEv)}</span>
            </div>
            <div>
              <span className="text-gray-400">Green Tier:</span>
              <span className="ml-2 text-green-400 font-bold">{stats.greenCount}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-gray-400">By Sport:</span>
              {Array.from(stats.sportCounts.entries()).map(([sport, count]) => (
                <span key={sport} className="text-xs px-2 py-0.5 bg-gray-700 rounded text-gray-300">
                  {sport}: {count}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full" />
        </div>
      )}
      
      {/* Picks Grid */}
      {!isLoading && sortedPicks.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {sortedPicks.map((pick, idx) => {
            const tier = getConfidenceTier(pick.model_probability, pick.expected_value);
            const sportConfig = SPORT_CONFIG[pick.sport_id] || { icon: '🎮', color: 'bg-gray-700' };
            
            return (
              <div
                key={`${pick.sport_id}-${pick.pick_id}-${idx}`}
                className={`bg-gray-800 border rounded-lg p-3 transition-all hover:border-gray-500 ${
                  tier === 'green' ? 'border-green-700/50' : 
                  tier === 'red' ? 'border-red-700/50' : 'border-gray-700'
                }`}
              >
                {/* Header */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-1.5 py-0.5 rounded ${sportConfig.color}`}>
                      {sportConfig.icon} {pick.sport_name}
                    </span>
                    <ConfidenceTierDot tier={tier} />
                  </div>
                  <span className="text-xs text-gray-500">#{idx + 1}</span>
                </div>
                
                {/* Player + Prop */}
                <div className="mb-2">
                  <div className="text-white font-medium">{pick.player_name}</div>
                  <div className="text-sm text-gray-400">
                    {pick.team_abbr || pick.team} vs {pick.opponent_abbr || pick.opponent_team}
                  </div>
                </div>
                
                {/* Line + Side */}
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs text-gray-500">{pick.stat_type}</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    pick.side === 'over' ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'
                  }`}>
                    {pick.side.toUpperCase()} {pick.line}
                  </span>
                  <span className="text-xs text-gray-400">{formatOdds(pick.odds)}</span>
                </div>
                
                {/* Stats Row */}
                <div className="flex items-center justify-between text-xs border-t border-gray-700 pt-2">
                  <div>
                    <span className="text-gray-500">Model:</span>
                    <span className="ml-1 text-green-400">{formatPercent(pick.model_probability)}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">EV:</span>
                    <span className={`ml-1 font-bold ${pick.expected_value > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      +{formatPercent(pick.expected_value)}
                    </span>
                  </div>
                  {pick.kelly_units && pick.kelly_units > 0 && (
                    <div>
                      <span className="text-gray-500">Kelly:</span>
                      <span className="ml-1 text-yellow-400">{pick.kelly_units}u</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {/* Empty State */}
      {!isLoading && sortedPicks.length === 0 && (
        <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
          <div className="text-4xl mb-3">🔍</div>
          <p className="text-gray-400 text-lg">No picks match your filters</p>
          <p className="text-sm text-gray-500 mt-2">
            {allSportsQuery.data && allSportsQuery.data.length > 0
              ? `${allSportsQuery.data.length} picks available but hidden by filters (minEV: ${(minEv * 100).toFixed(0)}%, minConf: ${(minConfidence * 100).toFixed(0)}%)`
              : 'No picks available across sports right now'}
          </p>
          <button
            onClick={resetFiltersToDefault}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg"
          >
            Reset All Filters
          </button>
        </div>
      )}
    </div>
  );
}
