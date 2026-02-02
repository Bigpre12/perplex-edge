import { useTonightSummary, SportTonightSummary } from '../api/public';

// =============================================================================
// Sport Card Component
// =============================================================================

interface SportCardProps {
  sport: SportTonightSummary;
  onSelect?: (sportId: number) => void;
}

function SportCard({ sport, onSelect }: SportCardProps) {
  const qualityColors = {
    loaded: 'border-green-500 bg-green-900/20',
    normal: 'border-blue-500 bg-blue-900/20',
    thin: 'border-yellow-500 bg-yellow-900/20',
    empty: 'border-gray-600 bg-gray-800/50',
  };
  
  const qualityBadges = {
    loaded: { bg: 'bg-green-500', text: 'LOADED' },
    normal: { bg: 'bg-blue-500', text: 'NORMAL' },
    thin: { bg: 'bg-yellow-500', text: 'THIN' },
    empty: { bg: 'bg-gray-600', text: 'EMPTY' },
  };
  
  const badge = qualityBadges[sport.slate_quality];
  
  return (
    <div
      onClick={() => onSelect?.(sport.sport_id)}
      className={`rounded-lg border-2 p-4 cursor-pointer transition-all hover:scale-[1.02] ${qualityColors[sport.slate_quality]}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-bold text-white">{sport.sport_name}</h3>
        <span className={`px-2 py-0.5 rounded text-xs font-bold text-white ${badge.bg}`}>
          {badge.text}
        </span>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <div className="text-2xl font-bold text-white">{sport.games_count}</div>
          <div className="text-xs text-gray-400">Games</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-white">{sport.props_count}</div>
          <div className="text-xs text-gray-400">Props</div>
        </div>
      </div>
      
      {/* Best EV */}
      {sport.best_ev !== null && sport.best_ev > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-700">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">Best EV</span>
            <span className="text-green-400 font-bold">
              +{(sport.best_ev * 100).toFixed(1)}%
            </span>
          </div>
          {sport.avg_ev !== null && (
            <div className="flex items-center justify-between mt-1">
              <span className="text-xs text-gray-400">Avg EV</span>
              <span className={`text-sm ${sport.avg_ev > 0 ? 'text-green-400' : 'text-gray-400'}`}>
                {sport.avg_ev > 0 ? '+' : ''}{(sport.avg_ev * 100).toFixed(1)}%
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Main Tonight Dashboard Component
// =============================================================================

interface TonightDashboardProps {
  onSelectSport?: (sportId: number) => void;
}

export function TonightDashboard({ onSelectSport }: TonightDashboardProps) {
  const { data, isLoading, error } = useTonightSummary();
  
  if (isLoading) {
    return (
      <div className="bg-gray-800/50 rounded-lg p-6 text-center">
        <div className="animate-spin inline-block w-6 h-6 border-2 border-purple-400 border-t-transparent rounded-full mb-2" />
        <div className="text-gray-400">Loading tonight's slate...</div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 text-red-400">
        Failed to load tonight's summary
      </div>
    );
  }
  
  if (!data) {
    return null;
  }
  
  const overallBadges = {
    loaded: { bg: 'bg-green-500', text: 'LOADED SLATE', icon: '🔥' },
    normal: { bg: 'bg-blue-500', text: 'NORMAL SLATE', icon: '✅' },
    thin: { bg: 'bg-yellow-500', text: 'THIN SLATE', icon: '⚠️' },
    empty: { bg: 'bg-gray-600', text: 'NO ACTION', icon: '😴' },
  };
  
  const overall = overallBadges[data.slate_quality];
  
  return (
    <div className="space-y-4">
      {/* Header with overall stats */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-lg p-4 border border-gray-700">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">{overall.icon}</span>
              <h2 className="text-xl font-bold text-white">What's On Tonight</h2>
              <span className={`px-3 py-1 rounded-full text-sm font-bold text-white ${overall.bg}`}>
                {overall.text}
              </span>
            </div>
            <div className="text-sm text-gray-400 mt-1">
              {data.date} ({data.timezone})
            </div>
          </div>
          
          {/* Summary stats */}
          <div className="flex items-center gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{data.total_games}</div>
              <div className="text-xs text-gray-400">Total Games</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{data.total_props}</div>
              <div className="text-xs text-gray-400">Total Props</div>
            </div>
            {data.overall_best_ev !== null && (
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">
                  +{(data.overall_best_ev * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-gray-400">Best Edge</div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Sport cards grid */}
      {data.sports.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {data.sports.map((sport) => (
            <SportCard
              key={sport.sport_id}
              sport={sport}
              onSelect={onSelectSport}
            />
          ))}
        </div>
      ) : (
        <div className="bg-gray-800/50 rounded-lg p-8 text-center">
          <div className="text-4xl mb-4">😴</div>
          <div className="text-gray-300 text-lg">No games scheduled for tonight</div>
          <div className="text-gray-500 text-sm mt-2">Check back later or look at tomorrow's slate</div>
        </div>
      )}
      
      {/* Advice based on slate quality */}
      {data.sports.length > 0 && (
        <div className={`rounded-lg p-3 text-sm ${
          data.slate_quality === 'loaded' ? 'bg-green-900/20 border border-green-700 text-green-300' :
          data.slate_quality === 'normal' ? 'bg-blue-900/20 border border-blue-700 text-blue-300' :
          data.slate_quality === 'thin' ? 'bg-yellow-900/20 border border-yellow-700 text-yellow-300' :
          'bg-gray-800 border border-gray-700 text-gray-400'
        }`}>
          {data.slate_quality === 'loaded' && (
            <span><strong>Loaded slate!</strong> Plenty of action tonight. Focus on the highest EV props and stick to your filters.</span>
          )}
          {data.slate_quality === 'normal' && (
            <span><strong>Normal slate.</strong> Good number of options. Be selective and prioritize quality over quantity.</span>
          )}
          {data.slate_quality === 'thin' && (
            <span><strong>Thin slate.</strong> Limited action tonight. Consider smaller position sizes or passing if edges aren't strong.</span>
          )}
          {data.slate_quality === 'empty' && (
            <span><strong>No action tonight.</strong> Take the night off or research tomorrow's slate.</span>
          )}
        </div>
      )}
    </div>
  );
}
