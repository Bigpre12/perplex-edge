import { useState } from 'react';
import { fetchBacktest, BacktestResult, BacktestFilters, STAT_TYPE_OPTIONS, useSports } from '../api/public';

// =============================================================================
// Backtest Tab Component
// =============================================================================

export function BacktestTab() {
  const { data: sportsData } = useSports();
  
  // Filter state
  const [sportId, setSportId] = useState<number | undefined>(undefined);
  const [statType, setStatType] = useState<string>('');
  const [side, setSide] = useState<string>('');
  const [minEv, setMinEv] = useState<number>(0.03);
  const [minConfidence, setMinConfidence] = useState<number>(0.55);
  const [daysBack, setDaysBack] = useState<number>(30);
  
  // Result state
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Run backtest
  const runBacktest = async () => {
    setIsRunning(true);
    setError(null);
    
    const filters: BacktestFilters = {
      sport_id: sportId,
      stat_type: statType || undefined,
      side: side || undefined,
      min_ev: minEv,
      min_confidence: minConfidence,
      days_back: daysBack,
    };
    
    try {
      const data = await fetchBacktest(filters);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run backtest');
    } finally {
      setIsRunning(false);
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white">Strategy Backtester</h2>
        <p className="text-sm text-gray-400">
          Define simple rules and see how that strategy would have performed historically
        </p>
      </div>
      
      {/* Filter Form */}
      <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {/* Sport */}
          <div>
            <label className="block text-xs text-gray-400 mb-1">Sport</label>
            <select
              value={sportId ?? ''}
              onChange={(e) => setSportId(e.target.value ? Number(e.target.value) : undefined)}
              className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm border border-gray-600"
            >
              <option value="">All Sports</option>
              {sportsData?.items?.map((sport) => (
                <option key={sport.id} value={sport.id}>{sport.name}</option>
              ))}
            </select>
          </div>
          
          {/* Stat Type */}
          <div>
            <label className="block text-xs text-gray-400 mb-1">Market</label>
            <select
              value={statType}
              onChange={(e) => setStatType(e.target.value)}
              className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm border border-gray-600"
            >
              <option value="">All Markets</option>
              {STAT_TYPE_OPTIONS.filter(o => o.value).map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
          
          {/* Side */}
          <div>
            <label className="block text-xs text-gray-400 mb-1">Side</label>
            <select
              value={side}
              onChange={(e) => setSide(e.target.value)}
              className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm border border-gray-600"
            >
              <option value="">Both</option>
              <option value="over">Over</option>
              <option value="under">Under</option>
            </select>
          </div>
          
          {/* Min EV */}
          <div>
            <label className="block text-xs text-gray-400 mb-1">
              Min EV: {(minEv * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0"
              max="0.15"
              step="0.01"
              value={minEv}
              onChange={(e) => setMinEv(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>
          
          {/* Min Confidence */}
          <div>
            <label className="block text-xs text-gray-400 mb-1">
              Min Conf: {(minConfidence * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0.40"
              max="0.80"
              step="0.05"
              value={minConfidence}
              onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>
          
          {/* Days Back */}
          <div>
            <label className="block text-xs text-gray-400 mb-1">Days Back</label>
            <select
              value={daysBack}
              onChange={(e) => setDaysBack(Number(e.target.value))}
              className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm border border-gray-600"
            >
              <option value={7}>7 days</option>
              <option value={14}>14 days</option>
              <option value={30}>30 days</option>
              <option value={60}>60 days</option>
              <option value={90}>90 days</option>
            </select>
          </div>
        </div>
        
        {/* Run Button */}
        <div className="mt-4 flex items-center gap-4">
          <button
            onClick={runBacktest}
            disabled={isRunning}
            className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:from-gray-600 disabled:to-gray-600 text-white font-semibold rounded-lg shadow-lg transition-all"
          >
            {isRunning ? (
              <span className="flex items-center gap-2">
                <span className="animate-spin">⏳</span>
                Running...
              </span>
            ) : (
              'Run Backtest'
            )}
          </button>
          
          <div className="text-xs text-gray-500">
            {statType || 'All markets'} | {side || 'Both sides'} | 
            {minEv * 100}%+ EV | {minConfidence * 100}%+ confidence | {daysBack} days
          </div>
        </div>
      </div>
      
      {/* Error */}
      {error && (
        <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 text-red-400">
          {error}
        </div>
      )}
      
      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Sample Quality Banner */}
          <div className={`rounded-lg p-3 flex items-center gap-3 ${
            result.sample_quality === 'high' ? 'bg-green-900/30 border border-green-700' :
            result.sample_quality === 'medium' ? 'bg-yellow-900/30 border border-yellow-700' :
            result.sample_quality === 'low' ? 'bg-orange-900/30 border border-orange-700' :
            'bg-red-900/30 border border-red-700'
          }`}>
            <span className="text-2xl">
              {result.sample_quality === 'high' ? '✅' :
               result.sample_quality === 'medium' ? '⚠️' :
               result.sample_quality === 'low' ? '⚠️' : '❌'}
            </span>
            <div>
              <div className="font-medium text-white">
                {result.qualifying_bets} qualifying bets found
              </div>
              <div className="text-xs text-gray-400">
                Sample quality: {result.sample_quality} | 
                {result.date_range?.start ?? 'N/A'} to {result.date_range?.end ?? 'N/A'}
              </div>
            </div>
          </div>
          
          {result.qualifying_bets > 0 && (
            <>
              {/* Key Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-xs text-gray-400">Record</div>
                  <div className="text-2xl font-bold text-white">
                    <span className="text-green-400">{result.wins}</span>
                    <span className="text-gray-500"> - </span>
                    <span className="text-red-400">{result.losses}</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {result.hit_rate}% hit rate
                  </div>
                </div>
                
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-xs text-gray-400">Flat Stake ROI</div>
                  <div className={`text-2xl font-bold ${result.flat_stake_roi > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {result.flat_stake_roi > 0 ? '+' : ''}{result.flat_stake_roi}%
                  </div>
                  <div className="text-xs text-gray-500">
                    {result.flat_stake_profit > 0 ? '+' : ''}{result.flat_stake_profit}u on {result.flat_stake_units}u staked
                  </div>
                </div>
                
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-xs text-gray-400">Kelly Stake ROI</div>
                  <div className={`text-2xl font-bold ${result.kelly_stake_roi > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {result.kelly_stake_roi > 0 ? '+' : ''}{result.kelly_stake_roi}%
                  </div>
                  <div className="text-xs text-gray-500">
                    {result.kelly_stake_profit > 0 ? '+' : ''}{result.kelly_stake_profit.toFixed(2)}u (¼ Kelly)
                  </div>
                </div>
                
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <div className="text-xs text-gray-400">Avg EV / CLV</div>
                  <div className="text-2xl font-bold text-white">
                    {result.avg_ev}%
                  </div>
                  <div className={`text-xs ${result.avg_clv_cents > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {result.avg_clv_cents > 0 ? '+' : ''}{result.avg_clv_cents}¢ CLV
                  </div>
                </div>
              </div>
              
              {/* Confidence Bucket Breakdown */}
              {result.confidence_buckets.length > 0 && (
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <h3 className="font-bold text-white mb-4">Hit Rate by Confidence</h3>
                  <div className="space-y-2">
                    {result.confidence_buckets.map((bucket, idx) => (
                      <div key={idx} className="flex items-center gap-3">
                        <div className="w-20 text-sm text-gray-400">{bucket.label}</div>
                        <div className="flex-1 h-6 bg-gray-700/50 rounded overflow-hidden relative">
                          <div
                            className={`h-full ${bucket.hit_rate >= 60 ? 'bg-green-500' : bucket.hit_rate >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
                            style={{ width: `${bucket.hit_rate}%` }}
                          />
                          <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white">
                            {bucket.hit_rate}% ({bucket.wins}-{bucket.losses})
                          </span>
                        </div>
                        <div className="w-16 text-xs text-gray-500 text-right">
                          {bucket.count} bets
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Insights */}
              <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
                <h3 className="font-bold text-blue-300 mb-2">📈 Insights</h3>
                <ul className="text-sm text-blue-200/80 space-y-1">
                  {result.hit_rate >= 55 && (
                    <li>• Strategy is profitable with {result.hit_rate}% hit rate</li>
                  )}
                  {result.kelly_stake_roi > result.flat_stake_roi && (
                    <li>• Kelly sizing outperformed flat stakes by {(result.kelly_stake_roi - result.flat_stake_roi).toFixed(1)}%</li>
                  )}
                  {result.avg_clv_cents > 0 && (
                    <li>• Beating closing lines by {result.avg_clv_cents}¢ on average - good sign!</li>
                  )}
                  {result.sample_quality === 'low' && (
                    <li>• Sample size is small - results may not be statistically significant</li>
                  )}
                  {result.hit_rate < 50 && (
                    <li>• Hit rate below 50% - consider adjusting filters</li>
                  )}
                </ul>
              </div>
            </>
          )}
          
          {result.qualifying_bets === 0 && (
            <div className="text-center py-8">
              <div className="text-4xl mb-4">📭</div>
              <div className="text-gray-300">No qualifying bets found</div>
              <div className="text-gray-500 text-sm mt-2">
                Try lowering EV/confidence thresholds or expanding the date range
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Initial state */}
      {!result && !isRunning && !error && (
        <div className="text-center py-12 bg-gray-800/30 rounded-lg">
          <div className="text-4xl mb-4">🔬</div>
          <div className="text-gray-300 text-lg">Configure your strategy above</div>
          <div className="text-gray-500 text-sm mt-2">
            Set your filters and click "Run Backtest" to see historical performance
          </div>
        </div>
      )}
    </div>
  );
}
