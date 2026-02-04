/**
 * MyEdgePage - Personal performance tracking and ROI analysis.
 * 
 * Shows:
 * - ROI by sport and stat type
 * - EV vs realized result analysis
 * - Summary of CLV (closing line value)
 */

import { useState } from 'react';

// Placeholder data structure for future API integration
interface PerformanceData {
  sport: string;
  bets: number;
  wins: number;
  roi: number;
}

interface EVBucket {
  range: string;
  bets: number;
  wins: number;
  hitRate: number;
  expectedHitRate: number;
}

export function MyEdgePage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | 'all'>('30d');

  // Placeholder data - will be replaced with actual API data
  const performanceData: PerformanceData[] = [
    { sport: 'NBA', bets: 45, wins: 28, roi: 8.5 },
    { sport: 'NFL', bets: 22, wins: 13, roi: 4.2 },
    { sport: 'MLB', bets: 18, wins: 9, roi: -2.1 },
    { sport: 'NHL', bets: 12, wins: 7, roi: 5.8 },
  ];

  const evBuckets: EVBucket[] = [
    { range: '0-5%', bets: 35, wins: 19, hitRate: 54.3, expectedHitRate: 52.5 },
    { range: '5-10%', bets: 28, wins: 17, hitRate: 60.7, expectedHitRate: 57.5 },
    { range: '10%+', bets: 15, wins: 11, hitRate: 73.3, expectedHitRate: 65.0 },
  ];

  const totalBets = performanceData.reduce((sum, p) => sum + p.bets, 0);
  const totalWins = performanceData.reduce((sum, p) => sum + p.wins, 0);
  const overallHitRate = totalBets > 0 ? (totalWins / totalBets * 100).toFixed(1) : '0';

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

      <div className="space-y-6">
        {/* Summary Cards */}
        <div className="grid sm:grid-cols-4 gap-4">
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <div className="text-gray-400 text-sm">Total Bets</div>
            <div className="text-2xl font-bold text-white">{totalBets}</div>
          </div>
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <div className="text-gray-400 text-sm">Win Rate</div>
            <div className="text-2xl font-bold text-green-400">{overallHitRate}%</div>
          </div>
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <div className="text-gray-400 text-sm">Overall ROI</div>
            <div className={`text-2xl font-bold ${5.3 >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              +5.3%
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
            <div className="text-gray-400 text-sm">CLV Average</div>
            <div className="text-2xl font-bold text-blue-400">+1.8%</div>
          </div>
        </div>

        {/* ROI by Sport */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="p-4 border-b border-gray-700">
            <h2 className="font-bold text-white">ROI by Sport</h2>
            <p className="text-xs text-gray-400">Performance breakdown</p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700/50">
                <tr>
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">Sport</th>
                  <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">Bets</th>
                  <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">Wins</th>
                  <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">Hit Rate</th>
                  <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">ROI</th>
                </tr>
              </thead>
              <tbody>
                {performanceData.map((row) => (
                  <tr key={row.sport} className="border-b border-gray-700/50">
                    <td className="py-3 px-4 font-medium text-white">{row.sport}</td>
                    <td className="py-3 px-4 text-center text-gray-300">{row.bets}</td>
                    <td className="py-3 px-4 text-center text-gray-300">{row.wins}</td>
                    <td className="py-3 px-4 text-center text-gray-300">
                      {((row.wins / row.bets) * 100).toFixed(1)}%
                    </td>
                    <td className={`py-3 px-4 text-center font-bold ${row.roi >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {row.roi >= 0 ? '+' : ''}{row.roi}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* EV Performance Analysis */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="p-4 border-b border-gray-700">
            <h2 className="font-bold text-white">EV Performance</h2>
            <p className="text-xs text-gray-400">How well are you hitting at different EV ranges?</p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700/50">
                <tr>
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">EV Range</th>
                  <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">Bets</th>
                  <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">Wins</th>
                  <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">Actual Hit %</th>
                  <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">Expected Hit %</th>
                  <th className="text-center py-3 px-4 text-xs text-gray-400 font-medium">vs Expected</th>
                </tr>
              </thead>
              <tbody>
                {evBuckets.map((bucket) => {
                  const diff = bucket.hitRate - bucket.expectedHitRate;
                  return (
                    <tr key={bucket.range} className="border-b border-gray-700/50">
                      <td className="py-3 px-4 font-medium text-white">{bucket.range}</td>
                      <td className="py-3 px-4 text-center text-gray-300">{bucket.bets}</td>
                      <td className="py-3 px-4 text-center text-gray-300">{bucket.wins}</td>
                      <td className="py-3 px-4 text-center text-gray-300">{bucket.hitRate}%</td>
                      <td className="py-3 px-4 text-center text-gray-400">{bucket.expectedHitRate}%</td>
                      <td className={`py-3 px-4 text-center font-bold ${diff >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {diff >= 0 ? '+' : ''}{diff.toFixed(1)}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

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
    </div>
  );
}

export default MyEdgePage;
