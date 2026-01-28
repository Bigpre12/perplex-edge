import { useEffect, useState } from 'react';
import { api, GameList, LineComparison } from '../api/client';

interface Player {
  id: number;
  name: string;
  position?: string;
}

export function PropsAnalyzer() {
  const [games, setGames] = useState<GameList | null>(null);
  const [selectedGame, setSelectedGame] = useState<number | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(null);
  const [props, setProps] = useState<LineComparison[]>([]);
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
    async function fetchPlayers() {
      if (!selectedGame) return;
      try {
        const data = await api.getPlayersWithProps(selectedGame);
        setPlayers(data);
        if (data.length > 0) {
          setSelectedPlayer(data[0].id);
        } else {
          setSelectedPlayer(null);
        }
      } catch (err) {
        console.error('Failed to fetch players:', err);
        setPlayers([]);
      }
    }
    fetchPlayers();
  }, [selectedGame]);

  useEffect(() => {
    async function fetchProps() {
      if (!selectedGame || !selectedPlayer) return;
      try {
        const data = await api.comparePlayerProps(selectedGame, selectedPlayer);
        setProps(data);
      } catch (err) {
        console.error('Failed to fetch props:', err);
        setProps([]);
      }
    }
    fetchProps();
  }, [selectedGame, selectedPlayer]);

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
          <label className="block text-sm text-gray-400 mb-1">Player</label>
          <select
            value={selectedPlayer ?? ''}
            onChange={(e) => setSelectedPlayer(Number(e.target.value))}
            className="bg-gray-700 text-white rounded px-3 py-2 min-w-[200px]"
            disabled={players.length === 0}
          >
            {players.length === 0 ? (
              <option>No players with props</option>
            ) : (
              players.map((player) => (
                <option key={player.id} value={player.id}>
                  {player.name} {player.position ? `(${player.position})` : ''}
                </option>
              ))
            )}
          </select>
        </div>
      </div>

      {/* Props Comparison */}
      {props.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {props.map((prop, idx) => (
            <div key={idx} className="bg-gray-800 rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="text-white font-medium">{prop.stat_type}</h4>
                  <p className="text-sm text-gray-400 capitalize">{prop.side}</p>
                </div>
                <div className="text-right">
                  <p className="text-gray-400 text-sm">Line</p>
                  <p className="text-xl font-bold text-white">
                    {prop.consensus_line ?? '-'}
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                {prop.lines.map((line, i) => (
                  <div
                    key={i}
                    className={`flex justify-between items-center p-2 rounded ${
                      line.sportsbook === prop.best_sportsbook
                        ? 'bg-green-900/30 border border-green-700'
                        : 'bg-gray-700/50'
                    }`}
                  >
                    <span className="text-gray-300 text-sm">{line.sportsbook}</span>
                    <div className="text-right">
                      {line.line_value !== undefined && (
                        <span className="text-gray-400 text-sm mr-2">{line.line_value}</span>
                      )}
                      <span
                        className={`font-medium ${
                          line.odds > 0 ? 'text-green-400' : 'text-white'
                        }`}
                      >
                        {line.odds > 0 ? `+${line.odds}` : line.odds}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-3 pt-3 border-t border-gray-700 flex justify-between items-center">
                <span className="text-sm text-gray-400">Best odds:</span>
                <span className="text-green-400 font-bold">
                  {prop.best_odds > 0 ? `+${prop.best_odds}` : prop.best_odds} @{' '}
                  {prop.best_sportsbook}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg p-8 text-center">
          <p className="text-gray-400">No props available</p>
          <p className="text-sm text-gray-500 mt-2">
            {players.length === 0
              ? 'No players have props for this game'
              : 'Select a player to view their props'}
          </p>
        </div>
      )}
    </div>
  );
}
