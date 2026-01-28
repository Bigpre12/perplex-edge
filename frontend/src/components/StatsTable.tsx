import { useState, useMemo } from 'react';
import { HitRateRecord, STAT_TYPE_OPTIONS } from '../api/public';

interface StatsTableProps {
  data: HitRateRecord[];
  isLoading?: boolean;
}

type SortField = 'player_name' | 'stat_type' | 'total_picks' | 'hits' | 'hit_rate_percentage' | 'avg_ev';
type SortDirection = 'asc' | 'desc';

export function StatsTable({ data, isLoading }: StatsTableProps) {
  // Sort state
  const [sortField, setSortField] = useState<SortField>('hit_rate_percentage');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  // Filter state
  const [statTypeFilter, setStatTypeFilter] = useState<string>('');
  const [minPicksFilter, setMinPicksFilter] = useState<number>(0);
  const [searchFilter, setSearchFilter] = useState<string>('');

  // Handle sort click
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // Sort icon
  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <span className="text-gray-600 ml-1">↕</span>;
    return <span className="text-blue-400 ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>;
  };

  // Filter and sort data
  const filteredData = useMemo(() => {
    let result = [...data];

    // Apply filters
    if (statTypeFilter) {
      result = result.filter((r) => r.stat_type === statTypeFilter);
    }
    if (minPicksFilter > 0) {
      result = result.filter((r) => r.total_picks >= minPicksFilter);
    }
    if (searchFilter) {
      const search = searchFilter.toLowerCase();
      result = result.filter((r) => r.player_name.toLowerCase().includes(search));
    }

    // Sort
    result.sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];

      // Handle string comparison
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }

      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [data, sortField, sortDirection, statTypeFilter, minPicksFilter, searchFilter]);

  // Export to CSV
  const exportToCsv = () => {
    const headers = ['Player', 'Stat Type', 'Total Picks', 'Hits', 'Misses', 'Hit Rate %', 'Avg EV'];
    const rows = filteredData.map((r) => [
      r.player_name,
      r.stat_type,
      r.total_picks,
      r.hits,
      r.misses,
      r.hit_rate_percentage.toFixed(2),
      r.avg_ev.toFixed(2),
    ]);

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `stats_${new Date().toISOString().split('T')[0]}.csv`);
    link.click();
  };

  // Format helpers
  const formatPercent = (value: number) => `${value.toFixed(1)}%`;
  const getHitRateColor = (rate: number) => {
    if (rate >= 60) return 'text-green-400';
    if (rate >= 50) return 'text-yellow-400';
    return 'text-red-400';
  };
  const getEvColor = (ev: number) => {
    if (ev >= 5) return 'text-green-400';
    if (ev >= 0) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex flex-wrap gap-4 items-end">
          {/* Search */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm text-gray-400 mb-1">Search Player</label>
            <input
              type="text"
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              placeholder="Player name..."
              className="w-full bg-gray-700 text-white rounded px-3 py-2 border border-gray-600 
                       hover:border-gray-500 focus:border-blue-500 focus:outline-none"
            />
          </div>

          {/* Stat Type */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Stat Type</label>
            <select
              value={statTypeFilter}
              onChange={(e) => setStatTypeFilter(e.target.value)}
              className="bg-gray-700 text-white rounded px-3 py-2 border border-gray-600 
                       hover:border-gray-500 focus:border-blue-500 focus:outline-none min-w-[140px]"
            >
              {STAT_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Min Picks */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Min Picks</label>
            <input
              type="number"
              value={minPicksFilter}
              onChange={(e) => setMinPicksFilter(parseInt(e.target.value) || 0)}
              min={0}
              className="w-24 bg-gray-700 text-white rounded px-3 py-2 border border-gray-600 
                       hover:border-gray-500 focus:border-blue-500 focus:outline-none"
            />
          </div>

          {/* Export Button */}
          <button
            onClick={exportToCsv}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded 
                     transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export CSV
          </button>

          {/* Results count */}
          <div className="text-sm text-gray-400">
            <span className="text-white font-medium">{filteredData.length}</span> of{' '}
            <span className="text-white font-medium">{data.length}</span> records
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        </div>
      )}

      {/* Table */}
      {!isLoading && filteredData.length > 0 && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-900 text-gray-400 text-xs uppercase">
                <tr>
                  <th
                    className="px-4 py-3 text-left cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort('player_name')}
                  >
                    Player <SortIcon field="player_name" />
                  </th>
                  <th
                    className="px-4 py-3 text-left cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort('stat_type')}
                  >
                    Stat <SortIcon field="stat_type" />
                  </th>
                  <th
                    className="px-4 py-3 text-right cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort('total_picks')}
                  >
                    Picks <SortIcon field="total_picks" />
                  </th>
                  <th
                    className="px-4 py-3 text-right cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort('hits')}
                  >
                    Hits <SortIcon field="hits" />
                  </th>
                  <th
                    className="px-4 py-3 text-right cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort('hit_rate_percentage')}
                  >
                    Hit Rate <SortIcon field="hit_rate_percentage" />
                  </th>
                  <th
                    className="px-4 py-3 text-right cursor-pointer hover:text-white transition-colors"
                    onClick={() => handleSort('avg_ev')}
                  >
                    Avg EV <SortIcon field="avg_ev" />
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {filteredData.map((record) => (
                  <tr
                    key={`${record.player_name}-${record.stat_type}`}
                    className="hover:bg-gray-700/50 transition-colors"
                  >
                    <td className="px-4 py-3 text-white font-medium">{record.player_name}</td>
                    <td className="px-4 py-3">
                      <span className="bg-blue-900/50 text-blue-400 text-xs px-2 py-0.5 rounded">
                        {record.stat_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right text-gray-300">{record.total_picks}</td>
                    <td className="px-4 py-3 text-right">
                      <span className="text-green-400">{record.hits}</span>
                      <span className="text-gray-500">/</span>
                      <span className="text-red-400">{record.misses}</span>
                    </td>
                    <td className={`px-4 py-3 text-right font-medium ${getHitRateColor(record.hit_rate_percentage)}`}>
                      {formatPercent(record.hit_rate_percentage)}
                    </td>
                    <td className={`px-4 py-3 text-right font-medium ${getEvColor(record.avg_ev)}`}>
                      {record.avg_ev.toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && filteredData.length === 0 && (
        <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
          <p className="text-gray-400">No stats data found</p>
          <p className="text-sm text-gray-500 mt-2">Try adjusting your filters</p>
        </div>
      )}
    </div>
  );
}

export default StatsTable;
