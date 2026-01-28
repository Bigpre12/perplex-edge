import { useEffect, useState } from 'react';
import { api, GameList, LineComparison } from '../api/client';

export function LinesTable() {
  const [games, setGames] = useState<GameList | null>(null);
  const [selectedGame, setSelectedGame] = useState<number | null>(null);
  const [lines, setLines] = useState<LineComparison[]>([]);
  const [marketType, setMarketType] = useState<string>('moneyline');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchGames() {
      try {
        const data = await api.getTodaysGames();
        setGames(data);
        if (data.items.length > 0) {
          setSelectedGame(data.items[0].id);
        }
      } catch (err) {
        console.error('Failed to fetch games:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchGames();
  }, []);

  useEffect(() => {
    async function fetchLines() {
      if (!selectedGame) return;
      try {
        const data = await api.compareLines(selectedGame, marketType);
        setLines(data);
      } catch (err) {
        console.error('Failed to fetch lines:', err);
        setLines([]);
      }
    }
    fetchLines();
  }, [selectedGame, marketType]);

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
          <label className="block text-sm text-gray-400 mb-1">Game</label>
          <select
            value={selectedGame ?? ''}
            onChange={(e) => setSelectedGame(Number(e.target.value))}
            className="bg-gray-700 text-white rounded px-3 py-2 min-w-[200px]"
          >
            {games?.items.map((game) => (
              <option key={game.id} value={game.id}>
                {game.away_team.abbreviation || game.away_team.name} @{' '}
                {game.home_team.abbreviation || game.home_team.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Market</label>
          <select
            value={marketType}
            onChange={(e) => setMarketType(e.target.value)}
            className="bg-gray-700 text-white rounded px-3 py-2"
          >
            <option value="moneyline">Moneyline</option>
            <option value="spread">Spread</option>
            <option value="total">Total</option>
          </select>
        </div>
      </div>

      {/* Lines Comparison */}
      {lines.length > 0 ? (
        <div className="bg-gray-800 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-700">
                <th className="text-left px-4 py-3 text-gray-300 font-medium">Side</th>
                <th className="text-left px-4 py-3 text-gray-300 font-medium">Line</th>
                <th className="text-left px-4 py-3 text-gray-300 font-medium">Best Odds</th>
                <th className="text-left px-4 py-3 text-gray-300 font-medium">Best Book</th>
                <th className="text-left px-4 py-3 text-gray-300 font-medium">All Books</th>
              </tr>
            </thead>
            <tbody>
              {lines.map((line, idx) => (
                <tr key={idx} className="border-t border-gray-700 hover:bg-gray-700/50">
                  <td className="px-4 py-3">
                    <span className="text-white font-medium capitalize">{line.side}</span>
                    {line.player_name && (
                      <span className="text-gray-400 text-sm block">{line.player_name}</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-gray-300">
                    {line.consensus_line !== null ? line.consensus_line : '-'}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`font-bold ${
                        line.best_odds > 0 ? 'text-green-400' : 'text-white'
                      }`}
                    >
                      {formatOdds(line.best_odds)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-blue-400 font-medium">
                    {line.best_sportsbook}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      {line.lines.map((bookLine, i) => (
                        <span
                          key={i}
                          className={`text-xs px-2 py-1 rounded ${
                            bookLine.sportsbook === line.best_sportsbook
                              ? 'bg-green-900/50 text-green-400'
                              : 'bg-gray-700 text-gray-300'
                          }`}
                        >
                          {bookLine.sportsbook}: {formatOdds(bookLine.odds)}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg p-8 text-center">
          <p className="text-gray-400">No lines available for this game</p>
          <p className="text-sm text-gray-500 mt-2">
            Try syncing odds data or selecting a different game
          </p>
        </div>
      )}
    </div>
  );
}

function formatOdds(odds: number): string {
  return odds > 0 ? `+${odds}` : String(odds);
}
