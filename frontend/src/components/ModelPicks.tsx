import { useEffect, useState } from 'react';
import { api, PickList, PickSummary } from '../api/client';

export function ModelPicks() {
  const [picks, setPicks] = useState<PickList | null>(null);
  const [summary, setSummary] = useState<PickSummary | null>(null);
  const [minConfidence, setMinConfidence] = useState<number>(0);
  const [minEV, setMinEV] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [picksData, summaryData] = await Promise.all([
          api.getPicks({
            min_confidence: minConfidence,
            min_ev: minEV,
            limit: 50,
          }),
          api.getPicksSummary(),
        ]);
        setPicks(picksData);
        setSummary(summaryData);
      } catch (err) {
        console.error('Failed to fetch picks:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [minConfidence, minEV]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <StatBadge label="Active Picks" value={summary.active_picks} />
          <StatBadge label="High Confidence" value={summary.high_confidence_picks} />
          <StatBadge label="Avg EV" value={`${(summary.avg_ev * 100).toFixed(1)}%`} />
          <StatBadge label="Avg Confidence" value={`${(summary.avg_confidence * 100).toFixed(0)}%`} />
          <StatBadge label="Total Picks" value={summary.total_picks} />
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-4 bg-gray-800 rounded-lg p-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Min Confidence</label>
          <select
            value={minConfidence}
            onChange={(e) => setMinConfidence(Number(e.target.value))}
            className="bg-gray-700 text-white rounded px-3 py-2"
          >
            <option value={0}>All</option>
            <option value={0.5}>50%+</option>
            <option value={0.6}>60%+</option>
            <option value={0.7}>70%+</option>
            <option value={0.8}>80%+</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Min EV</label>
          <select
            value={minEV}
            onChange={(e) => setMinEV(Number(e.target.value))}
            className="bg-gray-700 text-white rounded px-3 py-2"
          >
            <option value={0}>All</option>
            <option value={0.02}>2%+</option>
            <option value={0.05}>5%+</option>
            <option value={0.1}>10%+</option>
          </select>
        </div>
      </div>

      {/* Picks List */}
      {picks && picks.items.length > 0 ? (
        <div className="space-y-3">
          {picks.items.map((pick) => (
            <div
              key={pick.id}
              className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition"
            >
              <div className="flex flex-wrap justify-between items-start gap-4">
                {/* Game Info */}
                <div>
                  <p className="text-white font-medium">
                    {pick.away_team} @ {pick.home_team}
                  </p>
                  <p className="text-sm text-gray-400">
                    {new Date(pick.game_time).toLocaleString([], {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>

                {/* Pick Details */}
                <div className="text-right">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400">{pick.market_type}</span>
                    {pick.stat_type && (
                      <span className="bg-blue-900/50 text-blue-400 text-xs px-2 py-0.5 rounded">
                        {pick.stat_type}
                      </span>
                    )}
                  </div>
                  {pick.player_name && (
                    <p className="text-white">{pick.player_name}</p>
                  )}
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-gray-700 grid grid-cols-2 md:grid-cols-5 gap-4">
                {/* Side & Line */}
                <div>
                  <p className="text-xs text-gray-400">Pick</p>
                  <p className="text-white font-medium capitalize">
                    {pick.side} {pick.line_value !== null ? pick.line_value : ''}
                  </p>
                </div>

                {/* Odds */}
                <div>
                  <p className="text-xs text-gray-400">Odds</p>
                  <p className={`font-medium ${pick.odds > 0 ? 'text-green-400' : 'text-white'}`}>
                    {pick.odds > 0 ? `+${pick.odds}` : pick.odds}
                  </p>
                </div>

                {/* EV */}
                <div>
                  <p className="text-xs text-gray-400">Expected Value</p>
                  <p className={`font-medium ${pick.expected_value > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {(pick.expected_value * 100).toFixed(1)}%
                  </p>
                </div>

                {/* Confidence */}
                <div>
                  <p className="text-xs text-gray-400">Confidence</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          pick.confidence_score >= 0.7
                            ? 'bg-green-500'
                            : pick.confidence_score >= 0.5
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${pick.confidence_score * 100}%` }}
                      />
                    </div>
                    <span className="text-white text-sm">
                      {(pick.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

                {/* Model vs Implied */}
                <div>
                  <p className="text-xs text-gray-400">Model vs Implied</p>
                  <p className="text-sm">
                    <span className="text-green-400">{(pick.model_probability * 100).toFixed(0)}%</span>
                    {' vs '}
                    <span className="text-gray-400">{(pick.implied_probability * 100).toFixed(0)}%</span>
                  </p>
                </div>
              </div>

              {/* Hit Rates */}
              {(pick.hit_rate_30d || pick.hit_rate_10g) && (
                <div className="mt-2 flex gap-4 text-xs">
                  {pick.hit_rate_30d && (
                    <span className="text-gray-400">
                      30-day hit rate: <span className="text-white">{(pick.hit_rate_30d * 100).toFixed(0)}%</span>
                    </span>
                  )}
                  {pick.hit_rate_10g && (
                    <span className="text-gray-400">
                      Last 10 games: <span className="text-white">{(pick.hit_rate_10g * 100).toFixed(0)}%</span>
                    </span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg p-8 text-center">
          <p className="text-gray-400">No picks available</p>
          <p className="text-sm text-gray-500 mt-2">
            Model picks will appear here once generated
          </p>
        </div>
      )}
    </div>
  );
}

function StatBadge({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-gray-800 rounded-lg p-3 text-center">
      <p className="text-xs text-gray-400">{label}</p>
      <p className="text-xl font-bold text-white">{value}</p>
    </div>
  );
}
