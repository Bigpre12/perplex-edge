/**
 * StreaksPanel - Combined hot and cold streaks in a single panel.
 * 
 * Shows players on winning streaks (hot) and losing streaks (cold)
 * in a compact, side-by-side or tabbed view.
 */

import { useState } from 'react';
import { useStreaks, StreakPlayer } from '../api/public';
import { STAT_TYPE_LABELS } from '../config/sports';
import type { StatType } from '../config/sports';

interface StreaksPanelProps {
  sportId: number | null;
  minStreak?: number;
  limit?: number;
}

// Streak row component
function formatStatLabel(statType: string | null): string {
  if (!statType) return '';
  return STAT_TYPE_LABELS[statType as StatType] ?? statType.toUpperCase();
}

function StreakRow({ player, type }: { player: StreakPlayer; type: 'hot' | 'cold' }) {
  const isHot = type === 'hot';
  const statLabel = formatStatLabel(player.stat_type);
  const dirLabel = player.direction ? player.direction.toUpperCase() : '';
  
  return (
    <div className="flex items-center justify-between py-2 px-3 bg-gray-900/30 rounded hover:bg-gray-900/50 transition-colors">
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-white text-sm truncate">{player.player_name}</span>
          {player.last_5 && (
            <span className="text-[10px] text-gray-500 hidden sm:inline">
              {player.last_5}
            </span>
          )}
        </div>
        {(statLabel || dirLabel) && (
          <div className="text-xs text-gray-400 mt-0.5">
            {statLabel}{dirLabel ? ` ${dirLabel}` : ''}
          </div>
        )}
      </div>
      <div className="flex items-center gap-2 shrink-0">
        {player.hit_rate_7d !== null && (
          <span className={`text-xs ${isHot ? 'text-green-400/70' : 'text-red-400/70'}`}>
            {(player.hit_rate_7d * 100).toFixed(0)}%
          </span>
        )}
        <span className={`font-bold text-sm ${isHot ? 'text-green-400' : 'text-red-400'}`}>
          {isHot ? '+' : ''}{player.streak}
        </span>
      </div>
    </div>
  );
}

// Section for a streak type
function StreakSection({ 
  title, 
  players, 
  type, 
  emptyMessage 
}: { 
  title: string; 
  players: StreakPlayer[]; 
  type: 'hot' | 'cold';
  emptyMessage: string;
}) {
  const isHot = type === 'hot';
  
  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <span className={`w-2 h-2 rounded-full ${isHot ? 'bg-green-400' : 'bg-red-400'}`} />
        <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wide">
          {title}
        </h4>
      </div>
      
      {players.length === 0 ? (
        <div className="text-xs text-gray-500 py-3 text-center">
          {emptyMessage}
        </div>
      ) : (
        <div className="space-y-1">
          {players.slice(0, 5).map((player) => (
            <StreakRow key={`${player.player_id}-${player.stat_type}-${player.direction}`} player={player} type={type} />
          ))}
        </div>
      )}
    </div>
  );
}

export function StreaksPanel({ sportId, minStreak = 3, limit = 10 }: StreaksPanelProps) {
  const [activeTab, setActiveTab] = useState<'all' | 'hot' | 'cold'>('all');
  const { data: streaks, isLoading, error } = useStreaks(sportId, minStreak, limit);

  // Loading state
  if (isLoading) {
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="p-4 border-b border-gray-700">
          <h3 className="font-bold text-white">Win / Lose Streaks</h3>
          <p className="text-xs text-gray-400">Players on {minStreak}+ consecutive results</p>
        </div>
        <div className="p-4">
          <div className="animate-pulse space-y-2">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-8 bg-gray-700/50 rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="p-4 border-b border-gray-700">
          <h3 className="font-bold text-white">Win / Lose Streaks</h3>
        </div>
        <div className="p-4 text-xs text-red-400">
          Could not load streaks. Please try again.
        </div>
      </div>
    );
  }

  const hotPlayers = streaks?.hot || [];
  const coldPlayers = streaks?.cold || [];
  const hasData = hotPlayers.length > 0 || coldPlayers.length > 0;

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      {/* Header with tabs */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h3 className="font-bold text-white">Win / Lose Streaks</h3>
            <p className="text-xs text-gray-400">Players on {minStreak}+ consecutive results</p>
          </div>
        </div>
        
        {/* Tab buttons */}
        <div className="flex gap-1 mt-3">
          {(['all', 'hot', 'cold'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1 text-xs rounded transition-colors ${
                activeTab === tab
                  ? tab === 'hot' 
                    ? 'bg-green-600 text-white'
                    : tab === 'cold'
                    ? 'bg-red-600 text-white'
                    : 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {tab === 'all' ? 'All' : tab === 'hot' ? `Hot (${hotPlayers.length})` : `Cold (${coldPlayers.length})`}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {!hasData ? (
          <div className="text-center py-6 text-gray-500 text-sm">
            No active streaks found
          </div>
        ) : (
          <div className="space-y-4">
            {/* Hot streaks */}
            {(activeTab === 'all' || activeTab === 'hot') && (
              <StreakSection
                title="Hot Streaks"
                players={hotPlayers}
                type="hot"
                emptyMessage="No hot streaks"
              />
            )}
            
            {/* Cold streaks */}
            {(activeTab === 'all' || activeTab === 'cold') && (
              <StreakSection
                title="Cold Streaks"
                players={coldPlayers}
                type="cold"
                emptyMessage="No cold streaks"
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default StreaksPanel;
