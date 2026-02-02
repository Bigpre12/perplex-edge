import { useState, useMemo, useEffect } from 'react';
import { usePlayerPropPicks, STAT_TYPE_OPTIONS, PlayerPropFilters, BookLine, PlayerPropPick, useWatchlists, createWatchlist, deleteWatchlist, markWatchlistChecked, Watchlist } from '../api/public';
import { useSportContext } from '../context/SportContext';
import { ConfidenceBadge } from './ConfidenceBadge';
import { AltLineExplorer } from './AltLineExplorer';
import { useQueryClient } from '@tanstack/react-query';

// ============================================================================
// Confidence Tier Helpers
// ============================================================================

type ConfidenceTier = 'green' | 'yellow' | 'red';

function getConfidenceTier(modelProb: number, ev: number): ConfidenceTier {
  // Green: high confidence (≥60%) AND strong EV (≥5%)
  if (modelProb >= 0.6 && ev >= 0.05) return 'green';
  // Red: negative EV
  if (ev < 0) return 'red';
  // Yellow: thin edge or lower confidence
  return 'yellow';
}

function ConfidenceTierBadge({ tier }: { tier: ConfidenceTier }) {
  const config = {
    green: { bg: 'bg-green-900/50', border: 'border-green-500', text: 'text-green-400', label: '●' },
    yellow: { bg: 'bg-yellow-900/50', border: 'border-yellow-500', text: 'text-yellow-400', label: '●' },
    red: { bg: 'bg-red-900/50', border: 'border-red-500', text: 'text-red-400', label: '●' },
  }[tier];
  
  return (
    <span 
      className={`inline-block w-3 h-3 rounded-full ${config.bg} border ${config.border}`}
      title={tier === 'green' ? 'Strong pick' : tier === 'yellow' ? 'Thin edge' : 'Negative EV'}
    />
  );
}

// ============================================================================
// Stale Line Detection
// ============================================================================

function isLinePotentiallyStale(gameStartTime: string): boolean {
  const now = new Date();
  const gameStart = new Date(gameStartTime);
  const hoursUntilGame = (gameStart.getTime() - now.getTime()) / (1000 * 60 * 60);
  
  // If game starts within 2 hours, lines should be fresh - flag if potentially stale
  // For now, we just warn for games starting very soon (< 1 hour)
  return hoursUntilGame < 1 && hoursUntilGame > 0;
}

function StaleBadge({ gameStartTime }: { gameStartTime: string }) {
  if (!isLinePotentiallyStale(gameStartTime)) return null;
  
  return (
    <span 
      className="ml-1 px-1.5 py-0.5 text-xs bg-orange-900/50 text-orange-400 rounded"
      title="Game starts soon - verify line is current"
    >
      ⏰
    </span>
  );
}

// ============================================================================
// Don't Bet List - Exclusion Filters
// ============================================================================

const TRAP_STAT_TYPES = [
  { value: 'player_threes', label: '3PT Made', reason: 'High variance' },
  { value: 'player_steals', label: 'Steals', reason: 'Very random' },
  { value: 'player_blocks', label: 'Blocks', reason: 'Very random' },
  { value: 'player_turnovers', label: 'Turnovers', reason: 'Hard to model' },
];

// ============================================================================
// Opposite Side Info - Shows model's view of both sides
// ============================================================================

interface OppositeSideInfo {
  otherSide: 'over' | 'under';
  otherProb: number;
  otherEv: number;
  isCoinFlip: boolean; // Both sides 49-51%
  edgeDirection: 'strong' | 'weak' | 'none';
}

function getOppositeSideInfo(modelProb: number, side: string, impliedProb: number): OppositeSideInfo {
  const otherSide = side === 'over' ? 'under' : 'over';
  const otherProb = 1 - modelProb;
  // Approximate other side EV (assumes similar juice)
  const otherImplied = 1 - impliedProb;
  const otherEv = otherProb - otherImplied;
  
  // Coin flip detection: both sides within 49-51%
  const isCoinFlip = modelProb >= 0.49 && modelProb <= 0.51;
  
  // Edge direction
  let edgeDirection: 'strong' | 'weak' | 'none' = 'none';
  if (modelProb >= 0.55) edgeDirection = 'strong';
  else if (modelProb >= 0.52) edgeDirection = 'weak';
  
  return { otherSide, otherProb, otherEv, isCoinFlip, edgeDirection };
}

