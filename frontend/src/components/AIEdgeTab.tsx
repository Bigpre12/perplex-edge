/**
 * AIEdgeTab — AI-powered prop recommendations.
 *
 * Calls the /api/v1/ai/recommendations endpoint and displays
 * individual and parlay recommendations with confidence labels,
 * edge percentages, and signal source badges.
 */

import { useState } from 'react';
import { useSportContext } from '../context/SportContext';
import {
  useAIRecommendations,
  AIRecommendation,
  ParlayRecommendation,
  ConfidenceLabel,
  RiskProfile,
} from '../api/ai';
import { STAT_TYPE_LABELS } from '../config/sports';
import type { StatType } from '../config/sports';

// =============================================================================
// Helpers
// =============================================================================

function confidenceColor(label: ConfidenceLabel): string {
  switch (label) {
    case 'high':
      return 'text-green-400 bg-green-900/40';
    case 'medium':
      return 'text-blue-400 bg-blue-900/40';
    case 'low':
      return 'text-amber-400 bg-amber-900/40';
  }
}

function formatEdge(edge: number | null): string {
  if (edge === null || edge === undefined) return '—';
  return `+${(edge * 100).toFixed(1)}%`;
}

function formatStatLabel(statType: string): string {
  return STAT_TYPE_LABELS[statType as StatType] ?? statType.toUpperCase();
}

// =============================================================================
// Sub-components
// =============================================================================

