import { useEffect, useState } from 'react';
import { api, InjuryList } from '../api/client';

export function InjuryTracker() {
  const [injuries, setInjuries] = useState<InjuryList | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchInjuries() {
      try {
        setLoading(true);
        const data = await api.getInjuries({
          status: statusFilter || undefined,
          limit: 50,
        });
        setInjuries(data);
      } catch (err) {
        console.error('Failed to fetch injuries:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchInjuries();
  }, [statusFilter]);

  const statusColors: Record<string, string> = {
    OUT: 'bg-red-900/50 text-red-400 border-red-700',
    DOUBTFUL: 'bg-orange-900/50 text-orange-400 border-orange-700',
    QUESTIONABLE: 'bg-yellow-900/50 text-yellow-400 border-yellow-700',
    PROBABLE: 'bg-green-900/50 text-green-400 border-green-700',
    GTD: 'bg-purple-900/50 text-purple-400 border-purple-700',
    AVAILABLE: 'bg-blue-900/50 text-blue-400 border-blue-700',
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-4 bg-gray-800 rounded-lg p-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Status</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-gray-700 text-white rounded px-3 py-2"
          >
            <option value="">All Statuses</option>
            <option value="OUT">Out</option>
            <option value="DOUBTFUL">Doubtful</option>
            <option value="QUESTIONABLE">Questionable</option>
            <option value="PROBABLE">Probable</option>
            <option value="GTD">Game-Time Decision</option>
          </select>
        </div>
      </div>

      {/* Injuries List */}
      {injuries && injuries.items.length > 0 ? (
        <div className="bg-gray-800 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-700">
                <th className="text-left px-4 py-3 text-gray-300 font-medium">Player</th>
                <th className="text-left px-4 py-3 text-gray-300 font-medium">Team</th>
                <th className="text-left px-4 py-3 text-gray-300 font-medium">Position</th>
                <th className="text-left px-4 py-3 text-gray-300 font-medium">Status</th>
                <th className="text-left px-4 py-3 text-gray-300 font-medium">Details</th>
                <th className="text-left px-4 py-3 text-gray-300 font-medium">Updated</th>
              </tr>
            </thead>
            <tbody>
              {injuries.items.map((injury) => (
                <tr key={injury.id} className="border-t border-gray-700 hover:bg-gray-700/50">
                  <td className="px-4 py-3">
                    <span className="text-white font-medium">{injury.player_name}</span>
                  </td>
                  <td className="px-4 py-3 text-gray-300">{injury.team_name || '-'}</td>
                  <td className="px-4 py-3 text-gray-300">{injury.position || '-'}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded border ${
                        statusColors[injury.status] || 'bg-gray-700 text-gray-300'
                      }`}
                    >
                      {injury.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-sm max-w-xs truncate">
                    {injury.status_detail || '-'}
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-sm">
                    {new Date(injury.updated_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg p-8 text-center">
          <p className="text-gray-400">No injuries reported</p>
          <p className="text-sm text-gray-500 mt-2">
            Injury data will appear here once synced
          </p>
        </div>
      )}

      {/* Legend */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-300 mb-3">Status Legend</h4>
        <div className="flex flex-wrap gap-3">
          {Object.entries(statusColors).map(([status, color]) => (
            <span key={status} className={`px-2 py-1 text-xs rounded border ${color}`}>
              {status}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
