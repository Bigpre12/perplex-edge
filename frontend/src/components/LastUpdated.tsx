/**
 * LastUpdated component - displays data freshness indicator.
 * 
 * Shows "NBA slate last updated: 6:05 AM CT" style text with status coloring.
 */

import { useDataFreshness, SportMetadata } from '../api/public';

// Sport key to display name mapping
const SPORT_NAMES: Record<string, string> = {
  basketball_nba: 'NBA',
  basketball_ncaab: 'NCAAB',
  americanfootball_nfl: 'NFL',
};

interface LastUpdatedBadgeProps {
  sportKey: string;
  metadata: SportMetadata;
  showCounts?: boolean;
}

/**
 * Individual badge showing last updated status for one sport.
 */
function LastUpdatedBadge({ sportKey, metadata, showCounts = false }: LastUpdatedBadgeProps) {
  const sportName = SPORT_NAMES[sportKey] || sportKey.toUpperCase();
  
  // Determine status color based on freshness and health
  let statusColor = 'text-green-400';
  let bgColor = 'bg-green-400/10';
  
  if (!metadata.is_healthy) {
    statusColor = 'text-red-400';
    bgColor = 'bg-red-400/10';
  } else if (metadata.relative === 'never') {
    statusColor = 'text-gray-400';
    bgColor = 'bg-gray-400/10';
  } else if (metadata.relative.includes('d ago')) {
    statusColor = 'text-red-400';
    bgColor = 'bg-red-400/10';
  } else if (metadata.relative.includes('h ago')) {
    const hours = parseInt(metadata.relative);
    if (hours > 6) {
      statusColor = 'text-yellow-400';
      bgColor = 'bg-yellow-400/10';
    }
  }
  
  // Format last updated time for display
  let timeDisplay = 'Never synced';
  if (metadata.last_updated) {
    const date = new Date(metadata.last_updated);
    timeDisplay = date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
      timeZoneName: 'short',
    });
  }
  
  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full ${bgColor}`}>
      {/* Status dot */}
      <span className={`w-2 h-2 rounded-full ${statusColor.replace('text-', 'bg-')}`} />
      
      {/* Sport name and time */}
      <span className={`text-sm font-medium ${statusColor}`}>
        {sportName}
      </span>
      <span className="text-xs text-gray-400">
        {metadata.relative === 'never' ? 'Never synced' : (
          <>Updated {metadata.relative}</>
        )}
      </span>
      
      {/* Optional counts */}
      {showCounts && metadata.games_count !== undefined && (
        <span className="text-xs text-gray-500 border-l border-gray-600 pl-2 ml-1">
          {metadata.games_count}g / {metadata.lines_count || 0}l / {metadata.props_count || 0}p
        </span>
      )}
    </div>
  );
}

interface LastUpdatedProps {
  /** If provided, only show this sport. Otherwise show all. */
  sportKey?: string;
  /** Show detailed counts (games/lines/props) */
  showCounts?: boolean;
  /** Layout: inline (single row) or stacked */
  layout?: 'inline' | 'stacked';
  /** Custom class name */
  className?: string;
}

/**
 * Main LastUpdated component.
 * 
 * Displays data freshness for one or all sports.
 */
export function LastUpdated({ 
  sportKey, 
  showCounts = false, 
  layout = 'inline',
  className = '' 
}: LastUpdatedProps) {
  const { data, isLoading, error } = useDataFreshness();
  
  if (isLoading) {
    return (
      <div className={`text-sm text-gray-400 animate-pulse ${className}`}>
        Loading sync status...
      </div>
    );
  }
  
  if (error || !data) {
    return (
      <div className={`text-sm text-red-400 ${className}`}>
        Unable to fetch sync status
      </div>
    );
  }
  
  // Single sport mode
  if (sportKey && data.sports[sportKey]) {
    return (
      <div className={className}>
        <LastUpdatedBadge
          sportKey={sportKey}
          metadata={data.sports[sportKey]}
          showCounts={showCounts}
        />
      </div>
    );
  }
  
  // All sports mode
  const sportKeys = Object.keys(data.sports);
  
  return (
    <div className={`${layout === 'stacked' ? 'flex flex-col gap-2' : 'flex flex-wrap gap-2'} ${className}`}>
      {sportKeys.map((key) => (
        <LastUpdatedBadge
          key={key}
          sportKey={key}
          metadata={data.sports[key]}
          showCounts={showCounts}
        />
      ))}
    </div>
  );
}

/**
 * Compact version showing just the relative time.
 * Good for headers or small spaces.
 */
export function LastUpdatedCompact({ sportKey }: { sportKey: string }) {
  const { data, isLoading } = useDataFreshness();
  
  if (isLoading || !data || !data.sports[sportKey]) {
    return <span className="text-xs text-gray-500">--</span>;
  }
  
  const metadata = data.sports[sportKey];
  const isStale = !metadata.is_healthy || metadata.relative.includes('d ago');
  
  return (
    <span className={`text-xs ${isStale ? 'text-yellow-400' : 'text-gray-400'}`}>
      Updated {metadata.relative}
    </span>
  );
}

export default LastUpdated;
