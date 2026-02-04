/**
 * MyEdgePage - Personal performance tracking and ROI analysis.
 * 
 * Shows:
 * - ROI by sport and stat type
 * - EV vs realized result analysis
 * - Summary of CLV (closing line value)
 */

import { useState } from 'react';
import { useMarketPerformance, useBetStats } from '../api/public';
import { LoadingState, ErrorState, EmptyState } from '../components/StateDisplay';

// Time range type
type TimeRange = '7d' | '30d' | 'all';

// Map time range to days
function rangeToDays(range: TimeRange): number {
  switch (range) {
    case '7d': return 7;
    case '30d': return 30;
    case 'all': return 365;
  }
}

export function MyEdgePage() {
  const [timeRange, setTimeRange] = useState<TimeRange>('30d');
  const days = rangeToDays(timeRange);
  
  // Fetch real data from API
  const { 
    data: marketData, 
    isLoading: marketLoading, 
    error: marketError 
  } = useMarketPerformance(days);
  
  const {
    data: statsData,
    isLoading: statsLoading,
    error: statsError
  } = useBetStats(undefined, days); // (sportId, daysBack)
  
  const isLoading = marketLoading || statsLoading;
  const error = marketError || statsError;
  
  // Calculate summary values
  const totalBets = statsData?.total_bets || 0;
  const winRate = statsData?.overall_win_rate || 0;
  const overallRoi = statsData?.overall_roi || 0;
  const avgClv = statsData?.clv_stats?.avg_clv_cents || 0;
  
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">My Edge</h1>
          <p className="text-gray-400 text-sm">Track your betting performance</p>
        </div>
        
        {/* Time Range Toggle */}
        <div className="flex rounded-lg overflow-hidden border border-gray-600">
          {(['7d', '30d', 'all'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 text-sm transition-colors ${
                timeRange === range
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : 'All Time'}
            </button>
          ))}
        </div>
      </div>

      {/* Loading State */}
      {isLoading && <LoadingState message="Loading your performance data..." />}
      
      {/* Error State */}
      {error && !isLoading && (
        <ErrorState 
          title="Could not load performance data"
          message="Please try again later or check your internet connection."
        />
      )}
      
      {/* Data Display */}
      {!isLoading && !error && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid sm:grid-cols-4 gap-4">
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <div className="text-gray-400 text-sm">Total Bets</div>
              <div className="text-2xl font-bold text-white">{totalBets}</div>
            </div>
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <div className="text-gray-400 text-sm">Win Rate</div>
              <div className={`text-2xl font-bold ${winRate >= 50 ? 'text-green-400' : 'text-gray-300'}`}>
                {winRate.toFixed(1)}%
              </div>
            </div>
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <div className="text-gray-400 text-sm">Overall ROI</div>
              <div className={`text-2xl font-bold ${overallRoi >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {overallRoi >= 0 ? '+' : ''}{overallRoi.toFixed(1)}%
              </div>
            </div>
            <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
              <div className="text-gray-400 text-sm">CLV Average</div>
              <div className={`text-2xl font-bold ${avgClv >= 0 ? 'text-blue-400' : 'text-orange-400'}`}>
                {avgClv >= 0 ? '+' : ''}{(avgClv / 100).toFixed(2)}%
              </div>
            </div>
          </div>

          {/* ROI by Market Type */}
          <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <div className="p-4 border-b border-gray-700">
              <h2 className="font-bold text-white">ROI by Market Type</h2>
              <p className="text-xs text-gray-400">Performance breakdown by stat type</p>
            </div>
            
            {!marketData?.markets?.length ? (
              <EmptyState
                icon="chart"
                title="No performance data yet"
                message="Start tracking bets to see your ROI breakdown by market type."
              />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-700/50">
                    <tr>
                      <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">Market</th>
                      <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">Bets</th>
                      <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">Won</th>
                      <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">Win Rate</th>
                      <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">ROI</th>
                      <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">Avg CLV</th>
                      <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">Quality</th>
                    </tr>
                  </thead>
                  <tbody>
                    {marketData.markets.map((market) => (
                      <tr key={market.market_type} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                        <td className="py-3 px-4">
                          <span className="font-medium text-white">{market.market_type}</span>
                        </td>
                        <td className="py-3 px-4 text-center text-gray-300">{market.total_bets}</td>
                        <td className="py-3 px-4 text-center text-gray-300">{market.won}</td>
                        <td className="py-3 px-4 text-center text-gray-300">
                          {market.win_rate.toFixed(1)}%
                        </td>
                        <td className={`py-3 px-4 text-center font-bold ${market.roi >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {market.roi >= 0 ? '+' : ''}{market.roi.toFixed(1)}%
                        </td>
                        <td className={`py-3 px-4 text-center ${market.avg_clv_cents >= 0 ? 'text-blue-400' : 'text-orange-400'}`}>
                          {market.avg_clv_cents >= 0 ? '+' : ''}{(market.avg_clv_cents / 100).toFixed(2)}%
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className={`px-2 py-0.5 rounded text-xs ${
                            market.sample_quality === 'high' 
                              ? 'bg-green-900/50 text-green-400'
                              : market.sample_quality === 'medium'
                              ? 'bg-yellow-900/50 text-yellow-400'
                              : 'bg-gray-700 text-gray-400'
                          }`}>
                            {market.sample_quality}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Best and Worst Markets */}
          {marketData?.summary && (marketData.summary.best_market || marketData.summary.worst_market) && (
            <div className="grid sm:grid-cols-2 gap-4">
              {marketData.summary.best_market && (
                <div className="bg-green-900/20 border border-green-800/50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    <span className="text-green-400 text-sm font-medium">Best Performing</span>
                  </div>
                  <div className="text-xl font-bold text-white">{marketData.summary.best_market}</div>
                </div>
              )}
              {marketData.summary.worst_market && (
                <div className="bg-red-900/20 border border-red-800/50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6" />
                    </svg>
                    <span className="text-red-400 text-sm font-medium">Worst Performing</span>
                  </div>
                  <div className="text-xl font-bold text-white">{marketData.summary.worst_market}</div>
                </div>
              )}
            </div>
          )}

          {/* CLV Analysis */}
          {statsData?.clv_stats && (
            <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
              <div className="p-4 border-b border-gray-700">
                <h2 className="font-bold text-white">Closing Line Value (CLV)</h2>
                <p className="text-xs text-gray-400">How often you beat the closing line</p>
              </div>
              
              <div className="p-4 grid sm:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">
                    {statsData.clv_stats.total_bets_with_clv}
                  </div>
                  <div className="text-sm text-gray-400">Bets with CLV data</div>
                </div>
                <div className="text-center">
                  <div className={`text-2xl font-bold ${statsData.clv_stats.avg_clv_cents >= 0 ? 'text-blue-400' : 'text-orange-400'}`}>
                    {statsData.clv_stats.avg_clv_cents >= 0 ? '+' : ''}
                    {(statsData.clv_stats.avg_clv_cents / 100).toFixed(2)}%
                  </div>
                  <div className="text-sm text-gray-400">Average CLV</div>
                </div>
                <div className="text-center">
                  <div className={`text-2xl font-bold ${statsData.clv_stats.positive_clv_pct >= 50 ? 'text-green-400' : 'text-gray-300'}`}>
                    {statsData.clv_stats.positive_clv_pct.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-400">Beat Close Rate</div>
                </div>
              </div>
            </div>
          )}

          {/* Info Banner */}
          <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-blue-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-blue-200 font-medium">Track Your Edge</p>
                <p className="text-blue-300/70 text-sm mt-1">
                  Log your bets in the My Bets tab to see your actual performance here. 
                  We'll track your ROI, CLV, and how well you're hitting at different EV levels.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MyEdgePage;
