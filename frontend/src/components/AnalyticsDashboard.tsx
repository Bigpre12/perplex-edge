import { useState } from 'react';
import { useMarketPerformance, useBetStats, useCLVHistory, MarketPerformance } from '../api/public';

// =============================================================================
// Helper Components
// =============================================================================

function StatCard({ 
  label, 
  value, 
  subtext, 
  color = 'white' 
}: { 
  label: string; 
  value: string; 
  subtext?: string; 
  color?: string;
}) {
  const colorClasses: Record<string, string> = {
    white: 'text-white',
    green: 'text-green-400',
    red: 'text-red-400',
    yellow: 'text-yellow-400',
    blue: 'text-blue-400',
  };
  
  return (
    <div className="bg-gray-800/50 rounded-lg p-4">
      <div className="text-xs text-gray-400 mb-1">{label}</div>
      <div className={`text-2xl font-bold ${colorClasses[color] || 'text-white'}`}>{value}</div>
      {subtext && <div className="text-xs text-gray-500 mt-1">{subtext}</div>}
    </div>
  );
}

function MarketRow({ market }: { market: MarketPerformance }) {
  const roiColor = market.roi > 5 ? 'text-green-400' : market.roi > 0 ? 'text-green-300' : market.roi > -5 ? 'text-yellow-400' : 'text-red-400';
  const clvColor = market.avg_clv_cents > 0 ? 'text-green-400' : market.avg_clv_cents < 0 ? 'text-red-400' : 'text-gray-400';
  
  return (
    <tr className="border-b border-gray-700/50 hover:bg-gray-800/30">
      <td className="py-3 px-4">
        <div className="font-medium text-white">
          {market.market_type.replace('player_', '').replace(/_/g, ' ').toUpperCase()}
        </div>
        <div className="text-xs text-gray-500">
          {market.sample_quality === 'high' ? '✓ High sample' : 
           market.sample_quality === 'medium' ? '~ Medium sample' : '⚠ Low sample'}
        </div>
      </td>
      <td className="py-3 px-4 text-center text-gray-300">{market.total_bets}</td>
      <td className="py-3 px-4 text-center">
        <span className="text-green-400">{market.won}</span>
        <span className="text-gray-500"> - </span>
        <span className="text-red-400">{market.lost}</span>
      </td>
      <td className="py-3 px-4 text-center text-gray-300">{market.win_rate}%</td>
      <td className={`py-3 px-4 text-center font-medium ${roiColor}`}>
        {market.roi > 0 ? '+' : ''}{market.roi}%
      </td>
      <td className={`py-3 px-4 text-center ${clvColor}`}>
        {market.avg_clv_cents > 0 ? '+' : ''}{market.avg_clv_cents}¢
      </td>
      <td className="py-3 px-4 text-center text-gray-300">
        {market.beat_close_pct}%
      </td>
    </tr>
  );
}

