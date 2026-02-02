/**
 * Freshness Banner
 * 
 * A compact status banner showing last odds update time.
 * Builds trust by showing users the data is fresh.
 */

import { useDataFreshness } from '../api/public';
import { useSportContext } from '../context/SportContext';
import { SPORT_CONFIG } from '../constants/sports';

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

interface FreshnessBannerProps {
  className?: string;
}

export function FreshnessBanner({ className = '' }: FreshnessBannerProps) {
  const { sportId } = useSportContext();
  const { data, isLoading, error } = useDataFreshness();
  
  if (isLoading) {
    return (
      <div className={`text-xs text-gray-500 animate-pulse ${className}`}>
        Checking data freshness...
      </div>
    );
  }
  
  if (error || !data) {
    return null; // Don't show anything on error
  }
  
  // Get the sport key for the current sport
  const sportKey = sportId ? SPORT_API_KEYS[sportId] : null;
  const sportConfig = sportId ? SPORT_CONFIG[sportId] : null;
  
  if (!sportKey || !data.sports[sportKey]) {
    return null;
  }
  
  const metadata = data.sports[sportKey];
  
  // Determine status
  let statusIcon = '🟢';
  let statusColor = 'text-green-400';
  
  if (!metadata.is_healthy) {
    statusIcon = '🔴';
    statusColor = 'text-red-400';
  } else if (metadata.relative === 'never') {
    statusIcon = '⚪';
    statusColor = 'text-gray-400';
  } else if (metadata.relative.includes('d ago')) {
    statusIcon = '🟠';
    statusColor = 'text-orange-400';
  } else if (metadata.relative.includes('h ago')) {
    const hours = parseInt(metadata.relative);
    if (hours > 6) {
      statusIcon = '🟡';
      statusColor = 'text-yellow-400';
    }
  }
  
  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1 bg-gray-800/50 rounded-full border border-gray-700 ${className}`}>
      <span className="text-sm">{statusIcon}</span>
      <span className="text-xs text-gray-400">
        {sportConfig?.name || 'Data'} updated{' '}
        <span className={statusColor}>
          {metadata.relative === 'never' ? 'never' : metadata.relative}
        </span>
      </span>
      {metadata.props_count !== undefined && metadata.props_count > 0 && (
        <span className="text-xs text-gray-500 border-l border-gray-600 pl-2">
          {metadata.props_count} props
        </span>
      )}
    </div>
  );
}

/**
 * Full freshness status showing all sports
 */
export function FreshnessStatus() {
  const { data, isLoading, error } = useDataFreshness();
  
  if (isLoading) {
    return (
      <div className="text-center text-gray-400 py-4">
        <div className="animate-spin inline-block w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full mr-2" />
        Checking sync status...
      </div>
    );
  }
  
  if (error || !data) {
    return (
      <div className="text-center text-red-400 py-4">
        Unable to fetch sync status
      </div>
    );
  }
  
  const healthySports = Object.entries(data.sports).filter(([, metadata]) => metadata.is_healthy).length;
  const totalSports = Object.keys(data.sports).length;
  
  return (
    <div className="space-y-3">
      {/* Summary */}
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-400">
          System Status: {healthySports}/{totalSports} sports healthy
        </span>
        <span className={`${healthySports === totalSports ? 'text-green-400' : 'text-yellow-400'}`}>
          {healthySports === totalSports ? '✓ All systems operational' : '⚠ Some sports need sync'}
        </span>
      </div>
      
      {/* Per-sport breakdown */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {Object.entries(data.sports).map(([key, metadata]) => {
          const sportId = Object.entries(SPORT_API_KEYS).find(([, apiKey]) => apiKey === key)?.[0];
          const config = sportId ? SPORT_CONFIG[parseInt(sportId)] : null;
          
          return (
            <div 
              key={key}
              className={`p-2 rounded-lg border ${
                metadata.is_healthy 
                  ? 'bg-green-900/10 border-green-800' 
                  : 'bg-red-900/10 border-red-800'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span>{config?.icon || '🏆'}</span>
                <span className="text-sm font-medium text-white">{config?.name || key}</span>
              </div>
              <div className="text-xs text-gray-400">
                Updated: {metadata.relative}
              </div>
              {metadata.props_count !== undefined && (
                <div className="text-xs text-gray-500">
                  {metadata.games_count || 0} games, {metadata.props_count} props
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default FreshnessBanner;
