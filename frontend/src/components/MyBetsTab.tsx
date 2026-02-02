import { useState, useMemo } from 'react';
import { useSportContext } from '../context/SportContext';
import {
  useBets,
  useBetStats,
  useSettleBet,
  useDeleteBet,
  BetResponse,
  BetFilters,
  BetStatus,
  ROIByCategory,
} from '../api/bets';
import { LogBetModal } from './LogBetModal';

// =============================================================================
// Daily Risk Dashboard
// Shows today's betting activity, risk, and EV tracking
// =============================================================================

function DailyRiskDashboard({ bets }: { bets: BetResponse[] }) {
  // Get today's date at midnight for comparison
  const today = useMemo(() => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    return d;
  }, []);
  
  // Filter to today's bets
  const todaysBets = useMemo(() => {
    return bets.filter(bet => {
      const betDate = new Date(bet.created_at);
      betDate.setHours(0, 0, 0, 0);
      return betDate.getTime() === today.getTime();
    });
  }, [bets, today]);
  
  // Calculate stats
  const stats = useMemo(() => {
    if (todaysBets.length === 0) return null;
    
    const totalStaked = todaysBets.reduce((sum, b) => sum + b.stake, 0);
    const totalEv = todaysBets.reduce((sum, b) => {
      // Approximate EV from model_pick if available, otherwise estimate
      return sum + (b.stake * 0.03); // Assume 3% avg EV if not tracked
    }, 0);
    
    const settled = todaysBets.filter(b => b.status !== 'pending');
    const pending = todaysBets.filter(b => b.status === 'pending');
    
    const actualPnl = settled.reduce((sum, b) => sum + (b.profit_loss || 0), 0);
    const expectedPnl = totalEv;
    
    const won = todaysBets.filter(b => b.status === 'won').length;
    const lost = todaysBets.filter(b => b.status === 'lost').length;
    
    return {
      totalBets: todaysBets.length,
      totalStaked,
      totalEv,
      pending: pending.length,
      settled: settled.length,
      actualPnl,
      expectedPnl,
      won,
      lost,
      runningBehind: actualPnl < expectedPnl - 1, // More than 1 unit below expected
    };
  }, [todaysBets]);
  
  if (!stats || stats.totalBets === 0) {
    return (
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 border border-gray-700 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-white">📊 Today's Session</h3>
            <p className="text-sm text-gray-400">No bets logged today yet</p>
          </div>
          <div className="text-4xl opacity-30">📅</div>
        </div>
      </div>
    );
  }
  
  return (
    <div className={`rounded-lg p-4 mb-4 border ${
      stats.runningBehind 
        ? 'bg-gradient-to-r from-orange-900/20 to-red-900/20 border-orange-700/50' 
        : 'bg-gradient-to-r from-green-900/20 to-blue-900/20 border-green-700/50'
    }`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-bold text-white">📊 Today's Session</h3>
        {stats.runningBehind && (
          <span className="px-2 py-1 bg-orange-900/50 text-orange-400 text-xs rounded-full">
            ⚠️ Running below EV
          </span>
        )}
      </div>
      
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <div>
          <div className="text-2xl font-bold text-white">{stats.totalBets}</div>
          <div className="text-xs text-gray-400">Bets Today</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-yellow-400">{stats.totalStaked.toFixed(1)}u</div>
          <div className="text-xs text-gray-400">Total Staked</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-blue-400">+{stats.totalEv.toFixed(2)}u</div>
          <div className="text-xs text-gray-400">Expected EV</div>
        </div>
        <div>
          <div className={`text-2xl font-bold ${stats.actualPnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {stats.actualPnl >= 0 ? '+' : ''}{stats.actualPnl.toFixed(2)}u
          </div>
          <div className="text-xs text-gray-400">Actual P/L</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-white">
            {stats.won}W-{stats.lost}L
          </div>
          <div className="text-xs text-gray-400">{stats.pending} pending</div>
        </div>
      </div>
      
      {/* Variance indicator */}
      <div className="mt-3 pt-3 border-t border-gray-700/50">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">EV vs Actual:</span>
          <span className={stats.actualPnl >= stats.expectedPnl ? 'text-green-400' : 'text-orange-400'}>
            {(stats.actualPnl - stats.expectedPnl) >= 0 ? '+' : ''}
            {(stats.actualPnl - stats.expectedPnl).toFixed(2)}u variance
          </span>
        </div>
        {stats.runningBehind && (
          <p className="text-xs text-orange-400/80 mt-1">
            💡 You're below expected. This is normal variance - stick to your process.
          </p>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Helper Components
// =============================================================================

// Status badge with colors
function StatusBadge({ status }: { status: BetStatus }) {
  const colors: Record<BetStatus, string> = {
    pending: 'bg-yellow-900/50 text-yellow-400 border-yellow-700',
    won: 'bg-green-900/50 text-green-400 border-green-700',
    lost: 'bg-red-900/50 text-red-400 border-red-700',
    push: 'bg-gray-700 text-gray-300 border-gray-600',
    void: 'bg-gray-800 text-gray-500 border-gray-700',
  };
  
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium border ${colors[status]}`}>
      {status.toUpperCase()}
    </span>
  );
}

