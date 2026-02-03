/**
 * Admin Dashboard - Sports Data Health Monitor
 *
 * Displays per-sport health status with:
 * - Games scheduled in next 24h
 * - Current player props count
 * - Sportsbook coverage
 * - Data freshness
 * - Automated issue detection
 */

import { useAdminDashboard, SportHealth, SportHealthStatus } from '../api/public';
import { SPORT_KEY_TO_NAME } from '../constants/sports';

// Status badge colors
const STATUS_COLORS: Record<SportHealthStatus, string> = {
  ok: 'bg-green-900/50 text-green-400 border-green-700',
  warn: 'bg-yellow-900/50 text-yellow-400 border-yellow-700',
  error: 'bg-red-900/50 text-red-400 border-red-700',
};

const STATUS_DOT_COLORS: Record<SportHealthStatus, string> = {
  ok: 'bg-green-500',
  warn: 'bg-yellow-500',
  error: 'bg-red-500',
};

function StatusBadge({ status }: { status: SportHealthStatus }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-xs font-medium ${STATUS_COLORS[status]}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${STATUS_DOT_COLORS[status]}`} />
      {status.toUpperCase()}
    </span>
  );
}

function formatLastUpdate(isoString: string | null): string {
  if (!isoString) return '—';
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);

  if (diffMin < 1) return 'Just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  return date.toLocaleDateString();
}

function getSportDisplayName(sportKey: string): string {
  return SPORT_KEY_TO_NAME[sportKey] || sportKey.split('_').pop()?.toUpperCase() || sportKey;
}

export function AdminDashboard() {
  const { data, isLoading, isError, refetch } = useAdminDashboard();

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-700 rounded w-64 mb-4" />
          <div className="h-4 bg-gray-700 rounded w-48 mb-6" />
          <div className="space-y-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-800 rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-6">
        <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
          <h2 className="text-red-400 font-semibold mb-2">Failed to load dashboard</h2>
          <p className="text-gray-400 text-sm mb-3">
            Could not connect to the admin API. Check if the backend is running.
          </p>
          <button
            onClick={() => refetch()}
            className="px-3 py-1.5 bg-red-800 hover:bg-red-700 text-red-200 rounded text-sm"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Calculate summary stats
  const errorCount = data.sports.filter((s) => s.status === 'error').length;
  const warnCount = data.sports.filter((s) => s.status === 'warn').length;
  const okCount = data.sports.filter((s) => s.status === 'ok').length;
  const totalGames = data.sports.reduce((sum, s) => sum + s.game_count, 0);
  const totalProps = data.sports.reduce((sum, s) => sum + s.prop_count, 0);

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-white">Sports Data Health</h1>
          <p className="text-xs text-gray-400 mt-1">
            Last check: {new Date(data.now).toLocaleTimeString()} (auto-refresh every 60s)
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-gray-200 rounded text-sm flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-white">{data.sports.length}</div>
          <div className="text-xs text-gray-400">Sports Tracked</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-white">{totalGames}</div>
          <div className="text-xs text-gray-400">Games (24h)</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-2xl font-bold text-white">{totalProps.toLocaleString()}</div>
          <div className="text-xs text-gray-400">Active Props</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className={`text-2xl font-bold ${errorCount > 0 ? 'text-red-400' : 'text-green-400'}`}>
            {okCount}/{data.sports.length}
          </div>
          <div className="text-xs text-gray-400">Healthy</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className={`text-2xl font-bold ${errorCount > 0 ? 'text-red-400' : warnCount > 0 ? 'text-yellow-400' : 'text-green-400'}`}>
            {errorCount > 0 ? errorCount : warnCount}
          </div>
          <div className="text-xs text-gray-400">{errorCount > 0 ? 'Errors' : 'Warnings'}</div>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-900/50 border-b border-gray-700">
              <th className="text-left px-4 py-3 text-gray-400 font-medium">Sport</th>
              <th className="text-right px-4 py-3 text-gray-400 font-medium">Games (24h)</th>
              <th className="text-right px-4 py-3 text-gray-400 font-medium">Props</th>
              <th className="text-right px-4 py-3 text-gray-400 font-medium">Books</th>
              <th className="text-left px-4 py-3 text-gray-400 font-medium">Last Update</th>
              <th className="text-center px-4 py-3 text-gray-400 font-medium">Status</th>
              <th className="text-left px-4 py-3 text-gray-400 font-medium">Issues</th>
            </tr>
          </thead>
          <tbody>
            {data.sports.map((sport: SportHealth) => (
              <tr
                key={sport.sport_id}
                className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors"
              >
                <td className="px-4 py-3">
                  <span className="font-medium text-white">
                    {getSportDisplayName(sport.sport_key)}
                  </span>
                  <span className="text-xs text-gray-500 ml-2">({sport.sport_id})</span>
                </td>
                <td className="px-4 py-3 text-right text-gray-300">{sport.game_count}</td>
                <td className="px-4 py-3 text-right text-gray-300">
                  {sport.prop_count.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right">
                  <span
                    className={
                      sport.book_count === 0
                        ? 'text-red-400'
                        : sport.book_count === 1
                        ? 'text-yellow-400'
                        : 'text-gray-300'
                    }
                  >
                    {sport.book_count}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-400 text-sm">
                  {formatLastUpdate(sport.last_update)}
                </td>
                <td className="px-4 py-3 text-center">
                  <StatusBadge status={sport.status} />
                </td>
                <td className="px-4 py-3">
                  {sport.issues.length > 0 ? (
                    <span className="text-yellow-400 text-sm">{sport.issues.join('; ')}</span>
                  ) : (
                    <span className="text-gray-500">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="mt-4 text-xs text-gray-500">
        <p className="mb-1">
          <strong>Status Guide:</strong>
        </p>
        <ul className="list-disc list-inside space-y-0.5">
          <li>
            <span className="text-red-400">ERROR</span>: Games scheduled but no props (ETL/mapping
            issue)
          </li>
          <li>
            <span className="text-yellow-400">WARN</span>: Single-book data or stale odds (&gt;10
            min)
          </li>
          <li>
            <span className="text-green-400">OK</span>: Data is fresh with multiple books
          </li>
        </ul>
      </div>
    </div>
  );
}
