import { useState, useMemo, useCallback } from 'react';
import { useParlayBuilder, ParlayBuilderFilters, ParlayRecommendation, ParlayLeg, CorrelationWarning, fetchAutoGenerateSlips, AutoGenerateSlipsResponse, createSharedCard, CardLeg, quoteParlayLegs, QuoteResponse, OddsMovement, QuotedLeg, useOddsHealth } from '../api/public';
import { useSportContext } from '../context/SportContext';
import { DEFAULT_PARLAY_FILTERS } from '../constants/presets';
import { formatParlayForClipboard, copyToClipboard } from '../utils/clipboard';

// ============================================================================
// DFS Platform Payout Tables
// ============================================================================

type EntryType = 'power' | 'flex';

interface PayoutEntry {
  legs: number;
  type: EntryType;
  multiplier: number;
  flexMisses?: number; // How many can miss for flex
  flexMultiplier?: number; // Reduced payout if flex hits
}

interface PlatformConfig {
  name: string;
  payouts: PayoutEntry[];
  houseEdgeLabel: string;
  bestStructures: number[]; // Leg counts with best theoretical edge
  warnStructures: number[]; // Leg counts with high house edge
}

const PLATFORM_CONFIGS: Record<string, PlatformConfig> = {
  prizepicks: {
    name: 'PrizePicks',
    payouts: [
      { legs: 2, type: 'power', multiplier: 3 },
      { legs: 3, type: 'power', multiplier: 5 },
      { legs: 3, type: 'flex', multiplier: 5, flexMisses: 1, flexMultiplier: 1.25 },
      { legs: 4, type: 'power', multiplier: 10 },
      { legs: 4, type: 'flex', multiplier: 10, flexMisses: 1, flexMultiplier: 1.5 },
      { legs: 5, type: 'power', multiplier: 20 },
      { legs: 5, type: 'flex', multiplier: 20, flexMisses: 2, flexMultiplier: 0.4 },
      { legs: 6, type: 'power', multiplier: 37.5 },
      { legs: 6, type: 'flex', multiplier: 37.5, flexMisses: 2, flexMultiplier: 2.5 },
    ],
    houseEdgeLabel: '~10-20%',
    bestStructures: [3, 5], // 3-pick and 5-pick flex have best math
    warnStructures: [2, 6], // 2-pick power and 6-pick have worse edges
  },
  fliff: {
    name: 'Fliff',
    payouts: [
      { legs: 2, type: 'power', multiplier: 3 },
      { legs: 3, type: 'power', multiplier: 5 },
      { legs: 4, type: 'power', multiplier: 10 },
      { legs: 5, type: 'power', multiplier: 20 },
      { legs: 6, type: 'power', multiplier: 40 },
    ],
    houseEdgeLabel: '~15-25%',
    bestStructures: [3, 4],
    warnStructures: [2, 6],
  },
  underdog: {
    name: 'Underdog',
    payouts: [
      { legs: 2, type: 'power', multiplier: 3 },
      { legs: 3, type: 'power', multiplier: 6 },
      { legs: 4, type: 'power', multiplier: 10 },
      { legs: 5, type: 'power', multiplier: 20 },
      { legs: 6, type: 'power', multiplier: 35 },
    ],
    houseEdgeLabel: '~12-18%',
    bestStructures: [3, 5],
    warnStructures: [2],
  },
  sportsbook: {
    name: 'Sportsbook',
    payouts: [], // Standard parlay math, no fixed table
    houseEdgeLabel: 'Variable (vig)',
    bestStructures: [2, 3],
    warnStructures: [5, 6],
  },
};

// Calculate break-even hit rate per leg for a given payout
function calcBreakEvenPerLeg(multiplier: number, legs: number): number {
  // For all legs to hit at multiplier X: (hitRate)^legs = 1/X
  // hitRate = (1/X)^(1/legs)
  return Math.pow(1 / multiplier, 1 / legs);
}

// Calculate structure EV given model probability and platform payout
function calcStructureEV(modelProb: number, multiplier: number): number {
  // EV = (prob * multiplier) - 1
  return (modelProb * multiplier) - 1;
}

// Get structure edge rating
function getStructureEdge(structureEV: number, platform: string, legs: number): { label: string; color: string } {
  const config = PLATFORM_CONFIGS[platform];
  const isBest = config?.bestStructures.includes(legs);
  const isWarn = config?.warnStructures.includes(legs);
  
  if (structureEV > 0.08) return { label: 'Excellent', color: 'text-green-400' };
  if (structureEV > 0.03) return { label: isBest ? 'Good' : 'Decent', color: isBest ? 'text-green-400' : 'text-blue-400' };
  if (structureEV > 0) return { label: isWarn ? 'Marginal' : 'Neutral', color: isWarn ? 'text-yellow-400' : 'text-gray-400' };
  return { label: 'Negative', color: 'text-red-400' };
}

// Grade colors
const GRADE_COLORS: Record<string, string> = {
  'A': 'bg-green-500 text-white',
  'B': 'bg-green-600 text-white',
  'C': 'bg-yellow-500 text-black',
  'D': 'bg-orange-500 text-white',
  'F': 'bg-red-500 text-white',
};

// Label colors
const LABEL_COLORS: Record<string, string> = {
  'LOCK': 'bg-green-500 text-white',
  'PLAY': 'bg-blue-500 text-white',
  'SKIP': 'bg-gray-600 text-gray-300',
};

// Grade badge
function GradeBadge({ grade }: { grade: string }) {
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-bold ${GRADE_COLORS[grade] || 'bg-gray-600 text-white'}`}>
      {grade}
    </span>
  );
}

// Label badge (LOCK/PLAY/SKIP)
function LabelBadge({ label }: { label: string }) {
  const icon = label === 'LOCK' ? '🔒' : label === 'PLAY' ? '▶️' : '⏭️';
  return (
    <span className={`px-3 py-1 rounded-full text-sm font-bold ${LABEL_COLORS[label] || 'bg-gray-600 text-white'}`}>
      {icon} {label}
    </span>
  );
}

// Odds movement badge - shows when odds changed
function OddsMovementBadge({ movement }: { movement: OddsMovement | null }) {
  if (!movement || movement.direction === 'stable') return null;
  
  const isUp = movement.direction === 'up';
  const colorClass = movement.favorable 
    ? 'bg-green-900/30 text-green-400 border-green-700' 
    : 'bg-red-900/30 text-red-400 border-red-700';
  
  return (
    <span 
      className={`px-2 py-0.5 rounded text-xs font-medium border ${colorClass}`}
      title={`Odds moved ${isUp ? 'up (better payout)' : 'down (worse payout)'}`}
    >
      {isUp ? '↑' : '↓'} {movement.display}
    </span>
  );
}

// Odds health banner - shows when odds may be stale
function OddsHealthBanner({ sportId }: { sportId: number | null }) {
  const { data: health } = useOddsHealth(sportId ?? undefined);
  
  if (!health || health.status === 'healthy') return null;
  
  const statusConfig = {
    degraded: {
      icon: '⚠️',
      color: 'bg-yellow-900/20 border-yellow-700 text-yellow-400',
      message: 'Some odds may be delayed',
    },
    stale: {
      icon: '⏰',
      color: 'bg-orange-900/20 border-orange-700 text-orange-400',
      message: 'Live odds temporarily unavailable; using last known prices',
    },
    no_data: {
      icon: '📭',
      color: 'bg-gray-800 border-gray-600 text-gray-400',
      message: 'No odds data available',
    },
    unknown: {
      icon: '❓',
      color: 'bg-gray-800 border-gray-600 text-gray-400',
      message: 'Unable to verify odds freshness',
    },
  };
  
  const config = statusConfig[health.status] || statusConfig.unknown;
  
  return (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-sm ${config.color}`}>
      <span>{config.icon}</span>
      <span>{config.message}</span>
      {health.newest_update && (
        <span className="text-xs opacity-70">
          (Last update: {new Date(health.newest_update).toLocaleTimeString()})
        </span>
      )}
    </div>
  );
}