// P/L display with color
function ProfitLoss({ value }: { value: number | null }) {
  if (value === null) return <span className="text-gray-500">-</span>;
  
  const isPositive = value > 0;
  const isZero = value === 0;
  
  return (
    <span className={`font-medium ${
      isPositive ? 'text-green-400' : isZero ? 'text-gray-400' : 'text-red-400'
    }`}>
      {isPositive ? '+' : ''}{value.toFixed(2)}u
    </span>
  );
}

// CLV badge
function CLVBadge({ clv }: { clv: number | null }) {
  if (clv === null) return <span className="text-gray-500">-</span>;
  
  const isPositive = clv > 0;
  
  return (
    <span className={`text-xs ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
      {isPositive ? '+' : ''}{clv.toFixed(1)}¢
    </span>
  );
}

// ROI category row
function ROIRow({ item }: { item: ROIByCategory }) {
  return (
    <div className="flex items-center justify-between py-2 px-3 bg-gray-800/30 rounded">
      <div>
        <div className="text-white font-medium">{item.category}</div>
        <div className="text-xs text-gray-500">
          {item.won}W-{item.lost}L ({item.total_bets} bets)
        </div>
      </div>
      <div className="text-right">
        <div className={`font-medium ${item.roi >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {item.roi >= 0 ? '+' : ''}{item.roi.toFixed(1)}% ROI
        </div>
        <div className="text-xs text-gray-500">
          {item.total_profit_loss >= 0 ? '+' : ''}{item.total_profit_loss.toFixed(2)}u
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Stats Card
// =============================================================================

function StatsCard() {
  const { sportId } = useSportContext();
  const { data: stats, isLoading, error } = useBetStats(sportId || undefined);
  
  if (isLoading) {
    return (
      <div className="bg-gray-800/50 rounded-lg p-6">
        <div className="animate-pulse space-y-3">
          <div className="h-6 bg-gray-700 rounded w-1/3" />
          <div className="h-4 bg-gray-700 rounded w-1/2" />
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-gray-800/50 rounded-lg p-6 text-center text-red-400">
        Error loading stats: {error.message}
      </div>
    );
  }
  
  if (!stats) {
    return (
      <div className="bg-gray-800/50 rounded-lg p-6 text-center text-gray-400">
        No betting stats available yet. Log your first bet to see stats!
      </div>
    );
  }
  
  return (
    <div className="bg-gray-800/50 rounded-lg p-6 space-y-6">
      {/* Overall Stats */}
      <div>
        <h3 className="text-lg font-bold text-white mb-4">Overall Performance</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="text-center">
            <div className={`text-2xl font-bold ${stats.overall_roi >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {stats.overall_roi >= 0 ? '+' : ''}{stats.overall_roi.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500">ROI</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white">
              {(stats.overall_win_rate * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500">Win Rate</div>
          </div>
          <div className="text-center">
            <div className={`text-2xl font-bold ${stats.total_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {stats.total_profit_loss >= 0 ? '+' : ''}{stats.total_profit_loss.toFixed(1)}u
            </div>
            <div className="text-xs text-gray-500">P/L</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{stats.total_bets}</div>
            <div className="text-xs text-gray-500">Total Bets</div>
          </div>
        </div>
        
        {/* Record */}
        <div className="mt-4 flex justify-center gap-4 text-sm">
          <span className="text-green-400">{stats.won}W</span>
          <span className="text-red-400">{stats.lost}L</span>
          <span className="text-gray-400">{stats.pushed}P</span>
          <span className="text-yellow-400">{stats.pending_bets} pending</span>
        </div>
      </div>
      
      {/* CLV Stats */}
      {stats.clv_stats.total_bets_with_clv > 0 && (
        <div className="border-t border-gray-700 pt-4">
          <h4 className="text-sm font-medium text-gray-400 mb-2">Closing Line Value (CLV)</h4>
          <div className="flex items-center gap-6 text-sm">
            <div>
              <span className="text-gray-400">Avg: </span>
              <span className={stats.clv_stats.avg_clv_cents >= 0 ? 'text-green-400' : 'text-red-400'}>
                {stats.clv_stats.avg_clv_cents >= 0 ? '+' : ''}{stats.clv_stats.avg_clv_cents.toFixed(1)}¢
              </span>
            </div>
            <div>
              <span className="text-gray-400">Beat close: </span>
              <span className="text-white">
                {(stats.clv_stats.positive_clv_pct * 100).toFixed(0)}%
              </span>
            </div>
            <div>
              <span className="text-gray-400">Total: </span>
              <span className={stats.clv_stats.total_clv_cents >= 0 ? 'text-green-400' : 'text-red-400'}>
                {stats.clv_stats.total_clv_cents >= 0 ? '+' : ''}{stats.clv_stats.total_clv_cents.toFixed(0)}¢
              </span>
            </div>
          </div>
        </div>
      )}
      
      {/* ROI by Market */}
      {stats.by_market.length > 0 && (
        <div className="border-t border-gray-700 pt-4">
          <h4 className="text-sm font-medium text-gray-400 mb-2">By Market Type</h4>
          <div className="space-y-2">
            {stats.by_market.slice(0, 5).map(item => (
              <ROIRow key={item.category} item={item} />
            ))}
          </div>
        </div>
      )}
      
      {/* ROI by Sportsbook */}
      {stats.by_sportsbook.length > 0 && (
        <div className="border-t border-gray-700 pt-4">
          <h4 className="text-sm font-medium text-gray-400 mb-2">By Sportsbook</h4>
          <div className="space-y-2">
            {stats.by_sportsbook.map(item => (
              <ROIRow key={item.category} item={item} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Bets Table
// =============================================================================

function BetsTable({ bets, onSettle, onDelete }: {
  bets: BetResponse[];
  onSettle: (bet: BetResponse) => void;
  onDelete: (betId: number) => void;
}) {
  const formatOdds = (odds: number) => (odds > 0 ? `+${odds}` : odds.toString());
  
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };
  
  if (bets.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        No bets found. Log your first bet to start tracking!
      </div>
    );
  }
  
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-800/50 text-gray-400 text-xs uppercase">
          <tr>
            <th className="px-3 py-3 text-left">Date</th>
            <th className="px-3 py-3 text-left">Bet</th>
            <th className="px-3 py-3 text-left">Book</th>
            <th className="px-3 py-3 text-right">Odds</th>
            <th className="px-3 py-3 text-right">Stake</th>
            <th className="px-3 py-3 text-center">Status</th>
            <th className="px-3 py-3 text-right">P/L</th>
            <th className="px-3 py-3 text-right">CLV</th>
            <th className="px-3 py-3 text-center">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-700">
          {bets.map(bet => (
            <tr key={bet.id} className="hover:bg-gray-700/50 transition-colors">
              {/* Date */}
              <td className="px-3 py-3 text-gray-400">
                {formatDate(bet.placed_at)}
              </td>
              
              {/* Bet details */}
              <td className="px-3 py-3">
                <div className="text-white font-medium">
                  {bet.player_name || bet.market_type}
                </div>
                <div className="text-xs text-gray-500">
                  {bet.side.toUpperCase()} {bet.line_value ?? ''}
                </div>
              </td>
              
              {/* Sportsbook */}
              <td className="px-3 py-3 text-gray-300">
                {bet.sportsbook}
              </td>
              
              {/* Odds */}
              <td className="px-3 py-3 text-right text-white">
                {formatOdds(bet.opening_odds)}
              </td>
              
              {/* Stake */}
              <td className="px-3 py-3 text-right text-gray-300">
                {bet.stake}u
              </td>
              
              {/* Status */}
              <td className="px-3 py-3 text-center">
                <StatusBadge status={bet.status} />
              </td>
              
              {/* P/L */}
              <td className="px-3 py-3 text-right">
                <ProfitLoss value={bet.profit_loss} />
              </td>
              
              {/* CLV */}
              <td className="px-3 py-3 text-right">
                <CLVBadge clv={bet.clv_cents} />
              </td>
              
              {/* Actions */}
              <td className="px-3 py-3 text-center">
                <div className="flex items-center justify-center gap-2">
                  {bet.status === 'pending' && (
                    <button
                      onClick={() => onSettle(bet)}
                      className="text-blue-400 hover:text-blue-300 text-xs"
                    >
                      Settle
                    </button>
                  )}
                  <button
                    onClick={() => onDelete(bet.id)}
                    className="text-red-400 hover:text-red-300 text-xs"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// =============================================================================
// Settle Modal
// =============================================================================

function SettleModal({ bet, onClose, onSettle }: {
  bet: BetResponse;
  onClose: () => void;
  onSettle: (status: BetStatus, actualValue?: number, closingOdds?: number) => void;
}) {
  const [status, setStatus] = useState<BetStatus>('won');
  const [actualValue, setActualValue] = useState('');
  const [closingOdds, setClosingOdds] = useState('');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSettle(
      status,
      actualValue ? parseFloat(actualValue) : undefined,
      closingOdds ? parseInt(closingOdds) : undefined,
    );
  };
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-bold text-white mb-4">Settle Bet</h3>
        
        <div className="mb-4 p-3 bg-gray-700/50 rounded">
          <div className="text-white font-medium">{bet.player_name || bet.market_type}</div>
          <div className="text-sm text-gray-400">
            {bet.side.toUpperCase()} {bet.line_value} @ {bet.opening_odds > 0 ? '+' : ''}{bet.opening_odds}
          </div>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Status */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Result</label>
            <div className="flex gap-2">
              {(['won', 'lost', 'push', 'void'] as BetStatus[]).map(s => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setStatus(s)}
                  className={`flex-1 py-2 rounded text-sm font-medium transition-colors ${
                    status === s
                      ? s === 'won' ? 'bg-green-600 text-white'
                      : s === 'lost' ? 'bg-red-600 text-white'
                      : 'bg-gray-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {s.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
          
          {/* Actual value (for props) */}
          {bet.player_id && (
            <div>
              <label className="block text-sm text-gray-400 mb-1">Actual Value (optional)</label>
              <input
                type="number"
                step="0.1"
                value={actualValue}
                onChange={e => setActualValue(e.target.value)}
                placeholder="e.g., 28.5"
                className="w-full bg-gray-700 text-white rounded px-3 py-2"
              />
            </div>
          )}
          
          {/* Closing odds */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Closing Odds (optional, for CLV)</label>
            <input
              type="number"
              value={closingOdds}
              onChange={e => setClosingOdds(e.target.value)}
              placeholder="e.g., -115"
              className="w-full bg-gray-700 text-white rounded px-3 py-2"
            />
          </div>
          
          {/* Buttons */}
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
              className="flex-1 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded font-medium"
            >
              Settle Bet
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function MyBetsTab() {
  const { sportId, isLoading: sportLoading } = useSportContext();
  const [showLogModal, setShowLogModal] = useState(false);
  const [settlingBet, setSettlingBet] = useState<BetResponse | null>(null);
  const [statusFilter, setStatusFilter] = useState<BetStatus | ''>('');
  const [page, setPage] = useState(1);
  
  // Build filters
  const filters: BetFilters = {
    sport_id: sportId || undefined,
    status: statusFilter || undefined,
    page,
    page_size: 20,
  };
  
  const { data: betsData, isLoading, error, refetch } = useBets(filters);
  const settleMutation = useSettleBet();
  const deleteMutation = useDeleteBet();
  
  const handleSettle = (status: BetStatus, actualValue?: number, closingOdds?: number) => {
    if (!settlingBet) return;
    
    settleMutation.mutate({
      betId: settlingBet.id,
      data: {
        status,
        actual_value: actualValue,
        closing_odds: closingOdds,
      },
    }, {
      onSuccess: () => {
        setSettlingBet(null);
        refetch();
      },
    });
  };
  
  const handleDelete = (betId: number) => {
    if (confirm('Delete this bet?')) {
      deleteMutation.mutate(betId, {
        onSuccess: () => refetch(),
      });
    }
  };
  
  if (sportLoading || !sportId) {
    return (
      <div className="p-8 text-center text-gray-400">
        Loading sports...
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">My Bets</h2>
          <p className="text-sm text-gray-400">
            Track your bets, ROI, and CLV
          </p>
        </div>
        
        <button
          onClick={() => setShowLogModal(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium"
        >
          + Log Bet
        </button>
      </div>
      
      {/* Daily Risk Dashboard */}
      <DailyRiskDashboard bets={betsData?.items || []} />
      
      {/* Stats Card */}
      <StatsCard />
      
      {/* Filters */}
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-400">Filter:</span>
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value as BetStatus | '')}
          className="bg-gray-700 text-white rounded px-3 py-1.5 text-sm"
        >
          <option value="">All</option>
          <option value="pending">Pending</option>
          <option value="won">Won</option>
          <option value="lost">Lost</option>
          <option value="push">Push</option>
        </select>
      </div>
      
      {/* Bets Table */}
      {isLoading ? (
        <div className="p-8 text-center text-gray-400">
          <div className="animate-spin inline-block w-6 h-6 border-2 border-gray-400 border-t-transparent rounded-full mr-2" />
          Loading bets...
        </div>
      ) : error ? (
        <div className="p-8 text-center text-red-400">
          Error loading bets: {error.message}
        </div>
      ) : (
        <>
          <BetsTable
            bets={betsData?.items || []}
            onSettle={setSettlingBet}
            onDelete={handleDelete}
          />
          
          {/* Pagination */}
          {betsData && betsData.total_pages > 1 && (
            <div className="flex justify-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded disabled:opacity-50"
              >
                Prev
              </button>
              <span className="px-3 py-1 text-gray-400">
                Page {page} of {betsData.total_pages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(betsData.total_pages, p + 1))}
                disabled={page === betsData.total_pages}
                className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
      
      {/* Log Bet Modal */}
      {showLogModal && (
        <LogBetModal
          onClose={() => setShowLogModal(false)}
          onSuccess={() => {
            setShowLogModal(false);
            refetch();
          }}
        />
      )}
      
      {/* Settle Modal */}
      {settlingBet && (
        <SettleModal
          bet={settlingBet}
          onClose={() => setSettlingBet(null)}
          onSettle={handleSettle}
        />
      )}
    </div>
  );
}

export default MyBetsTab;
