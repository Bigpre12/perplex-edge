/**
 * Model Performance Dashboard
 * 
 * Shows 30-day rolling hit rate, EV buckets, and calibration metrics.
 * Proves the model works and provides sales screenshots.
 */

import { useState } from 'react';
import { useCalibrationReport, useAnalyticsDashboard, CalibrationBucket } from '../api/public';
import { useSportContext } from '../context/SportContext';
import { METRIC_EXPLAINERS } from '../constants/presets';

// Map sport IDs to API keys
const SPORT_API_KEYS: Record<number, string> = {
  30: 'basketball_nba',
  31: 'americanfootball_nfl',
  32: 'basketball_ncaab',
  40: 'baseball_mlb',
  41: 'americanfootball_ncaaf',
  42: 'tennis_atp',
  43: 'tennis_wta',
  44: 'icehockey_nhl',
};

const SPORT_SHORT_NAMES: Record<number, string> = {
  30: 'nba',
  31: 'nfl',
  32: 'ncaab',
  40: 'mlb',
  41: 'ncaaf',
  42: 'atp',
  43: 'wta',
  44: 'nhl',
};

// Calibration bucket bar component
function CalibrationBar({ bucket }: { bucket: CalibrationBucket }) {
  const predictedPercent = bucket.predicted_mid * 100;
  const actualPercent = bucket.actual_hit_rate * 100;
  const error = Math.abs(predictedPercent - actualPercent);
  
  // Color based on calibration error
  const barColor = error < 3 ? 'bg-green-500' : error < 7 ? 'bg-yellow-500' : 'bg-red-500';
  
  return (
    <div className="flex items-center gap-3 py-2">
      <div className="w-20 text-xs text-gray-400">{bucket.bucket_name}</div>
      <div className="flex-1 relative">
        {/* Background bar */}
        <div className="h-6 bg-gray-700 rounded-full overflow-hidden relative">
          {/* Predicted line */}
          <div 
            className="absolute top-0 bottom-0 w-0.5 bg-white/50 z-10"
            style={{ left: `${predictedPercent}%` }}
            title={`Predicted: ${predictedPercent.toFixed(1)}%`}
          />
          {/* Actual bar */}
          <div 
            className={`h-full ${barColor} transition-all`}
            style={{ width: `${Math.min(100, actualPercent)}%` }}
          />
        </div>
      </div>
      <div className="w-20 text-right">
        <span className={`text-sm font-medium ${error < 3 ? 'text-green-400' : error < 7 ? 'text-yellow-400' : 'text-red-400'}`}>
          {actualPercent.toFixed(1)}%
        </span>
      </div>
      <div className="w-12 text-right text-xs text-gray-500">
        n={bucket.sample_size}
      </div>
    </div>
  );
}

// Performance metric card
function MetricCard({ 
  label, 
  value, 
  subtext, 
  color = 'text-white',
  tooltip,
}: { 
  label: string; 
  value: string | number; 
  subtext?: string;
  color?: string;
  tooltip?: string;
}) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="text-xs text-gray-400 mb-1 flex items-center gap-1">
        {label}
        {tooltip && (
          <span className="cursor-help text-gray-500" title={tooltip}>ⓘ</span>
        )}
      </div>
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
      {subtext && <div className="text-xs text-gray-500 mt-1">{subtext}</div>}
    </div>
  );
}

