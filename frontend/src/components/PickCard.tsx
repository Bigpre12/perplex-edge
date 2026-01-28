import { useState } from 'react';
import { ConfidenceBadge } from './ConfidenceBadge';

interface PickCardProps {
  id: number;
  playerName: string;
  team: string;
  teamAbbr?: string | null;
  opponent: string;
  opponentAbbr?: string | null;
  statType: string;
  line: number;
  side: string;
  odds: number;
  modelProbability: number;
  impliedProbability: number;
  expectedValue: number;
  hitRate30d?: number | null;
  hitRate10g?: number | null;
  confidence: number;
  gameStartTime: string;
  pickType?: string;
}

export function PickCard({
  playerName,
  team,
  teamAbbr,
  opponent,
  opponentAbbr,
  statType,
  line,
  side,
  odds,
  modelProbability,
  impliedProbability,
  expectedValue,
  hitRate30d,
  hitRate10g,
  confidence,
  gameStartTime,
  pickType,
}: PickCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Format helpers
  const formatOdds = (o: number) => (o > 0 ? `+${o}` : o.toString());
  const formatPercent = (value: number | null | undefined) =>
    value !== null && value !== undefined ? `${(value * 100).toFixed(1)}%` : '-';
  const formatTime = (iso: string) => {
    const date = new Date(iso);
    return date.toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // EV color coding: green (>5%), yellow (2-5%), gray (<2%)
  const evPercentage = expectedValue * 100;
  const getEvColorClass = () => {
    if (evPercentage >= 5) return 'bg-green-900/50 border-green-700 text-green-400';
    if (evPercentage >= 2) return 'bg-yellow-900/50 border-yellow-700 text-yellow-400';
    return 'bg-gray-800 border-gray-700 text-gray-400';
  };

  const getEvBadgeClass = () => {
    if (evPercentage >= 5) return 'bg-green-500 text-white';
    if (evPercentage >= 2) return 'bg-yellow-500 text-black';
    return 'bg-gray-600 text-gray-300';
  };

  return (
    <div
      className={`rounded-lg border transition-all cursor-pointer ${getEvColorClass()}`}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      {/* Main Card Content */}
      <div className="p-4">
        <div className="flex items-start justify-between gap-4">
          {/* Left: Player Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="text-white font-semibold text-lg truncate">{playerName}</h3>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${getEvBadgeClass()}`}>
                {evPercentage.toFixed(1)}% EV
              </span>
            </div>
            <p className="text-sm text-gray-400 mt-1">
              {teamAbbr || team} vs {opponentAbbr || opponent}
            </p>
            <p className="text-xs text-gray-500 mt-0.5">{formatTime(gameStartTime)}</p>
          </div>

          {/* Center: Pick Details */}
          <div className="flex items-center gap-4 text-center">
            <div>
              <span className="bg-blue-900/50 text-blue-400 text-xs px-2 py-0.5 rounded">
                {statType}
              </span>
              <p className="text-white font-bold text-xl mt-1">{line}</p>
              <span
                className={`px-2 py-0.5 rounded text-xs font-medium ${
                  side === 'over'
                    ? 'bg-green-900/50 text-green-400'
                    : 'bg-red-900/50 text-red-400'
                }`}
              >
                {side.toUpperCase()}
              </span>
            </div>

            <div>
              <p className="text-xs text-gray-500 uppercase">Odds</p>
              <p
                className={`font-bold text-lg ${odds > 0 ? 'text-green-400' : 'text-white'}`}
              >
                {formatOdds(odds)}
              </p>
            </div>
          </div>

          {/* Right: Probabilities & Confidence */}
          <div className="text-right">
            <div className="flex items-center justify-end gap-2">
              <span className="text-xs text-gray-500">Confidence:</span>
              <ConfidenceBadge score={confidence} />
            </div>
            <div className="mt-2 text-sm">
              <p>
                <span className="text-gray-500">Model:</span>{' '}
                <span className="text-green-400 font-medium">{formatPercent(modelProbability)}</span>
              </p>
              <p>
                <span className="text-gray-500">Implied:</span>{' '}
                <span className="text-gray-300">{formatPercent(impliedProbability)}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Expand Indicator */}
        <div className="flex items-center justify-center mt-3 pt-2 border-t border-gray-700/50">
          <span className="text-xs text-gray-500">
            {isExpanded ? '▲ Click to collapse' : '▼ Click to expand'}
          </span>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-gray-700 p-4 bg-gray-900/50">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Hit Rates */}
            <div>
              <p className="text-xs text-gray-500 uppercase mb-1">Hit Rate (30d)</p>
              <p className="text-lg font-semibold text-white">{formatPercent(hitRate30d)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase mb-1">Hit Rate (10g)</p>
              <p className="text-lg font-semibold text-white">{formatPercent(hitRate10g)}</p>
            </div>

            {/* Edge */}
            <div>
              <p className="text-xs text-gray-500 uppercase mb-1">Edge</p>
              <p
                className={`text-lg font-semibold ${
                  modelProbability > impliedProbability ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {formatPercent(modelProbability - impliedProbability)}
              </p>
            </div>

            {/* Pick Type */}
            <div>
              <p className="text-xs text-gray-500 uppercase mb-1">Pick Type</p>
              <p className="text-lg font-semibold text-white capitalize">
                {pickType?.replace('_', ' ') || 'Player Prop'}
              </p>
            </div>
          </div>

          {/* Reasoning */}
          <div className="mt-4 p-3 bg-gray-800 rounded-lg">
            <p className="text-xs text-gray-500 uppercase mb-2">Model Reasoning</p>
            <p className="text-sm text-gray-300">
              {modelProbability > impliedProbability ? (
                <>
                  Model projects a <span className="text-green-400 font-medium">{formatPercent(modelProbability)}</span> chance 
                  of hitting this line, compared to the implied probability of {formatPercent(impliedProbability)} from 
                  the odds ({formatOdds(odds)}). This represents a{' '}
                  <span className="text-green-400 font-medium">{formatPercent(modelProbability - impliedProbability)}</span> edge.
                </>
              ) : (
                <>
                  Model projects {formatPercent(modelProbability)} probability, which is below the implied {formatPercent(impliedProbability)}.
                </>
              )}
              {hitRate10g && (
                <> Historical performance shows a {formatPercent(hitRate10g)} hit rate over the last 10 games.</>
              )}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default PickCard;
