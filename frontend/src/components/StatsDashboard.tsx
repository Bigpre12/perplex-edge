import { useStats, useHitRates } from '../api/public';
import { StatsTable } from './StatsTable';

export function StatsDashboard() {
  const { data: statsData, isLoading: statsLoading, error: statsError } = useStats();
  const { data: hitRatesData, isLoading: hitRatesLoading, error: hitRatesError } = useHitRates();

  // Format helpers
  const formatPercent = (value: number) => `${value.toFixed(1)}%`;

  return (
    <div className="space-y-6">
      {/* Overall Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Picks */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 uppercase tracking-wide">Total Picks</p>
              <p className="text-3xl font-bold text-white mt-2">
                {statsLoading ? (
                  <span className="animate-pulse">...</span>
                ) : (
                  statsData?.total_picks ?? 0
                )}
              </p>
            </div>
            <div className="p-3 bg-blue-900/50 rounded-lg">
              <svg className="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>
        </div>

        {/* Hit Rate */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 uppercase tracking-wide">Hit Rate</p>
              <p className={`text-3xl font-bold mt-2 ${
                (statsData?.hit_rate ?? 0) >= 50 ? 'text-green-400' : 'text-yellow-400'
              }`}>
                {statsLoading ? (
                  <span className="animate-pulse">...</span>
                ) : (
                  formatPercent(statsData?.hit_rate ?? 0)
                )}
              </p>
            </div>
            <div className="p-3 bg-green-900/50 rounded-lg">
              <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Avg EV */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 uppercase tracking-wide">Avg EV</p>
              <p className={`text-3xl font-bold mt-2 ${
                (statsData?.avg_ev ?? 0) >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {statsLoading ? (
                  <span className="animate-pulse">...</span>
                ) : (
                  `${statsData?.avg_ev?.toFixed(2) ?? 0}%`
                )}
              </p>
            </div>
            <div className="p-3 bg-purple-900/50 rounded-lg">
              <svg className="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
        </div>

        {/* Players Tracked */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 uppercase tracking-wide">Players Tracked</p>
              <p className="text-3xl font-bold text-white mt-2">
                {statsLoading ? (
                  <span className="animate-pulse">...</span>
                ) : (
                  statsData?.players_tracked ?? 0
                )}
              </p>
            </div>
            <div className="p-3 bg-orange-900/50 rounded-lg">
              <svg className="w-8 h-8 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Error States */}
      {statsError && (
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-4 text-red-400">
          Failed to load stats summary. Please try again.
        </div>
      )}
      {hitRatesError && (
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-4 text-red-400">
          Failed to load hit rates. Please try again.
        </div>
      )}

      {/* Top Performers Section */}
      {hitRatesData && hitRatesData.items.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-lg font-semibold text-white mb-4">Top Performers</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {hitRatesData.items
              .filter((r) => r.total_picks >= 5)
              .sort((a, b) => b.hit_rate_percentage - a.hit_rate_percentage)
              .slice(0, 6)
              .map((record) => (
                <div
                  key={`${record.player_name}-${record.stat_type}`}
                  className="bg-gray-900 rounded-lg p-4 border border-gray-700"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-white font-medium">{record.player_name}</p>
                      <p className="text-sm text-gray-400">
                        <span className="bg-blue-900/50 text-blue-400 text-xs px-2 py-0.5 rounded">
                          {record.stat_type}
                        </span>
                      </p>
                    </div>
                    <div className="text-right">
                      <p className={`text-xl font-bold ${
                        record.hit_rate_percentage >= 60 ? 'text-green-400' : 'text-yellow-400'
                      }`}>
                        {record.hit_rate_percentage.toFixed(1)}%
                      </p>
                      <p className="text-xs text-gray-500">{record.total_picks} picks</p>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Hit Rates Table */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Historical Hit Rates</h2>
        <StatsTable
          data={hitRatesData?.items ?? []}
          isLoading={hitRatesLoading}
        />
      </div>
    </div>
  );
}

export default StatsDashboard;