// Correlation risk badge
const RISK_COLORS: Record<string, string> = {
  'LOW': 'bg-green-900/30 text-green-400 border-green-700',
  'MEDIUM': 'bg-yellow-900/30 text-yellow-400 border-yellow-700',
  'HIGH': 'bg-orange-900/30 text-orange-400 border-orange-700',
  'CRITICAL': 'bg-red-900/30 text-red-400 border-red-700',
};

function CorrelationRiskBadge({ risk, label }: { risk: number; label: string }) {
  if (label === 'LOW' && risk === 0) return null;
  
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium border ${RISK_COLORS[label] || 'bg-gray-700 text-gray-300'}`}>
      ⚠️ {label} CORR
    </span>
  );
}

// Correlation warning card
function CorrelationWarningCard({ warnings }: { warnings: CorrelationWarning[] }) {
  if (!warnings || warnings.length === 0) return null;
  
  const severityIcons: Record<string, string> = {
    'high': '🚫',
    'medium': '⚠️',
    'low': 'ℹ️',
  };
  
  const severityColors: Record<string, string> = {
    'high': 'border-red-700 bg-red-900/20',
    'medium': 'border-yellow-700 bg-yellow-900/20',
    'low': 'border-blue-700 bg-blue-900/20',
  };
  
  return (
    <div className="mt-3 space-y-2">
      <div className="text-xs text-gray-400 font-medium">Correlation Warnings:</div>
      {warnings.map((warning, idx) => (
        <div 
          key={idx}
          className={`p-2 rounded border text-xs ${severityColors[warning.severity] || 'border-gray-700'}`}
        >
          <span className="mr-1">{severityIcons[warning.severity] || '⚠️'}</span>
          {warning.message}
        </div>
      ))}
    </div>
  );
}

// Format odds
function formatOdds(odds: number): string {
  return odds > 0 ? `+${odds}` : odds.toString();
}

// Format percentage
function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

// Individual leg component
function LegCard({ leg, index, liveLeg }: { leg: ParlayLeg; index: number; liveLeg?: QuotedLeg | null }) {
  const displayOdds = liveLeg?.current_odds ?? leg.odds;
  const displayProb = liveLeg?.model_prob ?? leg.win_prob;
  
  return (
    <div className="flex items-center justify-between py-2 px-3 bg-gray-800/50 rounded-lg">
      <div className="flex items-center gap-3">
        <span className="text-gray-500 text-sm w-5">{index + 1}.</span>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-white font-medium">{leg.player_name}</span>
            <span className="text-gray-500 text-xs">{leg.team_abbr}</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-gray-400">
              {leg.stat_type.replace('player_', '').replace(/_/g, ' ').toUpperCase()}
            </span>
            <span className={`font-medium ${leg.side === 'over' ? 'text-green-400' : 'text-red-400'}`}>
              {leg.side.toUpperCase()} {leg.line}
            </span>
          </div>
        </div>
      </div>
      
      <div className="flex items-center gap-3">
        <div className="text-right">
          <div className="text-white font-medium">{formatOdds(displayOdds)}</div>
          <div className="text-xs text-gray-500">{formatPercent(displayProb)} prob</div>
          {liveLeg?.is_stale && (
            <div className="text-[10px] text-orange-400">odds may be stale</div>
          )}
        </div>
        <GradeBadge grade={leg.grade} />
        {leg.is_100_last_5 && (
          <span className="px-1.5 py-0.5 text-xs bg-green-900/50 text-green-400 rounded">
            100% L5
          </span>
        )}
        {liveLeg?.movement && <OddsMovementBadge movement={liveLeg.movement} />}
      </div>
    </div>
  );
}

// Props for ParlayCard with DFS platform info
interface ParlayCardProps {
  parlay: ParlayRecommendation;
  index: number;
  siteMode: string;
  entryType: EntryType;
  platformPayout: PayoutEntry | null;
  onSelect?: (index: number) => void;
  isSelected?: boolean;
}

// Parlay card component
function ParlayCard({ parlay, index, siteMode, entryType, platformPayout, onSelect, isSelected }: ParlayCardProps) {
  const [isExpanded, setIsExpanded] = useState(index === 0); // First one expanded by default
  const [isSharing, setIsSharing] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [copyStatus, setCopyStatus] = useState<'idle' | 'copied' | 'error'>('idle');
  
  // Live quote state
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [liveQuote, setLiveQuote] = useState<QuoteResponse | null>(null);
  const [quoteError, setQuoteError] = useState<string | null>(null);
  
  // Fetch live odds quote for this parlay
  const handleGetQuote = useCallback(async () => {
    setQuoteLoading(true);
    setQuoteError(null);
    try {
      // Filter out legs with null IDs (shouldn't happen but handle gracefully)
      const validLegs = parlay.legs.filter(
        (leg): leg is typeof leg & { game_id: number; player_id: number } =>
          leg.game_id !== null && leg.player_id !== null
      );
      
      if (validLegs.length === 0) {
        setQuoteError('No valid legs to quote');
        return;
      }
      
      const request = {
        legs: validLegs.map(leg => ({
          game_id: leg.game_id,
          player_id: leg.player_id,
          stat_type: leg.stat_type,
          line_value: leg.line,
          side: leg.side,
          model_odds: leg.odds,
          model_prob: leg.win_prob,
        })),
        use_cache: true,
      };
      const quote = await quoteParlayLegs(request);
      setLiveQuote(quote);
    } catch (err) {
      console.error('Quote failed:', err);
      setQuoteError('Failed to fetch live odds');
    } finally {
      setQuoteLoading(false);
    }
  }, [parlay.legs]);
  
  // Copy parlay to clipboard (simple text format)
  const handleCopy = async () => {
    const text = formatParlayForClipboard(parlay.legs, parlay.total_odds, parlay.parlay_ev);
    const success = await copyToClipboard(text);
    setCopyStatus(success ? 'copied' : 'error');
    setTimeout(() => setCopyStatus('idle'), 2000);
  };
  
  // Share parlay as a public card
  const handleShare = async () => {
    setIsSharing(true);
    try {
      const legs: CardLeg[] = parlay.legs.map(leg => ({
        player_name: leg.player_name,
        team_abbr: leg.team_abbr || null,
        stat_type: leg.stat_type,
        line: leg.line,
        side: leg.side,
        odds: leg.odds,
        grade: leg.grade,
        win_prob: leg.win_prob,
        edge: leg.edge,
      }));
      
      const card = await createSharedCard({
        platform: siteMode,
        legs,
        total_odds: parlay.total_odds,
        decimal_odds: parlay.decimal_odds,
        parlay_probability: parlay.parlay_probability,
        parlay_ev: parlay.parlay_ev,
        overall_grade: parlay.overall_grade,
        label: parlay.label,
        kelly_suggested_units: parlay.kelly?.suggested_units,
        kelly_risk_level: parlay.kelly?.risk_level,
      });
      
      // Build full URL
      const fullUrl = `${window.location.origin}/cards/${card.id}`;
      setShareUrl(fullUrl);
      
      // Copy to clipboard
      await navigator.clipboard.writeText(fullUrl);
    } catch (err) {
      console.error('Failed to share card:', err);
    } finally {
      setIsSharing(false);
    }
  };
  
  // Calculate unique games for same-game vs multi-game indicator
  const uniqueGames = new Set(parlay.legs.map(l => l.game_id).filter(id => id != null)).size;
  const isSameGame = uniqueGames === 1 && parlay.legs.length > 1;
  
  // Calculate structure EV based on platform payout
  const structureEV = platformPayout 
    ? calcStructureEV(parlay.parlay_probability, platformPayout.multiplier)
    : parlay.parlay_ev;
  const structureEdge = platformPayout 
    ? getStructureEdge(structureEV, siteMode, parlay.leg_count)
    : null;
  
  // Entry type label for DFS
  const entryLabel = siteMode !== 'sportsbook' && platformPayout
    ? `${platformPayout.legs}-${entryType === 'power' ? 'Power' : 'Flex'}`
    : null;
  
  return (
    <div className={`border rounded-lg overflow-hidden transition-all ${
      isSelected
        ? 'border-purple-500 bg-purple-900/20 ring-2 ring-purple-500/50'
        : parlay.label === 'LOCK' 
        ? 'border-green-500/50 bg-green-900/10' 
        : parlay.label === 'PLAY'
        ? 'border-blue-500/30 bg-blue-900/5'
        : 'border-gray-700 bg-gray-800/30'
    }`}>
      {/* Header - always visible */}
      <div 
        className="p-4 cursor-pointer hover:bg-gray-700/30 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Checkbox for session tracking */}
            {onSelect && (
              <button
                onClick={(e) => { e.stopPropagation(); onSelect(index); }}
                className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${
                  isSelected 
                    ? 'bg-purple-600 border-purple-500 text-white' 
                    : 'border-gray-600 hover:border-gray-400'
                }`}
              >
                {isSelected && <span className="text-xs">✓</span>}
              </button>
            )}
            <span className="text-gray-500 text-lg font-medium">#{index + 1}</span>
            {/* Entry type badge for DFS */}
            {entryLabel && (
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-purple-900/50 text-purple-300 border border-purple-700">
                {entryLabel}
              </span>
            )}
            <LabelBadge label={parlay.label} />
            <GradeBadge grade={parlay.overall_grade} />
            <CorrelationRiskBadge 
              risk={parlay.correlation_risk} 
              label={parlay.correlation_risk_label} 
            />
            {/* Same-game vs Multi-game indicator */}
            {isSameGame ? (
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-orange-900/30 text-orange-400 border border-orange-700">
                SGP
              </span>
            ) : uniqueGames > 1 ? (
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-green-900/30 text-green-400 border border-green-700">
                {uniqueGames} Games
              </span>
            ) : null}
          </div>
          
          <div className="flex items-center gap-6">
            {/* Payout (DFS) or Odds (Sportsbook) */}
            <div className="text-right">
              {platformPayout ? (
                <>
                  <div className="text-xl font-bold text-green-400">
                    {platformPayout.multiplier}x
                  </div>
                  <div className="text-xs text-gray-500">payout</div>
                </>
              ) : (
                <>
                  <div className="text-xl font-bold text-white">
                    {formatOdds(parlay.total_odds)}
                  </div>
                  <div className="text-xs text-gray-500">
                    {parlay.decimal_odds.toFixed(2)}x
                  </div>
                </>
              )}
            </div>
            
            {/* Win Prob */}
            <div className="text-right">
              <div className="text-lg font-medium text-blue-400">
                {formatPercent(parlay.parlay_probability)}
              </div>
              <div className="text-xs text-gray-500">win prob</div>
            </div>
            
            {/* Structure EV (DFS) or standard EV (Sportsbook) */}
            <div className="text-right">
              <div className={`text-lg font-medium ${structureEV > 0 ? 'text-green-400' : 'text-red-400'}`}>
                {structureEV > 0 ? '+' : ''}{formatPercent(structureEV)}
              </div>
              <div className="text-xs text-gray-500">
                {platformPayout ? 'structure EV' : 'EV'}
              </div>
            </div>
            
            {/* Structure Edge Badge (DFS only) */}
            {structureEdge && (
              <div className="text-right">
                <div className={`text-sm font-medium ${structureEdge.color}`}>
                  {structureEdge.label}
                </div>
                <div className="text-xs text-gray-500">edge</div>
              </div>
            )}
            
            {/* Kelly Sizing */}
            {parlay.kelly && parlay.kelly.suggested_units > 0 && (
              <div className="text-right">
                <div className={`text-lg font-bold ${
                  parlay.kelly.risk_level === 'MAX' || parlay.kelly.risk_level === 'STRONG' 
                    ? 'text-yellow-400' 
                    : parlay.kelly.risk_level === 'CONFIDENT' 
                    ? 'text-green-400' 
                    : 'text-gray-300'
                }`}>
                  {parlay.kelly.suggested_units}u
                </div>
                <div className="text-xs text-gray-500">suggested</div>
              </div>
            )}
            
            {/* Expand icon */}
            <span className={`text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
              ▼
            </span>
          </div>
        </div>
        
        {/* Summary when collapsed */}
        {!isExpanded && (
          <div className="mt-2 text-sm text-gray-400">
            {parlay.legs.map(l => l.player_name).join(' + ')}
          </div>
        )}
      </div>
      
      {/* Expanded content - legs */}
      {isExpanded && (
        <div className="border-t border-gray-700 p-4 space-y-2">
          {parlay.legs.map((leg, legIndex) => (
            <LegCard
              key={leg.pick_id}
              leg={leg}
              index={legIndex}
              liveLeg={liveQuote?.legs?.[legIndex] ?? null}
            />
          ))}
          
          {/* Correlation warnings */}
          {parlay.correlations && parlay.correlations.length > 0 && (
            <CorrelationWarningCard warnings={parlay.correlations} />
          )}
          
          {/* Platform validity warnings */}
          {parlay.platform_violations && parlay.platform_violations.length > 0 && (
            <div className="bg-red-900/20 border border-red-700 rounded-lg p-3 mt-2">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-red-400 font-medium text-sm">Platform Restrictions</span>
              </div>
              <div className="space-y-1">
                {parlay.platform_violations.map((violation, i) => (
                  <div key={i} className="text-xs text-red-300 flex items-start gap-2">
                    <span className={violation.severity === 'CRITICAL' ? 'text-red-400' : 'text-orange-400'}>
                      {violation.severity === 'CRITICAL' ? '🚫' : '⚠️'}
                    </span>
                    <span>{violation.message}</span>
                  </div>
                ))}
              </div>
              {parlay.valid_platforms && parlay.valid_platforms.length > 0 && (
                <div className="mt-2 pt-2 border-t border-red-800 text-xs text-gray-400">
                  Valid on: <span className="text-green-400">{parlay.valid_platforms.join(', ')}</span>
                </div>
              )}
            </div>
          )}
          
          {/* Live quote summary */}
          {liveQuote && (
            <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-2 text-xs text-gray-400">
              <span className="text-gray-300 font-medium">Live parlay:</span>{' '}
              <span className="text-white">{formatOdds(liveQuote.parlay_odds)}</span>{' '}
              <span className={liveQuote.parlay_ev >= 0 ? 'text-green-400' : 'text-red-400'}>
                ({liveQuote.parlay_ev >= 0 ? '+' : ''}{formatPercent(liveQuote.parlay_ev)} EV)
              </span>
              {liveQuote.stale_legs > 0 && (
                <span className="ml-2 text-orange-400">
                  {liveQuote.stale_legs} stale leg{liveQuote.stale_legs > 1 ? 's' : ''}
                </span>
              )}
            </div>
          )}
          {quoteError && (
            <div className="text-xs text-red-400">{quoteError}</div>
          )}
          
          {/* Stats footer */}
          <div className="flex items-center justify-between pt-3 mt-3 border-t border-gray-700 text-xs text-gray-500">
            <div>
              <span>Min leg prob: </span>
              <span className="text-gray-300">{formatPercent(parlay.min_leg_prob)}</span>
            </div>
            <div>
              <span>Avg edge: </span>
              <span className="text-gray-300">{formatPercent(parlay.avg_edge)}</span>
            </div>
            {parlay.kelly && (
              <div>
                <span>Kelly: </span>
                <span className={`font-medium ${
                  parlay.kelly.risk_level === 'NO_BET' ? 'text-red-400' : 'text-green-400'
                }`}>
                  {parlay.kelly.suggested_units}u ({parlay.kelly.risk_level})
                </span>
              </div>
            )}
            <div>
              <span>Legs: </span>
              <span className="text-gray-300">{parlay.leg_count}</span>
            </div>
            {/* Live Quote Button */}
            <button
              onClick={(e) => { e.stopPropagation(); handleGetQuote(); }}
              disabled={quoteLoading}
              className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                liveQuote
                  ? liveQuote.has_movement
                    ? 'bg-yellow-900/50 text-yellow-400 border border-yellow-700'
                    : 'bg-green-900/50 text-green-400 border border-green-700'
                  : quoteError
                  ? 'bg-red-900/50 text-red-400 border border-red-700'
                  : 'bg-blue-900/50 text-blue-400 border border-blue-700 hover:bg-blue-800/50'
              }`}
              title="Get real-time odds quote"
            >
              {quoteLoading ? '...' : liveQuote ? (liveQuote.has_movement ? '⚡ Updated' : '✓ Fresh') : '🔄 Live Quote'}
            </button>
            {/* Copy Button */}
            <button
              onClick={(e) => { e.stopPropagation(); handleCopy(); }}
              className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                copyStatus === 'copied'
                  ? 'bg-green-900/50 text-green-400 border border-green-700'
                  : copyStatus === 'error'
                  ? 'bg-red-900/50 text-red-400 border border-red-700'
                  : 'bg-gray-700 text-gray-400 border border-gray-600 hover:border-gray-500'
              }`}
              title="Copy parlay to clipboard"
            >
              {copyStatus === 'copied' ? '✓ Copied!' : copyStatus === 'error' ? '✗ Failed' : '📋 Copy'}
            </button>
            {/* Share Button */}
            <button
              onClick={(e) => { e.stopPropagation(); handleShare(); }}
              disabled={isSharing}
              className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                shareUrl
                  ? 'bg-green-900/50 text-green-400 border border-green-700'
                  : 'bg-purple-900/50 text-purple-400 border border-purple-700 hover:bg-purple-800/50'
              }`}
            >
              {isSharing ? '...' : shareUrl ? '✓ Shared!' : '🔗 Share'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export function ParlayBuilder() {
  const { sportId, isLoading: sportLoading } = useSportContext();
  
  // Site mode state
  const [siteMode, setSiteMode] = useState<string>('prizepicks');
  const [entryType, setEntryType] = useState<EntryType>('power');
  
  // Filter state
  const [legCount, setLegCount] = useState(DEFAULT_PARLAY_FILTERS.legCount);
  const [include100Pct, setInclude100Pct] = useState(DEFAULT_PARLAY_FILTERS.include100Pct);
  const [minGrade, setMinGrade] = useState(DEFAULT_PARLAY_FILTERS.minGrade);
  const [maxResults, setMaxResults] = useState(DEFAULT_PARLAY_FILTERS.maxResults);
  const [blockCorrelated, setBlockCorrelated] = useState(DEFAULT_PARLAY_FILTERS.blockCorrelated);
  const [maxCorrelationRisk, setMaxCorrelationRisk] = useState(DEFAULT_PARLAY_FILTERS.maxCorrelationRisk);
  const [activePreset, setActivePreset] = useState<string | null>('pp3Power');
  
  // Reset all filters to default
  const resetFiltersToDefault = () => {
    setLegCount(DEFAULT_PARLAY_FILTERS.legCount);
    setInclude100Pct(DEFAULT_PARLAY_FILTERS.include100Pct);
    setMinGrade(DEFAULT_PARLAY_FILTERS.minGrade);
    setMaxResults(DEFAULT_PARLAY_FILTERS.maxResults);
    setBlockCorrelated(DEFAULT_PARLAY_FILTERS.blockCorrelated);
    setMaxCorrelationRisk(DEFAULT_PARLAY_FILTERS.maxCorrelationRisk);
    setActivePreset('pp3Power');
    setSiteMode('prizepicks');
    setEntryType('power');
  };
  
  // Session tracking
  const [selectedSlips, setSelectedSlips] = useState<Set<number>>(new Set());
  
  // Auto-generate state
  const [autoGenOpen, setAutoGenOpen] = useState(false);
  const [autoGenLoading, setAutoGenLoading] = useState(false);
  const [autoGenResult, setAutoGenResult] = useState<AutoGenerateSlipsResponse | null>(null);
  const [autoGenSlipCount, setAutoGenSlipCount] = useState(3);
  
  // Get current platform config
  const platformConfig = PLATFORM_CONFIGS[siteMode] || PLATFORM_CONFIGS.sportsbook;
  
  // Get payout multiplier for current settings
  const currentPayout = useMemo(() => {
    if (siteMode === 'sportsbook') return null;
    return platformConfig.payouts.find(
      p => p.legs === legCount && p.type === entryType
    );
  }, [siteMode, platformConfig, legCount, entryType]);
  
  // Calculate break-even per leg for current structure
  const breakEvenPerLeg = useMemo(() => {
    if (!currentPayout) return null;
    return calcBreakEvenPerLeg(currentPayout.multiplier, currentPayout.legs);
  }, [currentPayout]);
  
  // DFS-tuned presets by platform
  const DFS_PRESETS = {
    // PrizePicks presets
    pp2Power: { 
      legCount: 2, minGrade: 'A', entryType: 'power' as EntryType, site: 'prizepicks',
      label: 'PP 2-Power', desc: 'High edge only (3x payout, needs 6%+ edge/leg)',
      minEvPerLeg: 0.06, // Higher threshold due to worse structure
    },
    pp3Power: { 
      legCount: 3, minGrade: 'B', entryType: 'power' as EntryType, site: 'prizepicks',
      label: 'PP 3-Power', desc: 'Workhorse (5x payout, ~58% BE/leg)',
      minEvPerLeg: 0.03,
    },
    pp3Flex: { 
      legCount: 3, minGrade: 'B', entryType: 'flex' as EntryType, site: 'prizepicks',
      label: 'PP 3-Flex', desc: '3-pick flex (1.25x if 2/3 hit)',
      minEvPerLeg: 0.03,
    },
    pp5Flex: { 
      legCount: 5, minGrade: 'C', entryType: 'flex' as EntryType, site: 'prizepicks',
      label: 'PP 5-Flex', desc: 'Best flex value (can miss 2)',
      minEvPerLeg: 0.02,
    },
    // Sportsbook presets
    sb2Leg: { 
      legCount: 2, minGrade: 'A', entryType: 'power' as EntryType, site: 'sportsbook',
      label: '2-Leg Parlay', desc: 'Conservative sportsbook parlay',
      minEvPerLeg: 0.04,
    },
    sb3Leg: { 
      legCount: 3, minGrade: 'B', entryType: 'power' as EntryType, site: 'sportsbook',
      label: '3-Leg Parlay', desc: 'Standard sportsbook parlay',
      minEvPerLeg: 0.03,
    },
  };
  
  // Filter presets by current site mode
  const visiblePresets = Object.entries(DFS_PRESETS).filter(([, preset]) => 
    preset.site === siteMode || preset.site === 'sportsbook' && siteMode === 'sportsbook'
  );
  
  const applyPreset = (presetKey: string) => {
    const preset = DFS_PRESETS[presetKey as keyof typeof DFS_PRESETS];
    if (!preset) return;
    setLegCount(preset.legCount);
    setMinGrade(preset.minGrade);
    setEntryType(preset.entryType);
    setSiteMode(preset.site);
    setActivePreset(presetKey);
  };
  
  // Build filters
  const filters: ParlayBuilderFilters = useMemo(() => ({
    leg_count: legCount,
    include_100_pct: include100Pct,
    min_leg_grade: minGrade,
    max_results: maxResults,
    block_correlated: blockCorrelated,
    max_correlation_risk: maxCorrelationRisk,
  }), [legCount, include100Pct, minGrade, maxResults, blockCorrelated, maxCorrelationRisk]);
  
  // Fetch parlays
  const queryResult = useParlayBuilder(sportId, filters);
  const { data, isLoading, error, isFetching, status, fetchStatus } = queryResult;
  
  // CRITICAL: Derive display state with explicit null checks
  // React Query's isLoading is true when: fetching AND no cached data
  // We want to show spinner only during initial load, not refetches
  const parlays = data?.parlays ?? [];
  const totalCandidates = data?.total_candidates ?? 0;
  
  // Simple state machine:
  // 1. isLoading=true → show spinner (initial fetch, no cache)
  // 2. isLoading=false + error → show error
  // 3. isLoading=false + no error + parlays.length=0 → show empty state
  // 4. isLoading=false + no error + parlays.length>0 → show data
  const showSpinner = isLoading;
  const showError = !isLoading && !!error;
  const showEmpty = !isLoading && !error && parlays.length === 0;
  const showData = !isLoading && !error && parlays.length > 0;
  
  // Debug logging - log every render to help diagnose
  console.log('[ParlayBuilder] Render:', {
    sportId,
    status,
    fetchStatus,
    isLoading,
    isFetching,
    error: error?.message ?? null,
    dataExists: !!data,
    parlaysCount: parlays.length,
    totalCandidates,
    // What we'll show
    showSpinner,
    showError,
    showEmpty,
    showData,
  });
  
  if (sportLoading || !sportId) {
    return (
      <div className="p-8 text-center text-gray-400">
        Loading sports...
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      {/* Header + Site Mode */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Smart Parlay Builder</h2>
          <p className="text-sm text-gray-400">
            AI-optimized entries for DFS pick'em and sportsbooks
          </p>
        </div>
        
        {/* Site Mode Selector */}
        <div className="flex items-center gap-2 bg-gray-800/80 rounded-lg p-1">
          {Object.entries(PLATFORM_CONFIGS).map(([key, config]) => (
            <button
              key={key}
              onClick={() => {
                setSiteMode(key);
                // Auto-select best preset for this site
                if (key === 'prizepicks') applyPreset('pp3Power');
                else if (key === 'fliff' || key === 'underdog') applyPreset('pp3Power');
                else applyPreset('sb3Leg');
              }}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                siteMode === key
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              {config.name}
            </button>
          ))}
        </div>
      </div>
      
      {/* Live odds health banner */}
      <OddsHealthBanner sportId={sportId} />
      
      {/* Platform Info Bar */}
      {siteMode !== 'sportsbook' && (
        <div className="bg-purple-900/20 border border-purple-700/50 rounded-lg p-3 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-4">
            <div>
              <span className="text-xs text-purple-400">Platform</span>
              <div className="text-sm font-medium text-white">{platformConfig.name}</div>
            </div>
            {currentPayout && (
              <>
                <div>
                  <span className="text-xs text-purple-400">Payout</span>
                  <div className="text-sm font-medium text-green-400">{currentPayout.multiplier}x</div>
                </div>
                <div>
                  <span className="text-xs text-purple-400">Break-Even/Leg</span>
                  <div className="text-sm font-medium text-yellow-400">
                    {breakEvenPerLeg ? `${(breakEvenPerLeg * 100).toFixed(1)}%` : '-'}
                  </div>
                </div>
              </>
            )}
            <div>
              <span className="text-xs text-purple-400">House Edge</span>
              <div className="text-sm font-medium text-orange-400">{platformConfig.houseEdgeLabel}</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {platformConfig.bestStructures.includes(legCount) && (
              <span className="px-2 py-1 bg-green-900/50 text-green-400 text-xs rounded-full">
                ✓ Best Structure
              </span>
            )}
            {platformConfig.warnStructures.includes(legCount) && (
              <span className="px-2 py-1 bg-orange-900/50 text-orange-400 text-xs rounded-full">
                ⚠ High House Edge
              </span>
            )}
          </div>
        </div>
      )}
      
      {/* DFS-Tuned Presets + Auto-Generate Button */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs text-gray-500 self-center mr-2">Presets:</span>
        {visiblePresets.map(([key, preset]) => (
          <button
            key={key}
            onClick={() => applyPreset(key)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              activePreset === key
                ? 'bg-purple-600 text-white border-2 border-purple-400'
                : 'bg-gray-800 text-gray-300 border border-gray-700 hover:border-gray-500'
            }`}
            title={preset.desc}
          >
            {preset.label}
          </button>
        ))}
        <button
          onClick={() => setActivePreset(null)}
          className={`px-3 py-1.5 rounded-lg text-sm transition-all ${
            activePreset === null
              ? 'bg-gray-700 text-white border border-gray-500'
              : 'bg-gray-800/50 text-gray-500 border border-gray-700 hover:text-gray-300'
          }`}
        >
          Custom
        </button>
        <button
          onClick={resetFiltersToDefault}
          className="px-3 py-1.5 text-sm text-gray-400 hover:text-white border border-gray-600 rounded-lg hover:border-gray-500 transition-colors"
          title="Reset all filters to default"
        >
          ↺ Reset
        </button>
        
        {/* Auto-Generate Button - prominent one-click action */}
        <div className="ml-auto">
          <button
            onClick={() => setAutoGenOpen(true)}
            className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-semibold rounded-lg shadow-lg transition-all flex items-center gap-2"
          >
            <span>🚀</span>
            <span>Auto-Generate</span>
          </button>
        </div>
      </div>
      
      {/* Auto-Generate Modal */}
      {autoGenOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="p-4 border-b border-gray-700 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white">Auto-Generate Optimal Slips</h3>
                <p className="text-sm text-gray-400">
                  One-click: Generate {autoGenSlipCount} best {legCount}-leg slips for {platformConfig.name}
                </p>
              </div>
              <button
                onClick={() => {
                  setAutoGenOpen(false);
                  setAutoGenResult(null);
                }}
                className="text-gray-400 hover:text-white p-2"
              >
                ✕
              </button>
            </div>
            
            {/* Modal Body */}
            <div className="p-4 flex-1 overflow-y-auto">
              {/* Config before generating */}
              {!autoGenResult && !autoGenLoading && (
                <div className="space-y-4">
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-gray-300 mb-3">Generation Settings</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">Number of Slips</label>
                        <select
                          value={autoGenSlipCount}
                          onChange={(e) => setAutoGenSlipCount(Number(e.target.value))}
                          className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm"
                        >
                          <option value={1}>1 slip</option>
                          <option value={2}>2 slips</option>
                          <option value={3}>3 slips</option>
                          <option value={4}>4 slips</option>
                          <option value={5}>5 slips</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">Legs per Slip</label>
                        <div className="bg-gray-700 text-white rounded px-3 py-2 text-sm">
                          {legCount} legs
                        </div>
                      </div>
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">Platform</label>
                        <div className="bg-gray-700 text-white rounded px-3 py-2 text-sm">
                          {platformConfig.name}
                        </div>
                      </div>
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">Entry Type</label>
                        <div className="bg-gray-700 text-white rounded px-3 py-2 text-sm capitalize">
                          {entryType}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-3">
                    <div className="text-sm text-blue-300">
                      <strong>What happens:</strong> We'll find the best {autoGenSlipCount} non-overlapping {legCount}-leg parlays 
                      with 3%+ EV per leg and 55%+ model confidence. Each slip uses completely different legs.
                    </div>
                  </div>
                  
                  <button
                    onClick={async () => {
                      if (!sportId) return;
                      setAutoGenLoading(true);
                      try {
                        const result = await fetchAutoGenerateSlips(sportId, {
                          platform: siteMode,
                          leg_count: legCount,
                          slip_count: autoGenSlipCount,
                          min_leg_ev: 0.03,
                          min_confidence: 0.55,
                          allow_correlation: !blockCorrelated,
                        });
                        setAutoGenResult(result);
                      } catch (err) {
                        console.error('Auto-generate failed:', err);
                      } finally {
                        setAutoGenLoading(false);
                      }
                    }}
                    className="w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-bold rounded-lg shadow-lg transition-all"
                  >
                    Generate {autoGenSlipCount} Best Slips
                  </button>
                </div>
              )}
              
              {/* Loading state */}
              {autoGenLoading && (
                <div className="py-12 text-center">
                  <div className="animate-spin inline-block w-8 h-8 border-4 border-green-400 border-t-transparent rounded-full mb-4" />
                  <div className="text-gray-300">Generating optimal slips...</div>
                  <div className="text-xs text-gray-500 mt-1">Finding non-overlapping high-EV combinations</div>
                </div>
              )}
              
              {/* Results */}
              {autoGenResult && !autoGenLoading && (
                <div className="space-y-4">
                  {/* Quality indicator */}
                  <div className={`rounded-lg p-3 flex items-center gap-3 ${
                    autoGenResult.slate_quality === 'STRONG' ? 'bg-green-900/30 border border-green-700' :
                    autoGenResult.slate_quality === 'GOOD' ? 'bg-blue-900/30 border border-blue-700' :
                    autoGenResult.slate_quality === 'THIN' ? 'bg-yellow-900/30 border border-yellow-700' :
                    'bg-red-900/30 border border-red-700'
                  }`}>
                    <span className="text-2xl">
                      {autoGenResult.slate_quality === 'STRONG' ? '🔥' :
                       autoGenResult.slate_quality === 'GOOD' ? '✅' :
                       autoGenResult.slate_quality === 'THIN' ? '⚠️' : '❌'}
                    </span>
                    <div>
                      <div className="font-medium text-white">
                        Slate Quality: {autoGenResult.slate_quality}
                      </div>
                      <div className="text-xs text-gray-400">
                        {autoGenResult.slip_count} slips generated | Avg EV: {(autoGenResult.avg_slip_ev * 100).toFixed(1)}% | 
                        Suggested: {autoGenResult.total_suggested_units}u total
                      </div>
                    </div>
                  </div>
                  
                  {/* Generated slips */}
                  {autoGenResult.slips.length > 0 ? (
                    <div className="space-y-3">
                      {autoGenResult.slips.map((slip, idx) => (
                        <div key={idx} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-2">
                              <span className="text-lg font-bold text-white">Slip {idx + 1}</span>
                              <LabelBadge label={slip.label} />
                              <GradeBadge grade={slip.overall_grade} />
                            </div>
                            <div className="text-right">
                              <div className="text-green-400 font-medium">
                                EV: {(slip.parlay_ev * 100).toFixed(1)}%
                              </div>
                              <div className="text-xs text-gray-400">
                                {(slip.parlay_probability * 100).toFixed(1)}% hit rate
                              </div>
                            </div>
                          </div>
                          
                          {/* Legs */}
                          <div className="space-y-2">
                            {slip.legs.map((leg, legIdx) => (
                              <div key={legIdx} className="flex items-center justify-between py-1.5 px-2 bg-gray-700/50 rounded text-sm">
                                <div className="flex items-center gap-2">
                                  <span className="text-gray-500">{legIdx + 1}.</span>
                                  <span className="text-white">{leg.player_name}</span>
                                  <span className="text-gray-500">{leg.team_abbr}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className={`${leg.side === 'over' ? 'text-green-400' : 'text-red-400'}`}>
                                    {leg.side.toUpperCase()} {leg.line}
                                  </span>
                                  <span className="text-gray-400">{leg.stat_type.replace('player_', '').toUpperCase()}</span>
                                  <GradeBadge grade={leg.grade} />
                                </div>
                              </div>
                            ))}
                          </div>
                          
                          {/* Kelly suggestion */}
                          {slip.kelly && (
                            <div className="mt-3 pt-3 border-t border-gray-700 flex items-center justify-between text-xs">
                              <span className="text-gray-400">Suggested stake:</span>
                              <span className="text-yellow-400 font-medium">
                                {slip.kelly.suggested_units}u ({slip.kelly.risk_level})
                              </span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="py-8 text-center">
                      <div className="text-4xl mb-3">😬</div>
                      <div className="text-gray-300">No qualifying slips found</div>
                      <div className="text-xs text-gray-500 mt-1">
                        Try lowering leg count or passing on tonight's slate
                      </div>
                    </div>
                  )}
                  
                  {/* Reset button */}
                  <button
                    onClick={() => setAutoGenResult(null)}
                    className="w-full py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg text-sm"
                  >
                    Generate Again
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Filters */}
      <div className="bg-gray-800/50 rounded-lg p-4">
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
          {/* Entry Type (DFS only) */}
          {siteMode !== 'sportsbook' && (
            <div>
              <label className="block text-xs text-gray-400 mb-1">Entry Type</label>
              <div className="flex bg-gray-700 rounded p-0.5">
                <button
                  onClick={() => setEntryType('power')}
                  className={`flex-1 px-2 py-1.5 rounded text-xs font-medium transition-colors ${
                    entryType === 'power'
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Power
                </button>
                <button
                  onClick={() => setEntryType('flex')}
                  className={`flex-1 px-2 py-1.5 rounded text-xs font-medium transition-colors ${
                    entryType === 'flex'
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Flex
                </button>
              </div>
            </div>
          )}
          
          {/* Leg count */}
          <div>
            <label className="block text-xs text-gray-400 mb-1">Legs</label>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setLegCount(Math.max(2, legCount - 1))}
                className="px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-white"
              >
                -
              </button>
              <span className="text-white font-medium w-8 text-center">{legCount}</span>
              <button
                onClick={() => setLegCount(Math.min(6, legCount + 1))}
                className="px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-white"
              >
                +
              </button>
            </div>
          </div>
          
          {/* Min grade */}
          <div>
            <label className="block text-xs text-gray-400 mb-1">Min Grade</label>
            <select
              value={minGrade}
              onChange={e => setMinGrade(e.target.value)}
              className="w-full bg-gray-700 text-white rounded px-3 py-1.5 text-sm"
            >
              <option value="A">A (5%+ edge)</option>
              <option value="B">B (3%+ edge)</option>
              <option value="C">C (1%+ edge)</option>
              <option value="D">D (0%+ edge)</option>
            </select>
          </div>
          
          {/* 100% hit rate toggle */}
          <div>
            <label className="block text-xs text-gray-400 mb-1">100% Leg</label>
            <button
              onClick={() => setInclude100Pct(!include100Pct)}
              className={`w-full px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                include100Pct 
                  ? 'bg-green-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {include100Pct ? 'Required' : 'Optional'}
            </button>
          </div>
          
          {/* Max results */}
          <div>
            <label className="block text-xs text-gray-400 mb-1">Show Top</label>
            <select
              value={maxResults}
              onChange={e => setMaxResults(Number(e.target.value))}
              className="w-full bg-gray-700 text-white rounded px-3 py-1.5 text-sm"
            >
              <option value={3}>3 entries</option>
              <option value={5}>5 entries</option>
              <option value={10}>10 entries</option>
            </select>
          </div>
        </div>
        
        {/* Correlation controls - second row */}
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="flex items-center gap-6">
            {/* Block correlated toggle */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setBlockCorrelated(!blockCorrelated)}
                className={`relative w-10 h-5 rounded-full transition-colors ${
                  blockCorrelated ? 'bg-green-600' : 'bg-gray-600'
                }`}
              >
                <span className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full transition-transform ${
                  blockCorrelated ? 'translate-x-5' : ''
                }`} />
              </button>
              <span className="text-sm text-gray-300">Block correlated legs</span>
            </div>
            
            {/* Max correlation risk */}
            {blockCorrelated && (
              <div className="flex items-center gap-2">
                <label className="text-xs text-gray-400">Max risk:</label>
                <select
                  value={maxCorrelationRisk}
                  onChange={e => setMaxCorrelationRisk(e.target.value)}
                  className="bg-gray-700 text-white rounded px-2 py-1 text-sm"
                >
                  <option value="LOW">LOW (strictest)</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="HIGH">HIGH</option>
                  <option value="CRITICAL">CRITICAL (all allowed)</option>
                </select>
              </div>
            )}
            
            {/* Help text */}
            <div className="text-xs text-gray-500">
              {blockCorrelated 
                ? `Filtering out parlays with ${maxCorrelationRisk}+ correlation risk`
                : 'Showing all parlays with correlation warnings'
              }
            </div>
          </div>
        </div>
      </div>
      
      {/* Thin Slate Warning - when not enough quality legs */}
      {!isLoading && totalCandidates > 0 && totalCandidates < 10 && (
        <div className="bg-yellow-900/20 border border-yellow-700 rounded-lg p-3 flex items-center gap-3">
          <span className="text-yellow-400 text-lg">⚠️</span>
          <div>
            <div className="text-sm font-medium text-yellow-400">Slate is thin</div>
            <div className="text-xs text-yellow-500/80">
              Only {totalCandidates} eligible legs available. Consider 2-3 leg parlays or passing this slate.
            </div>
          </div>
        </div>
      )}
      
      {/* Loading state - spinner during initial fetch */}
      {showSpinner && (
        <div className="p-8 text-center text-gray-400">
          <div className="animate-spin inline-block w-6 h-6 border-2 border-gray-400 border-t-transparent rounded-full mr-2" />
          Building optimal parlays...
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
          <div>Error building parlays: {error?.message ?? 'Unknown error'}</div>
          <div className="text-sm text-gray-500 mt-2">
            Check browser console for details
          </div>
        </div>
      )}
      
      {/* Empty state - distinguish "no active slates" vs "filters too strict" */}
      {showEmpty && (
        <div className="p-8 text-center">
          {totalCandidates === 0 ? (
            // No active games/props for this sport
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6 max-w-md mx-auto">
              <div className="text-5xl mb-4">🗓️</div>
              <div className="text-gray-300 text-lg font-medium">No Active Slates</div>
              <div className="text-gray-500 text-sm mt-2 space-y-2">
                <p>There are no games starting within the next 24 hours for this sport.</p>
                <p className="text-gray-600">
                  Props are only available for upcoming games to ensure fresh odds.
                </p>
              </div>
              <button
                onClick={() => queryResult.refetch()}
                className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
              >
                Refresh
              </button>
            </div>
          ) : (
            // Props exist but filters are too strict
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6 max-w-md mx-auto">
              <div className="text-5xl mb-4">🎰</div>
              <div className="text-gray-300 text-lg font-medium">No Qualifying Parlays</div>
              <div className="text-gray-500 text-sm mt-2">
                <p><span className="text-white">{totalCandidates}</span> eligible legs available, but none meet your current filters.</p>
                <p className="mt-2">Try lowering the minimum grade or leg count.</p>
              </div>
              <button
                onClick={resetFiltersToDefault}
                className="mt-4 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white text-sm rounded-lg transition-colors"
              >
                Reset Filters
              </button>
            </div>
          )}
        </div>
      )}
      
      {/* Parlays list - only show when we have actual data */}
      {showData && (
        <div className="space-y-4">
          {/* Summary bar */}
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">
              Built from <span className="text-white font-medium">{data?.total_candidates ?? 0}</span> eligible legs
            </span>
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 bg-green-500 rounded-full" />
                <span className="text-gray-400">LOCK</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 bg-blue-500 rounded-full" />
                <span className="text-gray-400">PLAY</span>
              </span>
            </div>
          </div>
          
          {/* Session Risk Panel */}
          {selectedSlips.size > 0 && (
            <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-700/50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-6">
                  <div>
                    <div className="text-xs text-purple-400">Slips Selected</div>
                    <div className="text-2xl font-bold text-white">{selectedSlips.size}</div>
                  </div>
                  <div>
                    <div className="text-xs text-purple-400">Total Risk</div>
                    <div className="text-2xl font-bold text-yellow-400">
                      {(() => {
                        const totalUnits = Array.from(selectedSlips).reduce((sum, idx) => {
                          const p = parlays[idx];
                          return sum + (p?.kelly?.suggested_units ?? 0);
                        }, 0);
                        return `${totalUnits.toFixed(1)}u`;
                      })()}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-purple-400">Avg EV</div>
                    <div className={`text-2xl font-bold ${
                      (() => {
                        const selected = Array.from(selectedSlips).map(idx => parlays[idx]).filter(Boolean);
                        const avgEv = selected.length > 0 
                          ? selected.reduce((sum, p) => {
                              const ev = currentPayout 
                                ? calcStructureEV(p.parlay_probability, currentPayout.multiplier)
                                : p.parlay_ev;
                              return sum + ev;
                            }, 0) / selected.length
                          : 0;
                        return avgEv > 0.03 ? 'text-green-400' : avgEv > 0 ? 'text-yellow-400' : 'text-red-400';
                      })()
                    }`}>
                      {(() => {
                        const selected = Array.from(selectedSlips).map(idx => parlays[idx]).filter(Boolean);
                        const avgEv = selected.length > 0 
                          ? selected.reduce((sum, p) => {
                              const ev = currentPayout 
                                ? calcStructureEV(p.parlay_probability, currentPayout.multiplier)
                                : p.parlay_ev;
                              return sum + ev;
                            }, 0) / selected.length
                          : 0;
                        return `${avgEv > 0 ? '+' : ''}${(avgEv * 100).toFixed(1)}%`;
                      })()}
                    </div>
                  </div>
                </div>
                <div className="flex flex-col gap-2">
                  {/* Warning if risk is high */}
                  {(() => {
                    const totalUnits = Array.from(selectedSlips).reduce((sum, idx) => {
                      const p = parlays[idx];
                      return sum + (p?.kelly?.suggested_units ?? 0);
                    }, 0);
                    if (totalUnits > 5) {
                      return (
                        <div className="text-xs text-orange-400 bg-orange-900/30 px-3 py-1 rounded">
                          ⚠ High exposure ({totalUnits.toFixed(1)}u total)
                        </div>
                      );
                    }
                    return null;
                  })()}
                  <button
                    onClick={() => setSelectedSlips(new Set())}
                    className="text-xs text-gray-400 hover:text-white px-3 py-1 bg-gray-700 rounded"
                  >
                    Clear Selection
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {/* Parlay cards */}
          {parlays.map((parlay, index) => (
            <ParlayCard 
              key={index} 
              parlay={parlay} 
              index={index}
              siteMode={siteMode}
              entryType={entryType}
              platformPayout={currentPayout ?? null}
              onSelect={(idx) => {
                const newSet = new Set(selectedSlips);
                if (newSet.has(idx)) newSet.delete(idx);
                else newSet.add(idx);
                setSelectedSlips(newSet);
              }}
              isSelected={selectedSlips.has(index)}
            />
          ))}
        </div>
      )}
      
      {/* Legend */}
      <div className="bg-gray-800/30 rounded-lg p-4 text-xs text-gray-500">
        <div className="font-medium text-gray-400 mb-2">How the Smart Parlay Builder works:</div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          <div>
            <span className="text-green-400">LOCK</span>: All legs 2%+ edge, parlay EV 3%+
          </div>
          <div>
            <span className="text-blue-400">PLAY</span>: Parlay EV 1%+, moderate risk
          </div>
          <div>
            <span className="font-medium">Grades</span>: A (5%+) B (3%+) C (1%+) D (0%+)
          </div>
        </div>
      </div>
    </div>
  );
}

export default ParlayBuilder;
