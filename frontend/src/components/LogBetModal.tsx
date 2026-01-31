import { useState } from 'react';
import { useSportContext } from '../context/SportContext';
import { useSports } from '../api/public';
import {
  useCreateBet,
  useSportsbooks,
  BetCreate,
  DEFAULT_SPORTSBOOKS,
  DEFAULT_MARKET_TYPES,
} from '../api/bets';

interface LogBetModalProps {
  onClose: () => void;
  onSuccess: () => void;
  prefill?: Partial<BetCreate>;
}

export function LogBetModal({ onClose, onSuccess, prefill }: LogBetModalProps) {
  const { sportId } = useSportContext();
  const { data: sportsData } = useSports();
  const { data: sportsbooksData } = useSportsbooks();
  const createBetMutation = useCreateBet();
  
  // Form state
  const [selectedSportId, setSelectedSportId] = useState(prefill?.sport_id || sportId || 0);
  const [marketType, setMarketType] = useState(prefill?.market_type || 'player_points');
  const [side, setSide] = useState(prefill?.side || 'over');
  const [lineValue, setLineValue] = useState(prefill?.line_value?.toString() || '');
  const [sportsbook, setSportsbook] = useState(prefill?.sportsbook || 'FanDuel');
  const [odds, setOdds] = useState(prefill?.opening_odds?.toString() || '-110');
  const [stake, setStake] = useState(prefill?.stake?.toString() || '1');
  const [notes, setNotes] = useState(prefill?.notes || '');
  const [playerName, setPlayerName] = useState('');
  
  // Error state
  const [error, setError] = useState('');
  
  const sportsbooks = sportsbooksData?.sportsbooks || DEFAULT_SPORTSBOOKS;
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Validate
    if (!selectedSportId) {
      setError('Please select a sport');
      return;
    }
    if (!marketType) {
      setError('Please select a market type');
      return;
    }
    if (!odds || isNaN(parseInt(odds))) {
      setError('Please enter valid odds');
      return;
    }
    
    const betData: BetCreate = {
      sport_id: selectedSportId,
      market_type: marketType,
      side,
      line_value: lineValue ? parseFloat(lineValue) : undefined,
      sportsbook,
      opening_odds: parseInt(odds),
      stake: parseFloat(stake) || 1,
      notes: notes || undefined,
    };
    
    try {
      await createBetMutation.mutateAsync(betData);
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log bet');
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-white">Log New Bet</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            &times;
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Sport */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Sport *</label>
            <select
              value={selectedSportId}
              onChange={e => setSelectedSportId(parseInt(e.target.value))}
              className="w-full bg-gray-700 text-white rounded px-3 py-2"
              required
            >
              <option value="">Select sport...</option>
              {sportsData?.items.map(sport => (
                <option key={sport.id} value={sport.id}>
                  {sport.name}
                </option>
              ))}
            </select>
          </div>
          
          {/* Market Type */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Market Type *</label>
            <select
              value={marketType}
              onChange={e => setMarketType(e.target.value)}
              className="w-full bg-gray-700 text-white rounded px-3 py-2"
              required
            >
              {DEFAULT_MARKET_TYPES.map(mt => (
                <option key={mt.value} value={mt.value}>
                  {mt.label}
                </option>
              ))}
            </select>
          </div>
          
          {/* Player Name (for props) */}
          {marketType.startsWith('player_') && (
            <div>
              <label className="block text-sm text-gray-400 mb-1">Player Name</label>
              <input
                type="text"
                value={playerName}
                onChange={e => setPlayerName(e.target.value)}
                placeholder="e.g., LeBron James"
                className="w-full bg-gray-700 text-white rounded px-3 py-2"
              />
              <p className="text-xs text-gray-500 mt-1">
                Optional - for tracking performance by player
              </p>
            </div>
          )}
          
          {/* Side and Line */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Side *</label>
              <div className="flex gap-2">
                {marketType.startsWith('player_') || marketType === 'total' ? (
                  <>
                    <button
                      type="button"
                      onClick={() => setSide('over')}
                      className={`flex-1 py-2 rounded font-medium transition-colors ${
                        side === 'over'
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      Over
                    </button>
                    <button
                      type="button"
                      onClick={() => setSide('under')}
                      className={`flex-1 py-2 rounded font-medium transition-colors ${
                        side === 'under'
                          ? 'bg-red-600 text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      Under
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={() => setSide('home')}
                      className={`flex-1 py-2 rounded font-medium transition-colors ${
                        side === 'home'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      Home
                    </button>
                    <button
                      type="button"
                      onClick={() => setSide('away')}
                      className={`flex-1 py-2 rounded font-medium transition-colors ${
                        side === 'away'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      Away
                    </button>
                  </>
                )}
              </div>
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">Line</label>
              <input
                type="number"
                step="0.5"
                value={lineValue}
                onChange={e => setLineValue(e.target.value)}
                placeholder="e.g., 24.5"
                className="w-full bg-gray-700 text-white rounded px-3 py-2"
              />
            </div>
          </div>
          
          {/* Sportsbook */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Sportsbook *</label>
            <select
              value={sportsbook}
              onChange={e => setSportsbook(e.target.value)}
              className="w-full bg-gray-700 text-white rounded px-3 py-2"
              required
            >
              {sportsbooks.map(sb => (
                <option key={sb} value={sb}>
                  {sb}
                </option>
              ))}
            </select>
          </div>
          
          {/* Odds and Stake */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Odds *</label>
              <input
                type="number"
                value={odds}
                onChange={e => setOdds(e.target.value)}
                placeholder="-110"
                className="w-full bg-gray-700 text-white rounded px-3 py-2"
                required
              />
              <p className="text-xs text-gray-500 mt-1">American odds</p>
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">Stake (units)</label>
              <input
                type="number"
                step="0.5"
                value={stake}
                onChange={e => setStake(e.target.value)}
                placeholder="1"
                className="w-full bg-gray-700 text-white rounded px-3 py-2"
              />
              <p className="text-xs text-gray-500 mt-1">Default: 1 unit</p>
            </div>
          </div>
          
          {/* Notes */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Notes</label>
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder="Optional notes about this bet..."
              rows={2}
              className="w-full bg-gray-700 text-white rounded px-3 py-2 resize-none"
            />
          </div>
          
          {/* Error */}
          {error && (
            <div className="p-3 bg-red-900/30 border border-red-800 rounded text-red-400 text-sm">
              {error}
            </div>
          )}
          
          {/* Submit */}
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createBetMutation.isPending}
              className="flex-1 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded font-medium disabled:opacity-50"
            >
              {createBetMutation.isPending ? 'Logging...' : 'Log Bet'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default LogBetModal;