function OppositeSidePopover({ pick }: { pick: PlayerPropPick }) {
  const [isOpen, setIsOpen] = useState(false);
  const info = getOppositeSideInfo(pick.model_probability, pick.side, pick.implied_probability);
  
  const formatPercent = (v: number) => `${(v * 100).toFixed(1)}%`;
  
  return (
    <div className="relative inline-block">
      <button
        onClick={(e) => { e.stopPropagation(); setIsOpen(!isOpen); }}
        className={`text-xs px-1.5 py-0.5 rounded ${
          info.isCoinFlip 
            ? 'bg-gray-700 text-gray-400' 
            : info.edgeDirection === 'strong'
            ? 'bg-green-900/30 text-green-400'
            : 'bg-yellow-900/30 text-yellow-400'
        }`}
        title={info.isCoinFlip ? 'Coin flip - skip' : `Model: ${formatPercent(pick.model_probability)} ${pick.side.toUpperCase()}`}
      >
        {info.isCoinFlip ? '50/50' : info.edgeDirection === 'strong' ? '↑' : '~'}
      </button>
      
      {isOpen && (
        <div className="absolute z-50 left-0 mt-1 bg-gray-900 border border-gray-600 rounded-lg shadow-xl p-3 min-w-[200px]">
          <div className="text-xs text-gray-400 mb-2 font-medium">Model View (Both Sides)</div>
          <div className="space-y-1 text-xs">
            <div className={`flex justify-between ${pick.expected_value > 0 ? 'text-green-400' : 'text-red-400'}`}>
              <span>{pick.side.toUpperCase()} {pick.line}:</span>
              <span>{formatPercent(pick.model_probability)} ({pick.expected_value > 0 ? '+' : ''}{formatPercent(pick.expected_value)} EV)</span>
            </div>
            <div className={`flex justify-between ${info.otherEv > 0 ? 'text-green-400' : 'text-red-400'}`}>
              <span>{info.otherSide.toUpperCase()} {pick.line}:</span>
              <span>{formatPercent(info.otherProb)} ({info.otherEv > 0 ? '+' : ''}{formatPercent(info.otherEv)} EV)</span>
            </div>
          </div>
          {info.isCoinFlip && (
            <div className="mt-2 pt-2 border-t border-gray-700 text-xs text-orange-400">
              ⚠️ Coin flip - both sides ~50%, skip this prop
            </div>
          )}
          <button
            onClick={(e) => { e.stopPropagation(); setIsOpen(false); }}
            className="mt-2 text-xs text-gray-500 hover:text-gray-400"
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Inline Quick Exclusion Controls
// ============================================================================

interface QuickExcludeProps {
  playerName: string;
  statType: string;
  onExcludePlayer: (name: string) => void;
  onExcludeStat: (stat: string) => void;
}

function QuickExcludeMenu({ playerName, statType, onExcludePlayer, onExcludeStat }: QuickExcludeProps) {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div className="relative inline-block">
      <button
        onClick={(e) => { e.stopPropagation(); setIsOpen(!isOpen); }}
        className="text-gray-500 hover:text-gray-400 text-xs px-1"
        title="Quick exclude options"
      >
        ⋮
      </button>
      
      {isOpen && (
        <div className="absolute z-50 right-0 mt-1 bg-gray-900 border border-gray-600 rounded-lg shadow-xl p-2 min-w-[160px]">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onExcludePlayer(playerName);
              setIsOpen(false);
            }}
            className="w-full text-left px-2 py-1.5 text-xs text-red-400 hover:bg-red-900/30 rounded"
          >
            🚫 Hide {playerName}
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onExcludeStat(statType);
              setIsOpen(false);
            }}
            className="w-full text-left px-2 py-1.5 text-xs text-orange-400 hover:bg-orange-900/30 rounded"
          >
            🚫 Hide all {statType}
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); setIsOpen(false); }}
            className="w-full text-left px-2 py-1.5 text-xs text-gray-500 hover:bg-gray-800 rounded mt-1"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}

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

  // Filter state - EV-first defaults for max profit
  const [statType, setStatType] = useState<string>('');
  const [minConfidence, setMinConfidence] = useState<number>(0.55); // 55%+ confidence (sweet spot)
  const [minEv, setMinEv] = useState<number>(0.03);                 // 3%+ EV only
  const [riskLevels, setRiskLevels] = useState<string[]>(['STANDARD', 'CONFIDENT', 'STRONG']);
  
  // Don't Bet List state
  const [showDontBetPanel, setShowDontBetPanel] = useState(false);
  const [excludedStatTypes, setExcludedStatTypes] = useState<Set<string>>(new Set(['player_steals', 'player_blocks']));
  const [excludedPlayers, setExcludedPlayers] = useState<Set<string>>(new Set());
  const [onlyGreenTier, setOnlyGreenTier] = useState(false);
  const [hideStaleLines, setHideStaleLines] = useState(true);
  const [hideCoinFlips, setHideCoinFlips] = useState(true); // Auto-hide 49-51% props
  
  // Alt-line explorer state
  const [exploringPickId, setExploringPickId] = useState<number | null>(null);
  
  // Watchlist state
  const queryClient = useQueryClient();
  const { data: watchlistsData } = useWatchlists(sportId ?? undefined);
  const [showWatchlistPanel, setShowWatchlistPanel] = useState(false);
  const [watchlistName, setWatchlistName] = useState('');
  const [savingWatchlist, setSavingWatchlist] = useState(false);
  
  // Load watchlist filters
  const loadWatchlist = async (watchlist: Watchlist) => {
    if (watchlist.filters.stat_type) setStatType(watchlist.filters.stat_type);
    if (watchlist.filters.min_ev !== undefined) setMinEv(watchlist.filters.min_ev);
    if (watchlist.filters.min_confidence !== undefined) setMinConfidence(watchlist.filters.min_confidence);
    if (watchlist.filters.risk_levels) setRiskLevels(watchlist.filters.risk_levels.split(','));
    // Mark as checked to clear new matches badge
    try {
      await markWatchlistChecked(watchlist.id);
      queryClient.invalidateQueries({ queryKey: ['watchlists'] });
    } catch (err) {
      console.error('Failed to mark watchlist checked:', err);
    }
  };
  
  // Save current filters as watchlist
  const saveAsWatchlist = async () => {
    if (!watchlistName.trim() || !sportId) return;
    setSavingWatchlist(true);
    try {
      await createWatchlist({
        name: watchlistName,
        filters: {
          sport_id: sportId,
          stat_type: statType || undefined,
          min_ev: minEv || undefined,
          min_confidence: minConfidence || undefined,
          risk_levels: riskLevels.length > 0 ? riskLevels.join(',') : undefined,
        },
      });
      setWatchlistName('');
      setShowWatchlistPanel(false);
      queryClient.invalidateQueries({ queryKey: ['watchlists'] });
    } catch (err) {
      console.error('Failed to save watchlist:', err);
    } finally {
      setSavingWatchlist(false);
    }
  };
  
  // Delete a watchlist
  const handleDeleteWatchlist = async (id: number) => {
    try {
      await deleteWatchlist(id);
      queryClient.invalidateQueries({ queryKey: ['watchlists'] });
    } catch (err) {
      console.error('Failed to delete watchlist:', err);
    }
  };
  
  // Toggle excluded stat type
  const toggleExcludedStat = (stat: string) => {
    setExcludedStatTypes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(stat)) newSet.delete(stat);
      else newSet.add(stat);
      return newSet;
    });
  };
  
  // Add player to exclusion list
  const excludePlayer = (name: string) => {
    setExcludedPlayers(prev => new Set([...prev, name]));
  };
  
  // Remove player from exclusion list
  const unexcludePlayer = (name: string) => {
    setExcludedPlayers(prev => {
      const newSet = new Set(prev);
      newSet.delete(name);
      return newSet;
    });
  };
  
  // Reset all filters to show everything
  const resetFiltersToDefault = () => {
    setStatType('');
    setMinConfidence(0);
    setMinEv(0);
    setRiskLevels(['SMALL', 'STANDARD', 'CONFIDENT', 'STRONG', 'MAX']);
    setExcludedStatTypes(new Set());
    setExcludedPlayers(new Set());
    setOnlyGreenTier(false);
    setHideCoinFlips(false);
    setHideStaleLines(false);
  };

  // Build filters object
  const filters: PlayerPropFilters = useMemo(
    () => ({
      stat_type: statType || undefined,
      min_confidence: minConfidence > 0 ? minConfidence : undefined,
      min_ev: minEv > 0 ? minEv : undefined,
      risk_levels: riskLevels.length > 0 ? riskLevels.join(',') : undefined,
      fresh_only: false,  // Show all picks regardless of game start time
      limit: 100,
    }),
    [statType, minConfidence, minEv, riskLevels]
  );

  // Available Kelly risk levels
  const RISK_LEVEL_OPTIONS = [
    { value: 'SMALL', label: 'Small', color: 'gray' },
    { value: 'STANDARD', label: 'Standard', color: 'blue' },
    { value: 'CONFIDENT', label: 'Confident', color: 'green' },
    { value: 'STRONG', label: 'Strong', color: 'yellow' },
    { value: 'MAX', label: 'Max', color: 'red' },
  ];

  const toggleRiskLevel = (level: string) => {
    setRiskLevels(prev => 
      prev.includes(level) 
        ? prev.filter(l => l !== level)
        : [...prev, level]
    );
  };

  // Fetch data with React Query
  const { data: rawData, isLoading, error, isFetching } = usePlayerPropPicks(sportId, filters);
  
  // Apply client-side "Don't Bet List" filters
  const data = useMemo(() => {
    if (!rawData) return rawData;
    
    let filteredItems = rawData.items;
    
    // Filter out excluded stat types
    if (excludedStatTypes.size > 0) {
      filteredItems = filteredItems.filter(pick => !excludedStatTypes.has(pick.stat_type));
    }
    
    // Filter out excluded players
    if (excludedPlayers.size > 0) {
      filteredItems = filteredItems.filter(pick => !excludedPlayers.has(pick.player_name));
    }
    
    // Filter to green tier only if enabled
    if (onlyGreenTier) {
      filteredItems = filteredItems.filter(pick => 
        getConfidenceTier(pick.model_probability, pick.expected_value) === 'green'
      );
    }
    
    // Hide coin flip props (49-51% model probability)
    if (hideCoinFlips) {
      filteredItems = filteredItems.filter(pick => 
        pick.model_probability < 0.49 || pick.model_probability > 0.51
      );
    }
    
    // Hide stale lines
    if (hideStaleLines) {
      filteredItems = filteredItems.filter(pick => !isLinePotentiallyStale(pick.game_start_time));
    }
    
    return {
      ...rawData,
      items: filteredItems,
      total: filteredItems.length,
    };
  }, [rawData, excludedStatTypes, excludedPlayers, onlyGreenTier, hideCoinFlips, hideStaleLines]);

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

          {/* Kelly Risk Level Filter */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Kelly Risk</label>
            <div className="flex gap-1">
              {RISK_LEVEL_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => toggleRiskLevel(opt.value)}
                  className={`px-2 py-1 text-xs rounded border transition-colors ${
                    riskLevels.includes(opt.value)
                      ? opt.value === 'SMALL' ? 'bg-gray-600 border-gray-500 text-white'
                      : opt.value === 'STANDARD' ? 'bg-blue-900/50 border-blue-500 text-blue-400'
                      : opt.value === 'CONFIDENT' ? 'bg-green-900/50 border-green-500 text-green-400'
                      : opt.value === 'STRONG' ? 'bg-yellow-900/50 border-yellow-500 text-yellow-400'
                      : 'bg-red-900/50 border-red-500 text-red-400'
                      : 'bg-gray-800 border-gray-600 text-gray-500 hover:border-gray-500'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Results count + Watchlists + Don't Bet Toggle */}
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-400">
              {isFetching && <span className="animate-pulse">Updating...</span>}
              {data && !isFetching && (
                <span>
                  <span className="text-white font-medium">{data.total}</span> picks
                  {rawData && rawData.total !== data.total && (
                    <span className="text-orange-400 ml-1">
                      ({rawData.total - data.total} filtered)
                    </span>
                  )}
                </span>
              )}
            </div>
            
            {/* Watchlist Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowWatchlistPanel(!showWatchlistPanel)}
                className={`text-xs px-3 py-1 rounded-full border transition-colors flex items-center gap-1 ${
                  showWatchlistPanel
                    ? 'bg-purple-900/30 border-purple-600 text-purple-400'
                    : 'bg-gray-700 border-gray-600 text-gray-400 hover:border-gray-500'
                }`}
              >
                <span>📋</span>
                <span>Watchlists</span>
                {watchlistsData?.items && watchlistsData.items.some(w => w.new_matches_since_last_check > 0) && (
                  <span className="bg-green-500 text-white text-[10px] px-1.5 rounded-full ml-1">
                    {watchlistsData.items.reduce((sum, w) => sum + w.new_matches_since_last_check, 0)} new
                  </span>
                )}
              </button>
              
              {showWatchlistPanel && (
                <div className="absolute z-50 right-0 mt-1 bg-gray-900 border border-gray-600 rounded-lg shadow-xl p-3 min-w-[280px]">
                  <div className="text-xs text-gray-400 mb-2 font-medium">My Watchlists</div>
                  
                  {/* Existing watchlists */}
                  {watchlistsData?.items && watchlistsData.items.length > 0 ? (
                    <div className="space-y-1 max-h-48 overflow-y-auto mb-3">
                      {watchlistsData.items.map(w => (
                        <div key={w.id} className="flex items-center justify-between bg-gray-800 rounded p-2 group">
                          <button
                            onClick={() => {
                              loadWatchlist(w);
                              setShowWatchlistPanel(false);
                            }}
                            className="flex-1 text-left text-sm text-white hover:text-purple-300"
                          >
                            {w.name}
                            {w.new_matches_since_last_check > 0 && (
                              <span className="ml-2 text-xs bg-green-500 text-white px-1.5 rounded-full">
                                +{w.new_matches_since_last_check}
                              </span>
                            )}
                            <span className="text-xs text-gray-500 ml-1">
                              ({w.current_match_count} matches)
                            </span>
                          </button>
                          <button
                            onClick={() => handleDeleteWatchlist(w.id)}
                            className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 p-1 text-xs"
                            title="Delete watchlist"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-xs text-gray-500 mb-3">No saved watchlists yet</div>
                  )}
                  
                  {/* Save new watchlist */}
                  <div className="border-t border-gray-700 pt-2">
                    <div className="text-xs text-gray-400 mb-1">Save current filters:</div>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={watchlistName}
                        onChange={(e) => setWatchlistName(e.target.value)}
                        placeholder="e.g., NBA Assists Unders"
                        className="flex-1 bg-gray-800 border border-gray-600 rounded px-2 py-1 text-xs text-white"
                      />
                      <button
                        onClick={saveAsWatchlist}
                        disabled={!watchlistName.trim() || savingWatchlist}
                        className="px-2 py-1 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-600 text-white text-xs rounded"
                      >
                        {savingWatchlist ? '...' : 'Save'}
                      </button>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => setShowWatchlistPanel(false)}
                    className="mt-2 text-xs text-gray-500 hover:text-gray-400"
                  >
                    Close
                  </button>
                </div>
              )}
            </div>
            
            <button
              onClick={() => setShowDontBetPanel(!showDontBetPanel)}
              className={`text-xs px-3 py-1 rounded-full border transition-colors ${
                showDontBetPanel || excludedStatTypes.size > 0 || excludedPlayers.size > 0 || onlyGreenTier
                  ? 'bg-orange-900/30 border-orange-600 text-orange-400'
                  : 'bg-gray-700 border-gray-600 text-gray-400 hover:border-gray-500'
              }`}
            >
              🚫 Don't Bet List {(excludedStatTypes.size + excludedPlayers.size) > 0 && `(${excludedStatTypes.size + excludedPlayers.size})`}
            </button>
          </div>
        </div>
        
        {/* Don't Bet List Panel */}
        {showDontBetPanel && (
          <div className="mt-4 pt-4 border-t border-gray-700">
            <div className="flex flex-wrap gap-6">
              {/* Trap Stat Types */}
              <div>
                <div className="text-xs text-gray-400 mb-2 font-medium">Exclude Trap Stats</div>
                <div className="flex flex-wrap gap-2">
                  {TRAP_STAT_TYPES.map(stat => (
                    <button
                      key={stat.value}
                      onClick={() => toggleExcludedStat(stat.value)}
                      className={`px-2 py-1 text-xs rounded border transition-colors ${
                        excludedStatTypes.has(stat.value)
                          ? 'bg-red-900/30 border-red-600 text-red-400'
                          : 'bg-gray-700 border-gray-600 text-gray-400 hover:border-gray-500'
                      }`}
                      title={stat.reason}
                    >
                      {excludedStatTypes.has(stat.value) ? '✗' : '○'} {stat.label}
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Excluded Players (from inline hides) */}
              {excludedPlayers.size > 0 && (
                <div>
                  <div className="text-xs text-gray-400 mb-2 font-medium">Excluded Players</div>
                  <div className="flex flex-wrap gap-2">
                    {Array.from(excludedPlayers).map(name => (
                      <button
                        key={name}
                        onClick={() => unexcludePlayer(name)}
                        className="px-2 py-1 text-xs rounded border bg-red-900/30 border-red-600 text-red-400 hover:bg-red-900/50"
                        title="Click to remove from exclusion"
                      >
                        ✗ {name}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Quality Filters */}
              <div>
                <div className="text-xs text-gray-400 mb-2 font-medium">Quality Controls</div>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => setOnlyGreenTier(!onlyGreenTier)}
                    className={`px-2 py-1 text-xs rounded border transition-colors ${
                      onlyGreenTier
                        ? 'bg-green-900/30 border-green-600 text-green-400'
                        : 'bg-gray-700 border-gray-600 text-gray-400 hover:border-gray-500'
                    }`}
                    title="Only show picks with high confidence (≥60%) AND strong EV (≥5%)"
                  >
                    {onlyGreenTier ? '✓' : '○'} Green Tier Only
                  </button>
                  <button
                    onClick={() => setHideStaleLines(!hideStaleLines)}
                    className={`px-2 py-1 text-xs rounded border transition-colors ${
                      hideStaleLines
                        ? 'bg-orange-900/30 border-orange-600 text-orange-400'
                        : 'bg-gray-700 border-gray-600 text-gray-400 hover:border-gray-500'
                    }`}
                    title="Hide props for games starting within 1 hour (lines may be stale)"
                  >
                    {hideStaleLines ? '✓' : '○'} Hide Stale Lines
                  </button>
                  <button
                    onClick={() => setHideCoinFlips(!hideCoinFlips)}
                    className={`px-2 py-1 text-xs rounded border transition-colors ${
                      hideCoinFlips
                        ? 'bg-purple-900/30 border-purple-600 text-purple-400'
                        : 'bg-gray-700 border-gray-600 text-gray-400 hover:border-gray-500'
                    }`}
                    title="Hide props where model is 49-51% (coin flips with no edge)"
                  >
                    {hideCoinFlips ? '✓' : '○'} Hide Coin Flips
                  </button>
                </div>
              </div>
              
              {/* Quick Reset */}
              <div className="flex items-end">
                <button
                  onClick={() => {
                    setExcludedStatTypes(new Set(['player_steals', 'player_blocks']));
                    setExcludedPlayers(new Set());
                    setOnlyGreenTier(false);
                    setHideStaleLines(true);
                    setHideCoinFlips(true);
                  }}
                  className="text-xs text-gray-500 hover:text-gray-400 underline"
                >
                  Reset Filters
                </button>
              </div>
            </div>
            
            {/* Legend */}
            <div className="mt-3 pt-3 border-t border-gray-700/50 flex items-center gap-4 text-xs text-gray-500">
              <span>Tier Legend:</span>
              <span className="flex items-center gap-1">
                <ConfidenceTierBadge tier="green" /> Strong (≥60% conf, ≥5% EV)
              </span>
              <span className="flex items-center gap-1">
                <ConfidenceTierBadge tier="yellow" /> Thin edge
              </span>
              <span className="flex items-center gap-1">
                <ConfidenceTierBadge tier="red" /> Negative EV
              </span>
            </div>
          </div>
        )}
      </div>
      
      {/* All Picks Hidden Warning */}
      {!isLoading && data && data.items.length === 0 && rawData && rawData.total > 0 && (
        <div className="bg-orange-900/20 border border-orange-700 rounded-lg p-3 flex items-center justify-between">
          <span className="text-sm text-orange-400">
            All {rawData.total} picks are hidden by your current filters
          </span>
          <button 
            onClick={resetFiltersToDefault}
            className="text-sm text-orange-400 hover:text-orange-300 underline"
          >
            Show all picks
          </button>
        </div>
      )}

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
                  <th className="px-2 py-3 text-center w-8" title="Confidence Tier">Tier</th>
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
                  <th className="px-3 py-3 text-center">Kelly</th>
                  <th className="px-3 py-3 text-left">Start Time</th>
                  <th className="px-3 py-3 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {data.items.map((pick) => {
                  const tier = getConfidenceTier(pick.model_probability, pick.expected_value);
                  return (
                  <tr
                    key={pick.pick_id}
                    className={`hover:bg-gray-700/50 transition-colors ${
                      tier === 'green' ? 'bg-green-900/5' : 
                      tier === 'red' ? 'bg-red-900/5' : ''
                    }`}
                  >
                    <td className="px-2 py-3 text-center">
                      <ConfidenceTierBadge tier={tier} />
                    </td>
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
                      <div className="flex items-center justify-center gap-1">
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-medium ${
                            pick.side === 'over'
                              ? 'bg-green-900/50 text-green-400'
                              : 'bg-red-900/50 text-red-400'
                          }`}
                        >
                          {pick.side.toUpperCase()}
                        </span>
                        <OppositeSidePopover pick={pick} />
                      </div>
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
                    <td className="px-3 py-3 text-center">
                      {pick.kelly_units !== null && pick.kelly_units > 0 ? (
                        <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                          pick.kelly_risk_level === 'MAX' || pick.kelly_risk_level === 'STRONG'
                            ? 'bg-yellow-900/50 text-yellow-400'
                            : pick.kelly_risk_level === 'CONFIDENT'
                            ? 'bg-green-900/50 text-green-400'
                            : pick.kelly_risk_level === 'STANDARD'
                            ? 'bg-blue-900/50 text-blue-400'
                            : 'bg-gray-700/50 text-gray-400'
                        }`} title={`${pick.kelly_edge_pct}% edge - ${pick.kelly_risk_level}`}>
                          {pick.kelly_units}u
                        </span>
                      ) : (
                        <span className="text-gray-600 text-xs">-</span>
                      )}
                    </td>
                    <td className="px-3 py-3 text-gray-400 text-xs">
                      {formatTime(pick.game_start_time)}
                      <StaleBadge gameStartTime={pick.game_start_time} />
                    </td>
                    <td className="px-3 py-3 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <button
                          onClick={() => setExploringPickId(pick.pick_id)}
                          className="text-blue-400 hover:text-blue-300 text-xs underline"
                          title="Explore alternate lines"
                        >
                          Alt Lines
                        </button>
                        <QuickExcludeMenu
                          playerName={pick.player_name}
                          statType={pick.stat_type}
                          onExcludePlayer={excludePlayer}
                          onExcludeStat={toggleExcludedStat}
                        />
                      </div>
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
            
            {/* Alt-line explorer modal */}
            {exploringPickId !== null && (
              <AltLineExplorer
                pickId={exploringPickId}
                onClose={() => setExploringPickId(null)}
              />
            )}
          </div>
        </div>
      )}

      {/* Empty State */}
      {data && data.items.length === 0 && (
        <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
          <div className="text-4xl mb-3">🔍</div>
          <p className="text-gray-400 text-lg">No picks match your filters</p>
          <p className="text-sm text-gray-500 mt-2">
            {rawData && rawData.total > 0 
              ? `${rawData.total} picks available but hidden by current filters`
              : 'No picks available for this sport right now'}
          </p>
          {rawData && rawData.total > 0 && (
            <button
              onClick={resetFiltersToDefault}
              className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg"
            >
              Reset All Filters
            </button>
          )}
        </div>
      )}
    </div>
  );
}
