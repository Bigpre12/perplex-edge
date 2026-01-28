import { useEffect, useState } from 'react';
import { api, SyncStatus, PickSummary, GameList } from '../api/client';

export function Dashboard() {
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [picksSummary, setPicksSummary] = useState<PickSummary | null>(null);
  const [todaysGames, setTodaysGames] = useState<GameList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [status, summary, games] = await Promise.all([
          api.getSyncStatus().catch(() => null),
          api.getPicksSummary().catch(() => null),
          api.getTodaysGames().catch(() => null),
        ]);
        setSyncStatus(status);
        setPicksSummary(summary);
        setTodaysGames(games);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
        <p className="text-red-400">Error: {error}</p>
        <p className="text-sm text-gray-400 mt-2">Make sure the backend is running on port 8000</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Today's Games"
          value={todaysGames?.total ?? 0}
          subtitle="Scheduled"
          color="blue"
        />
        <StatCard
          title="Active Picks"
          value={picksSummary?.active_picks ?? 0}
          subtitle={`${picksSummary?.high_confidence_picks ?? 0} high confidence`}
          color="green"
        />
        <StatCard
          title="Avg EV"
          value={picksSummary ? `${(picksSummary.avg_ev * 100).toFixed(1)}%` : '0%'}
          subtitle="Expected value"
          color="purple"
        />
        <StatCard
          title="Current Lines"
          value={syncStatus?.counts.lines.current ?? 0}
          subtitle={`${syncStatus?.counts.lines.total ?? 0} total`}
          color="orange"
        />
      </div>

      {/* Data Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Today's Games */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-white mb-4">Today's Games</h3>
          {todaysGames && todaysGames.items.length > 0 ? (
            <div className="space-y-2">
              {todaysGames.items.slice(0, 5).map((game) => (
                <div
                  key={game.id}
                  className="flex items-center justify-between p-3 bg-gray-700/50 rounded"
                >
                  <div>
                    <p className="text-white font-medium">
                      {game.away_team.abbreviation || game.away_team.name} @{' '}
                      {game.home_team.abbreviation || game.home_team.name}
                    </p>
                    <p className="text-sm text-gray-400">
                      {new Date(game.start_time).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs rounded ${
                      game.status === 'scheduled'
                        ? 'bg-blue-900/50 text-blue-400'
                        : game.status === 'in_progress'
                        ? 'bg-green-900/50 text-green-400'
                        : 'bg-gray-600 text-gray-300'
                    }`}
                  >
                    {game.status}
                  </span>
                </div>
              ))}
              {todaysGames.total > 5 && (
                <p className="text-sm text-gray-400 text-center pt-2">
                  +{todaysGames.total - 5} more games
                </p>
              )}
            </div>
          ) : (
            <p className="text-gray-400">No games scheduled for today</p>
          )}
        </div>

        {/* System Status */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-white mb-4">System Status</h3>
          {syncStatus ? (
            <div className="space-y-3">
              <StatusRow label="Sports" value={syncStatus.counts.sports} />
              <StatusRow label="Games" value={syncStatus.counts.games} />
              <StatusRow
                label="Lines"
                value={`${syncStatus.counts.lines.current} current / ${syncStatus.counts.lines.total} total`}
              />
              <StatusRow label="Injuries" value={syncStatus.counts.injuries} />
              <StatusRow
                label="Picks"
                value={`${syncStatus.counts.picks.active} active / ${syncStatus.counts.picks.total} total`}
              />
            </div>
          ) : (
            <p className="text-gray-400">Unable to load status</p>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  subtitle,
  color,
}: {
  title: string;
  value: string | number;
  subtitle: string;
  color: 'blue' | 'green' | 'purple' | 'orange';
}) {
  const colors = {
    blue: 'bg-blue-900/30 border-blue-700',
    green: 'bg-green-900/30 border-green-700',
    purple: 'bg-purple-900/30 border-purple-700',
    orange: 'bg-orange-900/30 border-orange-700',
  };

  return (
    <div className={`rounded-lg border p-4 ${colors[color]}`}>
      <p className="text-sm text-gray-400">{title}</p>
      <p className="text-3xl font-bold text-white mt-1">{value}</p>
      <p className="text-sm text-gray-400 mt-1">{subtitle}</p>
    </div>
  );
}

function StatusRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-gray-700 last:border-0">
      <span className="text-gray-400">{label}</span>
      <span className="text-white font-medium">{value}</span>
    </div>
  );
}