export function ModelPerformance() {
  const { sportId, isLoading: sportLoading } = useSportContext();
  const [days, setDays] = useState(30);
  
  // Get sport key for API
  const sportKey = sportId ? SPORT_SHORT_NAMES[sportId] || 'nba' : 'nba';
  const sportApiKey = sportId ? SPORT_API_KEYS[sportId] || 'basketball_nba' : 'basketball_nba';
  
  // Fetch data
  const { data: calibration, isLoading: calibrationLoading, error: calibrationError } = useCalibrationReport(sportApiKey, days);
  const { data: analytics, isLoading: analyticsLoading } = useAnalyticsDashboard(sportKey, days);
  
  const isLoading = sportLoading || calibrationLoading || analyticsLoading;
  
  if (sportLoading || !sportId) {
    return (
      <div className="p-8 text-center text-gray-400">
        Loading sports...
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Model Performance</h2>
          <p className="text-sm text-gray-400">
            Track hit rates, ROI, and calibration metrics over time
          </p>
        </div>
        
        {/* Time range selector */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">Period:</span>
          <div className="flex bg-gray-800 rounded-lg p-1">
            {[7, 30, 90].map(d => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={`px-3 py-1.5 text-sm font-medium rounded transition-colors ${
                  days === d
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                {d}d
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {/* Loading state */}
      {isLoading && (
        <div className="p-8 text-center text-gray-400">
          <div className="animate-spin inline-block w-6 h-6 border-2 border-gray-400 border-t-transparent rounded-full mr-2" />
          Loading performance data...
        </div>
      )}
      
      {/* Error state */}
      {calibrationError && !isLoading && (
        <div className="bg-yellow-900/20 border border-yellow-700 rounded-lg p-4 text-yellow-400">
          <div className="font-medium mb-1">Limited data available</div>
          <div className="text-sm text-yellow-400/70">
            Not enough settled picks yet to show calibration metrics. Keep betting!
          </div>
        </div>
      )}
      
      {/* Key Metrics Row */}
      {!isLoading && (calibration || analytics) && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {calibration && (
            <>
              <MetricCard 
                label="Total Picks"
                value={calibration.total_picks}
                subtext={`Last ${days} days`}
              />
              <MetricCard 
                label="Overall Hit Rate"
                value={`${(calibration.overall_hit_rate * 100).toFixed(1)}%`}
                color={calibration.overall_hit_rate >= 0.52 ? 'text-green-400' : 'text-red-400'}
                tooltip="Percentage of picks that won"
              />
              <MetricCard 
                label="ROI"
                value={`${calibration.overall_roi > 0 ? '+' : ''}${calibration.overall_roi.toFixed(1)}%`}
                color={calibration.overall_roi > 0 ? 'text-green-400' : 'text-red-400'}
                tooltip="Return on investment from all picks"
              />
              <MetricCard 
                label="Brier Score"
                value={calibration.brier_score.toFixed(3)}
                subtext="Lower is better"
                color={calibration.brier_score < 0.25 ? 'text-green-400' : 'text-yellow-400'}
                tooltip="Measures prediction accuracy (0 = perfect)"
              />
              <MetricCard 
                label="Calibration Error"
                value={`${(calibration.expected_calibration_error * 100).toFixed(1)}%`}
                subtext="ECE"
                color={calibration.expected_calibration_error < 0.05 ? 'text-green-400' : 'text-yellow-400'}
                tooltip="How well probabilities match reality"
              />
              <MetricCard 
                label="Confidence"
                value={calibration.buckets.length > 0 ? '✓' : '—'}
                subtext={`${calibration.buckets.length} buckets`}
                color="text-blue-400"
              />
            </>
          )}
        </div>
      )}
      
      {/* Calibration Chart */}
      {!isLoading && calibration && calibration.buckets.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-white">Calibration by Probability Bucket</h3>
              <p className="text-sm text-gray-400">
                Predicted vs actual hit rate (white line = predicted)
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 bg-green-500 rounded-full" />
                Well calibrated (&lt;3% error)
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 bg-yellow-500 rounded-full" />
                Slight deviation
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 bg-red-500 rounded-full" />
                Needs adjustment
              </span>
            </div>
          </div>
          
          <div className="space-y-1">
            {calibration.buckets.map((bucket, i) => (
              <CalibrationBar key={i} bucket={bucket} />
            ))}
          </div>
        </div>
      )}
      
      {/* Info Box */}
      <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <span className="text-2xl">📊</span>
          <div>
            <div className="font-medium text-white mb-1">Understanding Model Performance</div>
            <div className="text-sm text-gray-400 space-y-2">
              <p><strong>Hit Rate:</strong> {METRIC_EXPLAINERS.hitRate.short}</p>
              <p><strong>Brier Score:</strong> Measures prediction accuracy. 0 is perfect, 0.25 is random guessing.</p>
              <p><strong>Calibration:</strong> A well-calibrated model's 60% predictions should win ~60% of the time.</p>
              <p><strong>CLV:</strong> {METRIC_EXPLAINERS.clv.short}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
