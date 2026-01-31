import { useState, useMemo } from 'react';
import { useParlayBuilder, ParlayBuilderFilters, ParlayRecommendation, ParlayLeg, CorrelationWarning } from '../api/public';
import { useSportContext } from '../context/SportContext';

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
function LegCard({ leg, index }: { leg: ParlayLeg; index: number }) {
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
          <div className="text-white font-medium">{formatOdds(leg.odds)}</div>
          <div className="text-xs text-gray-500">{formatPercent(leg.win_prob)} prob</div>
        </div>
        <GradeBadge grade={leg.grade} />
        {leg.is_100_last_5 && (
          <span className="px-1.5 py-0.5 text-xs bg-green-900/50 text-green-400 rounded">
            100% L5
          </span>
        )}
      </div>
    </div>
  );
}

// Parlay card component
function ParlayCard({ parlay, index }: { parlay: ParlayRecommendation; index: number }) {
  const [isExpanded, setIsExpanded] = useState(index === 0); // First one expanded by default
  
  return (
    <div className={`border rounded-lg overflow-hidden transition-all ${
      parlay.label === 'LOCK' 
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
            <span className="text-gray-500 text-lg font-medium">#{index + 1}</span>
            <LabelBadge label={parlay.label} />
            <GradeBadge grade={parlay.overall_grade} />
            <CorrelationRiskBadge 
              risk={parlay.correlation_risk} 
              label={parlay.correlation_risk_label} 
            />
          </div>
          
          <div className="flex items-center gap-6">
            {/* Odds */}
            <div className="text-right">
              <div className="text-xl font-bold text-white">
                {formatOdds(parlay.total_odds)}
              </div>
              <div className="text-xs text-gray-500">
                {parlay.decimal_odds.toFixed(2)}x payout
              </div>
            </div>
            
            {/* Win Prob */}
            <div className="text-right">
              <div className="text-lg font-medium text-blue-400">
                {formatPercent(parlay.parlay_probability)}
              </div>
              <div className="text-xs text-gray-500">win prob</div>
            </div>
            
            {/* EV */}
            <div className="text-right">
              <div className={`text-lg font-medium ${parlay.parlay_ev > 0 ? 'text-green-400' : 'text-red-400'}`}>
                {parlay.parlay_ev > 0 ? '+' : ''}{formatPercent(parlay.parlay_ev)}
              </div>
              <div className="text-xs text-gray-500">EV</div>
            </div>
            
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
            <LegCard key={leg.pick_id} leg={leg} index={legIndex} />
          ))}
          
          {/* Correlation warnings */}
          {parlay.correlations && parlay.correlations.length > 0 && (
            <CorrelationWarningCard warnings={parlay.correlations} />
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
          </div>
        </div>
      )}
    </div>
  );
}

export function ParlayBuilder() {
  const { sportId, isLoading: sportLoading } = useSportContext();
  
  // Filter state
  const [legCount, setLegCount] = useState(3);
  const [include100Pct, setInclude100Pct] = useState(false);
  const [minGrade, setMinGrade] = useState('C');
  const [maxResults, setMaxResults] = useState(5);
  const [blockCorrelated, setBlockCorrelated] = useState(true);
  const [maxCorrelationRisk, setMaxCorrelationRisk] = useState('MEDIUM');
  
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
  const { data, isLoading, error } = useParlayBuilder(sportId, filters);
  
  // Log state for debugging
  console.log('[ParlayBuilder] State:', {
    sportId,
    sportLoading,
    filters,
    parlaysCount: data?.parlays?.length,
    totalCandidates: data?.total_candidates,
    isLoading,
    error: error?.message,
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
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Smart Parlay Builder</h2>
          <p className="text-sm text-gray-400">
            AI-optimized parlays with grading and LOCK/PLAY/SKIP recommendations
          </p>
        </div>
      </div>
      
      {/* Filters */}
      <div className="bg-gray-800/50 rounded-lg p-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
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
                onClick={() => setLegCount(Math.min(15, legCount + 1))}
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
              <option value={3}>3 parlays</option>
              <option value={5}>5 parlays</option>
              <option value={10}>10 parlays</option>
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
      
      {/* Loading state */}
      {isLoading && (
        <div className="p-8 text-center text-gray-400">
          <div className="animate-spin inline-block w-6 h-6 border-2 border-gray-400 border-t-transparent rounded-full mr-2" />
          Building optimal parlays...
        </div>
      )}
      
      {/* Error state */}
      {error && (
        <div className="p-8 text-center text-red-400">
          Error building parlays: {error.message}
        </div>
      )}
      
      {/* Empty state */}
      {!isLoading && !error && data?.parlays?.length === 0 && (
        <div className="p-8 text-center">
          <div className="text-5xl mb-4">🎰</div>
          <div className="text-gray-400 text-lg">No qualifying parlays found</div>
          <div className="text-gray-500 text-sm mt-2">
            Try lowering the minimum grade or leg count
          </div>
        </div>
      )}
      
      {/* Parlays list */}
      {!isLoading && !error && data && data.parlays.length > 0 && (
        <div className="space-y-4">
          {/* Summary bar */}
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">
              Built from <span className="text-white font-medium">{data.total_candidates}</span> eligible legs
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
          
          {/* Parlay cards */}
          {data.parlays.map((parlay, index) => (
            <ParlayCard key={index} parlay={parlay} index={index} />
          ))}
        </div>
      )}
      
      {/* Legend */}
      <div className="bg-gray-800/30 rounded-lg p-4 text-xs text-gray-500">
        <div className="font-medium text-gray-400 mb-2">How it works:</div>
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