function SimpleBarChart({ 
  data, 
  valueKey, 
  labelKey,
  positiveColor = 'bg-green-500',
  negativeColor = 'bg-red-500',
}: { 
  data: Array<Record<string, unknown>>;
  valueKey: string;
  labelKey: string;
  positiveColor?: string;
  negativeColor?: string;
}) {
  if (!data || data.length === 0) {
    return <div className="text-gray-500 text-center py-4">No data available</div>;
  }
  
  const maxValue = Math.max(...data.map(d => Math.abs(Number(d[valueKey]) || 0)));
  
  return (
    <div className="space-y-2">
      {data.map((item, idx) => {
        const value = Number(item[valueKey]) || 0;
        const label = String(item[labelKey] || '').replace('player_', '').replace(/_/g, ' ').toUpperCase();
        const width = maxValue > 0 ? (Math.abs(value) / maxValue) * 100 : 0;
        const isPositive = value >= 0;
        
        return (
          <div key={idx} className="flex items-center gap-2">
            <div className="w-24 text-xs text-gray-400 truncate" title={label}>{label}</div>
            <div className="flex-1 h-6 bg-gray-700/50 rounded overflow-hidden relative">
              <div
                className={`h-full ${isPositive ? positiveColor : negativeColor} transition-all`}
                style={{ width: `${Math.min(width, 100)}%` }}
              />
              <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white">
                {value > 0 ? '+' : ''}{typeof value === 'number' ? value.toFixed(1) : value}%
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// =============================================================================
// Main Dashboard Component
// =============================================================================

export function AnalyticsDashboard() {
  const [daysBack, setDaysBack] = useState(30);
  
  const { data: marketData, isLoading: marketLoading } = useMarketPerformance(daysBack);
  const { data: statsData, isLoading: statsLoading } = useBetStats(undefined, daysBack);
  const { data: clvData, isLoading: clvLoading } = useCLVHistory(undefined, daysBack);
  
  const isLoading = marketLoading || statsLoading || clvLoading;
  
  // Calculate derived stats
  const totalBets = statsData?.total_bets ?? 0;
  const hasData = totalBets > 0;
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">CLV/ROI Analytics</h2>
          <p className="text-sm text-gray-400">
            Track model performance by market, CLV, and ROI over time
          </p>
        </div>
        
        {/* Time range selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">Time range:</span>
          {[7, 30, 90].map((days) => (
            <button
              key={days}
              onClick={() => setDaysBack(days)}
              className={`px-3 py-1.5 rounded text-sm transition-colors ${
                daysBack === days
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              {days}d
            </button>
          ))}
        </div>
      </div>
      
      {/* Loading state */}
      {isLoading && (
        <div className="text-center py-12">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-purple-400 border-t-transparent rounded-full mb-4" />
          <div className="text-gray-400">Loading analytics...</div>
        </div>
      )}
      
      {/* No data state */}
      {!isLoading && !hasData && (
        <div className="text-center py-12 bg-gray-800/30 rounded-lg">
          <div className="text-4xl mb-4">📊</div>
          <div className="text-gray-300 text-lg">No betting data yet</div>
          <div className="text-gray-500 text-sm mt-2">
            Start logging bets in the "My Bets" tab to see analytics here.
          </div>
        </div>
      )}
      
      {/* Dashboard content */}
      {!isLoading && hasData && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <StatCard
              label="Total Bets"
              value={totalBets.toString()}
              subtext={`${statsData?.won ?? 0}W - ${statsData?.lost ?? 0}L`}
            />
            <StatCard
              label="Overall ROI"
              value={`${(statsData?.overall_roi ?? 0) > 0 ? '+' : ''}${(statsData?.overall_roi ?? 0).toFixed(1)}%`}
              subtext={`$${(statsData?.total_profit_loss ?? 0).toFixed(2)} P/L`}
              color={(statsData?.overall_roi ?? 0) > 0 ? 'green' : 'red'}
            />
            <StatCard
              label="Win Rate"
              value={`${((statsData?.overall_win_rate ?? 0) * 100).toFixed(1)}%`}
              subtext={`${statsData?.pushed ?? 0} pushes`}
            />
            <StatCard
              label="CLV"
              value={`${(statsData?.clv_stats?.avg_clv_cents ?? 0) > 0 ? '+' : ''}${(statsData?.clv_stats?.avg_clv_cents ?? 0).toFixed(1)}¢`}
              subtext={`${(statsData?.clv_stats?.positive_clv_pct ?? 0) * 100}% beat close`}
              color={(statsData?.clv_stats?.avg_clv_cents ?? 0) > 0 ? 'green' : 'yellow'}
            />
          </div>
          
          {/* Market Performance Table */}
          <div className="bg-gray-800/30 rounded-lg overflow-hidden">
            <div className="p-4 border-b border-gray-700">
              <h3 className="font-bold text-white">Performance by Market</h3>
              <p className="text-xs text-gray-400">
                Which markets is the model best at? Focus on high-sample markets.
              </p>
            </div>
            
            {marketData?.markets && marketData.markets.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-800/50">
                    <tr>
                      <th className="text-left py-2 px-4 text-xs text-gray-400 font-medium">Market</th>
                      <th className="text-center py-2 px-4 text-xs text-gray-400 font-medium">Bets</th>
                      <th className="text-center py-2 px-4 text-xs text-gray-400 font-medium">Record</th>
                      <th className="text-center py-2 px-4 text-xs text-gray-400 font-medium">Win%</th>
                      <th className="text-center py-2 px-4 text-xs text-gray-400 font-medium">ROI</th>
                      <th className="text-center py-2 px-4 text-xs text-gray-400 font-medium">Avg CLV</th>
                      <th className="text-center py-2 px-4 text-xs text-gray-400 font-medium">Beat Close</th>
                    </tr>
                  </thead>
                  <tbody>
                    {marketData.markets.map((market, idx) => (
                      <MarketRow key={idx} market={market} />
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-8 text-center text-gray-500">No market data available</div>
            )}
          </div>
          
          {/* ROI Charts */}
          <div className="grid md:grid-cols-2 gap-4">
            {/* ROI by Market Chart */}
            <div className="bg-gray-800/30 rounded-lg p-4">
              <h3 className="font-bold text-white mb-4">ROI by Market</h3>
              <SimpleBarChart
                data={(statsData?.by_market || []).slice(0, 8)}
                valueKey="roi"
                labelKey="category"
              />
            </div>
            
            {/* ROI by Sportsbook Chart */}
            <div className="bg-gray-800/30 rounded-lg p-4">
              <h3 className="font-bold text-white mb-4">ROI by Sportsbook</h3>
              <SimpleBarChart
                data={(statsData?.by_sportsbook || []).slice(0, 6)}
                valueKey="roi"
                labelKey="category"
              />
            </div>
          </div>
          
          {/* CLV Trend */}
          {clvData?.data_points && clvData.data_points.length > 0 && (
            <div className="bg-gray-800/30 rounded-lg p-4">
              <h3 className="font-bold text-white mb-2">CLV Trend</h3>
              <p className="text-xs text-gray-400 mb-4">
                Cumulative CLV over time. Upward trend = consistently beating closing lines.
              </p>
              
              {/* Simple line representation */}
              <div className="h-32 flex items-end gap-1">
                {clvData.data_points.map((point, idx) => {
                  const maxClv = Math.max(...clvData.data_points.map(p => Math.abs(p.cumulative_clv)));
                  const height = maxClv > 0 ? (Math.abs(point.cumulative_clv) / maxClv) * 100 : 50;
                  const isPositive = point.cumulative_clv >= 0;
                  
                  return (
                    <div
                      key={idx}
                      className="flex-1 min-w-1"
                      title={`${point.date}: ${point.cumulative_clv > 0 ? '+' : ''}${point.cumulative_clv.toFixed(0)}¢`}
                    >
                      <div
                        className={`w-full rounded-t ${isPositive ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{ height: `${Math.max(height, 4)}%` }}
                      />
                    </div>
                  );
                })}
              </div>
              
              <div className="flex justify-between text-xs text-gray-500 mt-2">
                <span>{clvData.data_points[0]?.date}</span>
                <span className={clvData.total_clv > 0 ? 'text-green-400' : 'text-red-400'}>
                  Total: {clvData.total_clv > 0 ? '+' : ''}{clvData.total_clv.toFixed(0)}¢
                </span>
                <span>{clvData.data_points[clvData.data_points.length - 1]?.date}</span>
              </div>
            </div>
          )}
          
          {/* Top/Worst Players */}
          <div className="grid md:grid-cols-2 gap-4">
            {/* Top Players */}
            <div className="bg-gray-800/30 rounded-lg p-4">
              <h3 className="font-bold text-white mb-4">🏆 Top Players (by ROI)</h3>
              {statsData?.top_players && statsData.top_players.length > 0 ? (
                <div className="space-y-2">
                  {statsData.top_players.slice(0, 5).map((player, idx) => (
                    <div key={idx} className="flex items-center justify-between py-2 px-3 bg-gray-700/30 rounded">
                      <div>
                        <span className="text-white font-medium">{player.player_name}</span>
                        <span className="text-gray-500 text-xs ml-2">({player.total_bets} bets)</span>
                      </div>
                      <span className="text-green-400 font-medium">+{player.roi.toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-gray-500 text-sm">Need 5+ bets per player to show</div>
              )}
            </div>
            
            {/* Worst Players */}
            <div className="bg-gray-800/30 rounded-lg p-4">
              <h3 className="font-bold text-white mb-4">📉 Worst Players (avoid)</h3>
              {statsData?.worst_players && statsData.worst_players.length > 0 ? (
                <div className="space-y-2">
                  {statsData.worst_players.slice(0, 5).map((player, idx) => (
                    <div key={idx} className="flex items-center justify-between py-2 px-3 bg-gray-700/30 rounded">
                      <div>
                        <span className="text-white font-medium">{player.player_name}</span>
                        <span className="text-gray-500 text-xs ml-2">({player.total_bets} bets)</span>
                      </div>
                      <span className="text-red-400 font-medium">{player.roi.toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-gray-500 text-sm">Need 5+ bets per player to show</div>
              )}
            </div>
          </div>
          
          {/* Insights */}
          <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
            <h3 className="font-bold text-blue-300 mb-2">📈 Key Insights</h3>
            <ul className="text-sm text-blue-200/80 space-y-1">
              {marketData?.summary?.best_market && (
                <li>• Best market: <strong>{marketData.summary.best_market.replace('player_', '').replace(/_/g, ' ').toUpperCase()}</strong></li>
              )}
              {(statsData?.clv_stats?.positive_clv_pct ?? 0) > 0.5 && (
                <li>• You're beating the close {((statsData?.clv_stats?.positive_clv_pct ?? 0) * 100).toFixed(0)}% of the time - good sign!</li>
              )}
              {(statsData?.clv_stats?.positive_clv_pct ?? 0) < 0.5 && (statsData?.clv_stats?.total_bets_with_clv ?? 0) > 10 && (
                <li>• CLV below 50% - consider betting earlier or finding sharper lines</li>
              )}
              {(statsData?.overall_roi ?? 0) > 0 && (
                <li>• Profitable over {daysBack} days - keep following the model!</li>
              )}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
