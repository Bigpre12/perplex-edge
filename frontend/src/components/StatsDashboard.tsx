import { useSports, useHotPlayers, useColdPlayers, useStreaks, useRecentResults } from '../api/public';
import { useSport } from '../context/SportContext';

export function StatsDashboard() {
  const { sportId } = useSport();
  const { data: sportsData } = useSports();
  
  // Use NBA as default if no sport selected
  const activeSportId = sportId || sportsData?.items?.[0]?.id || null;
  
  const { data: hotPlayers, isLoading: hotLoading } = useHotPlayers(activeSportId, 3, 10);
  const { data: coldPlayers, isLoading: coldLoading } = useColdPlayers(activeSportId, 3, 10);
  const { data: streaks, isLoading: streaksLoading } = useStreaks(activeSportId, 3);
  const { data: recentResults, isLoading: recentLoading } = useRecentResults(activeSportId, 20);

  // Format helpers
  const formatPercent = (value: number | null) => value !== null ? `${(value * 100).toFixed(1)}%` : '-';
  const formatStreak = (streak: number) => {
    if (streak > 0) return `+${streak}`;
    return streak.toString();
  };
  const formatTime = (iso: string) => {
    const date = new Date(iso);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  // Render last 5 results as colored dots
  const renderLast5 = (last5: string | null) => {
    if (!last5) return null;
    return (
      <div className="flex gap-0.5">
        {last5.split('').map((result, i) => (
          <span
            key={i}
            className={`w-2 h-2 rounded-full ${
              result === 'W' ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Hot Players Panel */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center gap-2 mb-4">
          <svg className="w-5 h-5 text-orange-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd" />
          </svg>
          <h2 className="text-lg font-semibold text-white">Hot Players</h2>
          <span className="text-sm text-gray-400">(7-day hit rate)</span>
        </div>
        
        {hotLoading ? (
          <div className="animate-pulse space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-700 rounded" />
            ))}
          </div>
        ) : hotPlayers?.items.length === 0 ? (
          <p className="text-gray-400 text-sm">No data yet. Results will appear after games settle.</p>
        ) : (
          <div className="space-y-2">
            {hotPlayers?.items.map((player, idx) => (
              <div
                key={player.player_id}
                className="flex items-center justify-between bg-gray-900 rounded-lg px-4 py-3 border border-gray-700"
              >
                <div className="flex items-center gap-3">
                  <span className={`text-sm font-bold w-6 ${idx < 3 ? 'text-orange-400' : 'text-gray-500'}`}>
                    #{idx + 1}
                  </span>
                  <div>
                    <p className="text-white font-medium">{player.player_name}</p>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <span>{player.hits_7d}/{player.total_7d} picks</span>
                      {renderLast5(player.last_5)}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xl font-bold text-green-400">{formatPercent(player.hit_rate_7d)}</p>
                  <p className={`text-xs ${player.current_streak > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {formatStreak(player.current_streak)} streak
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Streaks Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hot Streaks */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            <h2 className="text-lg font-semibold text-white">Win Streaks</h2>
          </div>
          
          {streaksLoading ? (
            <div className="animate-pulse space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-10 bg-gray-700 rounded" />
              ))}
            </div>
          ) : streaks?.hot.length === 0 ? (
            <p className="text-gray-400 text-sm">No players on 3+ win streaks</p>
          ) : (
            <div className="space-y-2">
              {streaks?.hot.map((player) => (
                <div
                  key={player.player_id}
                  className="flex items-center justify-between bg-green-900/20 rounded-lg px-4 py-2 border border-green-800/30"
                >
                  <div>
                    <p className="text-white font-medium">{player.player_name}</p>
                    {renderLast5(player.last_5)}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl font-bold text-green-400">+{player.streak}</span>
                    <svg className="w-4 h-4 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Cold Streaks */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
            </svg>
            <h2 className="text-lg font-semibold text-white">Cold Streaks</h2>
          </div>
          
          {streaksLoading ? (
            <div className="animate-pulse space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-10 bg-gray-700 rounded" />
              ))}
            </div>
          ) : streaks?.cold.length === 0 ? (
            <p className="text-gray-400 text-sm">No players on 3+ loss streaks</p>
          ) : (
            <div className="space-y-2">
              {streaks?.cold.map((player) => (
                <div
                  key={player.player_id}
                  className="flex items-center justify-between bg-red-900/20 rounded-lg px-4 py-2 border border-red-800/30"
                >
                  <div>
                    <p className="text-white font-medium">{player.player_name}</p>
                    {renderLast5(player.last_5)}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl font-bold text-red-400">{player.streak}</span>
                    <svg className="w-4 h-4 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.599-.8a1 1 0 01.894 1.79l-1.233.616 1.738 5.42a1 1 0 01-.285 1.05A3.989 3.989 0 0115 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.715-5.349L11 6.477V16h2a1 1 0 110 2H7a1 1 0 110-2h2V6.477L6.237 7.582l1.715 5.349a1 1 0 01-.285 1.05A3.989 3.989 0 015 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.738-5.42-1.233-.617a1 1 0 01.894-1.788l1.599.799L9 4.323V3a1 1 0 011-1z" />
                    </svg>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent Results Feed */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center gap-2 mb-4">
          <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className="text-lg font-semibold text-white">Recent Results</h2>
        </div>
        
        {recentLoading ? (
          <div className="animate-pulse space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-14 bg-gray-700 rounded" />
            ))}
          </div>
        ) : recentResults?.items.length === 0 ? (
          <p className="text-gray-400 text-sm">No results yet. Results will appear after games settle.</p>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {recentResults?.items.map((result) => (
              <div
                key={result.result_id}
                className={`flex items-center justify-between rounded-lg px-4 py-3 border ${
                  result.hit 
                    ? 'bg-green-900/20 border-green-800/30' 
                    : 'bg-red-900/20 border-red-800/30'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    result.hit ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                  }`}>
                    {result.hit ? 'HIT' : 'MISS'}
                  </span>
                  <div>
                    <p className="text-white font-medium">{result.player_name}</p>
                    <p className="text-xs text-gray-400">
                      {result.stat_type} {result.side.toUpperCase()} {result.line}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-lg font-bold ${result.hit ? 'text-green-400' : 'text-red-400'}`}>
                    {result.actual_value}
                  </p>
                  <p className="text-xs text-gray-500">{formatTime(result.settled_at)}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Cold Players Panel */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center gap-2 mb-4">
          <svg className="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.599-.8a1 1 0 01.894 1.79l-1.233.616 1.738 5.42a1 1 0 01-.285 1.05A3.989 3.989 0 0115 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.715-5.349L11 6.477V16h2a1 1 0 110 2H7a1 1 0 110-2h2V6.477L6.237 7.582l1.715 5.349a1 1 0 01-.285 1.05A3.989 3.989 0 015 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.738-5.42-1.233-.617a1 1 0 01.894-1.788l1.599.799L9 4.323V3a1 1 0 011-1z" />
          </svg>
          <h2 className="text-lg font-semibold text-white">Cold Players</h2>
          <span className="text-sm text-gray-400">(fade candidates)</span>
        </div>
        
        {coldLoading ? (
          <div className="animate-pulse space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-700 rounded" />
            ))}
          </div>
        ) : coldPlayers?.items.length === 0 ? (
          <p className="text-gray-400 text-sm">No data yet.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {coldPlayers?.items.slice(0, 6).map((player) => (
              <div
                key={player.player_id}
                className="flex items-center justify-between bg-gray-900 rounded-lg px-4 py-3 border border-gray-700"
              >
                <div>
                  <p className="text-white font-medium">{player.player_name}</p>
                  <div className="flex items-center gap-2 text-xs text-gray-400">
                    <span>{player.hits_7d}/{player.total_7d} picks</span>
                    {renderLast5(player.last_5)}
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xl font-bold text-red-400">{formatPercent(player.hit_rate_7d)}</p>
                  <p className={`text-xs ${player.current_streak < 0 ? 'text-red-400' : 'text-green-400'}`}>
                    {formatStreak(player.current_streak)} streak
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default StatsDashboard;
