/**
 * FullSlateReview - Multi-sport prop review component.
 * 
 * Displays all player props across all sports for a specific date,
 * grouped by sport with collapsible sections.
 */

import { useState, useMemo } from 'react';
import { useFullSlate, SportSlate, PlayerPropPick } from '../api/public';
import { SPORT_CONFIG } from '../constants/sports';

// Format helpers
const formatPercent = (v: number | null) => v !== null ? `${(v * 100).toFixed(1)}%` : '-';
const formatOdds = (odds: number) => odds > 0 ? `+${odds}` : odds.toString();

interface FullSlateReviewProps {
  date: string;
  minEv?: number;
  minConfidence?: number;
}

// Individual prop row
function PropRow({ prop }: { prop: PlayerPropPick }) {
  const evColor = prop.expected_value > 0.05 ? 'text-green-400' : 
                  prop.expected_value > 0 ? 'text-green-300' : 'text-gray-400';
  
  return (
    <div className="flex items-center justify-between py-2 px-3 bg-gray-900/50 rounded border border-gray-700/50 hover:border-gray-600 transition-colors">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-white font-medium truncate">{prop.player_name}</span>
          <span className="text-xs text-gray-500">
            {prop.team_abbr || prop.team}
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400 mt-0.5">
          <span>{prop.stat_type}</span>
          <span className={`px-1.5 py-0.5 rounded ${
            prop.side === 'over' ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'
          }`}>
            {prop.side.toUpperCase()} {prop.line}
          </span>
          <span>{formatOdds(prop.odds)}</span>
        </div>
      </div>
      <div className="text-right ml-4">
        <div className={`font-bold ${evColor}`}>
          +{formatPercent(prop.expected_value)}
        </div>
        <div className="text-xs text-gray-500">
          {formatPercent(prop.model_probability)} prob
        </div>
      </div>
    </div>
  );
}

// Sport section with collapsible props
function SportSection({ slate, defaultExpanded = false }: { slate: SportSlate; defaultExpanded?: boolean }) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const config = SPORT_CONFIG[slate.sport_id] || { name: slate.sport_name, icon: '🎮', color: 'bg-gray-700 text-gray-300' };
  
  // Sort props by EV
  const sortedProps = useMemo(() => {
    return [...slate.props].sort((a, b) => b.expected_value - a.expected_value);
  }, [slate.props]);
  
  // Calculate section stats
  const stats = useMemo(() => {
    if (sortedProps.length === 0) return null;
    const avgEv = sortedProps.reduce((sum, p) => sum + p.expected_value, 0) / sortedProps.length;
    const bestEv = sortedProps[0]?.expected_value || 0;
    return { avgEv, bestEv };
  }, [sortedProps]);
  
  if (slate.count === 0) return null;
  
  return (
    <div className="bg-gray-800/50 rounded-lg border border-gray-700 overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-700/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className={`px-2 py-1 rounded text-sm ${config.color}`}>
            {config.icon} {config.name}
          </span>
          <span className="text-white font-medium">
            {slate.count} props
          </span>
          {stats && (
            <span className="text-xs text-gray-400">
              Best: <span className="text-green-400">+{formatPercent(stats.bestEv)}</span>
              {' · '}
              Avg: <span className="text-green-300">+{formatPercent(stats.avgEv)}</span>
            </span>
          )}
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {/* Props list */}
      {expanded && (
        <div className="border-t border-gray-700 p-3 space-y-2 max-h-96 overflow-y-auto">
          {sortedProps.map((prop, idx) => (
            <PropRow key={`${prop.pick_id}-${idx}`} prop={prop} />
          ))}
        </div>
      )}
    </div>
  );
}

export function FullSlateReview({ date, minEv = 0, minConfidence = 0 }: FullSlateReviewProps) {
  const { data, isLoading, error } = useFullSlate(date, minEv, minConfidence);
  
  // Loading state
  if (isLoading) {
    return (
      <div className="bg-gray-800/30 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="animate-spin w-5 h-5 border-2 border-purple-400 border-t-transparent rounded-full" />
          <span className="text-gray-400">Loading slate for {date}...</span>
        </div>
        <div className="animate-pulse space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-700/50 rounded" />
          ))}
        </div>
      </div>
    );
  }
  
  // Error state
  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 text-red-400">
        Failed to load slate: {error instanceof Error ? error.message : 'Unknown error'}
      </div>
    );
  }
  
  // Empty state
  if (!data || data.total_props === 0) {
    return (
      <div className="bg-gray-800/30 rounded-lg p-8 text-center">
        <div className="text-4xl mb-3">📋</div>
        <p className="text-gray-400 text-lg">No props available for {date}</p>
        <p className="text-sm text-gray-500 mt-2">
          Lines may not be posted yet or no games scheduled.
        </p>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Full Slate Review</h2>
          <p className="text-sm text-gray-400">
            {data.total_props} props across {data.sports.filter(s => s.count > 0).length} sports for {date}
          </p>
        </div>
        
        {/* Summary stats */}
        <div className="flex items-center gap-4 text-sm">
          {data.sports.filter(s => s.count > 0).slice(0, 4).map(sport => {
            const config = SPORT_CONFIG[sport.sport_id] || { icon: '🎮' };
            return (
              <span key={sport.sport_id} className="text-gray-400">
                {config.icon} {sport.count}
              </span>
            );
          })}
        </div>
      </div>
      
      {/* Sport sections */}
      <div className="space-y-3">
        {data.sports
          .filter(s => s.count > 0)
          .map((slate, idx) => (
            <SportSection
              key={slate.sport_id}
              slate={slate}
              defaultExpanded={idx === 0}  // Expand first sport by default
            />
          ))}
      </div>
    </div>
  );
}

export default FullSlateReview;