function SignalBadge({ source }: { source: string }) {
  const isAI = source === 'ai_assisted';
  return (
    <span
      className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium ${
        isAI
          ? 'bg-purple-900/50 text-purple-300'
          : 'bg-gray-700 text-gray-400'
      }`}
    >
      {isAI ? '✦ AI' : '⚙ Model'}
    </span>
  );
}

function RecommendationCard({ rec }: { rec: AIRecommendation }) {
  return (
    <div className="bg-gray-800/60 border border-gray-700 rounded-lg p-4 hover:border-gray-600 transition-colors">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-white font-medium text-sm truncate">
              {rec.player_name}
            </span>
            <SignalBadge source={rec.signal_source} />
          </div>
          <div className="text-xs text-gray-400">
            {formatStatLabel(rec.stat_type)}{' '}
            <span className={rec.side === 'over' ? 'text-green-400' : 'text-red-400'}>
              {rec.side.toUpperCase()}
            </span>{' '}
            {rec.line}
          </div>
          {rec.reasoning && (
            <p className="text-xs text-gray-500 mt-2 line-clamp-2">{rec.reasoning}</p>
          )}
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          <span
            className={`px-2 py-0.5 rounded text-xs font-bold ${confidenceColor(rec.confidence_label)}`}
          >
            {rec.confidence_label.toUpperCase()}
          </span>
          {rec.edge_pct !== null && (
            <span className="text-green-400 text-sm font-bold">
              {formatEdge(rec.edge_pct)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

function ParlayCard({ parlay }: { parlay: ParlayRecommendation }) {
  return (
    <div className="bg-gray-800/60 border border-gray-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-white font-medium text-sm">
            {parlay.legs.length}-Leg Parlay
          </span>
          <span
            className={`px-2 py-0.5 rounded text-xs font-bold ${confidenceColor(parlay.confidence_label)}`}
          >
            {parlay.confidence_label.toUpperCase()}
          </span>
        </div>
        {parlay.combined_ev !== null && (
          <span className="text-green-400 text-sm font-bold">
            EV {formatEdge(parlay.combined_ev)}
          </span>
        )}
      </div>
      <div className="space-y-1.5">
        {parlay.legs.map((leg, i) => (
          <div
            key={`${leg.player_name}-${leg.stat_type}-${i}`}
            className="flex items-center justify-between text-xs"
          >
            <span className="text-gray-300">
              {leg.player_name} — {formatStatLabel(leg.stat_type)}{' '}
              <span className={leg.side === 'over' ? 'text-green-400' : 'text-red-400'}>
                {leg.side.toUpperCase()}
              </span>{' '}
              {leg.line}
            </span>
            {leg.edge_pct !== null && (
              <span className="text-green-400/70">{formatEdge(leg.edge_pct)}</span>
            )}
          </div>
        ))}
      </div>
      {parlay.reasoning && (
        <p className="text-xs text-gray-500 mt-2">{parlay.reasoning}</p>
      )}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function AIEdgeTab() {
  const { sportId } = useSportContext();
  const [riskProfile, setRiskProfile] = useState<RiskProfile>('moderate');
  const [minEv, setMinEv] = useState(0.03);

  const { data, isLoading, error, isFetching } = useAIRecommendations(sportId, {
    risk_profile: riskProfile,
    min_ev: minEv,
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span className="text-purple-400">✦</span> AI Edge
          </h2>
          <p className="text-sm text-gray-400">
            AI-assisted prop recommendations powered by Perplex Edge
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3">
          <select
            value={riskProfile}
            onChange={(e) => setRiskProfile(e.target.value as RiskProfile)}
            className="bg-gray-700 text-white text-sm rounded px-3 py-1.5 border border-gray-600 focus:border-purple-500 focus:outline-none"
          >
            <option value="conservative">Conservative</option>
            <option value="moderate">Moderate</option>
            <option value="aggressive">Aggressive</option>
          </select>

          <select
            value={minEv}
            onChange={(e) => setMinEv(parseFloat(e.target.value))}
            className="bg-gray-700 text-white text-sm rounded px-3 py-1.5 border border-gray-600 focus:border-purple-500 focus:outline-none"
          >
            <option value={0.01}>1%+ EV</option>
            <option value={0.03}>3%+ EV</option>
            <option value={0.05}>5%+ EV</option>
            <option value={0.1}>10%+ EV</option>
          </select>

          {isFetching && (
            <div className="w-4 h-4 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
          )}
        </div>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-8">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-gray-400">Analyzing props with AI...</p>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-4">
          <p className="text-sm text-red-400">
            {error instanceof Error ? error.message : 'Failed to load AI recommendations'}
          </p>
        </div>
      )}

      {/* Warnings */}
      {data?.warnings && data.warnings.length > 0 && (
        <div className="bg-amber-900/20 border border-amber-800 rounded-lg p-4">
          {data.warnings.map((w, i) => (
            <p key={i} className="text-sm text-amber-400">
              {w}
            </p>
          ))}
        </div>
      )}

      {/* Individual Recommendations */}
      {data && data.individual.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-3">
            Individual Picks ({data.individual.length})
          </h3>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data.individual.map((rec, i) => (
              <RecommendationCard key={`${rec.player_name}-${rec.stat_type}-${i}`} rec={rec} />
            ))}
          </div>
        </div>
      )}

      {/* Parlay Recommendations */}
      {data && data.parlays.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-3">
            Parlay Suggestions ({data.parlays.length})
          </h3>
          <div className="grid gap-3 sm:grid-cols-2">
            {data.parlays.map((parlay, i) => (
              <ParlayCard key={i} parlay={parlay} />
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {data && data.individual.length === 0 && data.parlays.length === 0 && data.warnings.length === 0 && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
          <p className="text-gray-400">No AI recommendations available for the current filters.</p>
          <p className="text-xs text-gray-500 mt-2">Try lowering the minimum EV or changing the risk profile.</p>
        </div>
      )}

      {/* Footer */}
      {data && (
        <div className="text-xs text-gray-500 flex items-center justify-between">
          <span>
            {data.ai_model && `Model: ${data.ai_model}`}
          </span>
          <span>
            {data.generated_at && `Generated: ${new Date(data.generated_at).toLocaleTimeString()}`}
          </span>
        </div>
      )}
    </div>
  );
}

export default AIEdgeTab;
