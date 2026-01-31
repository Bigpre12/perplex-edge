import { useAltLines, AltLine } from '../api/public';

interface AltLineExplorerProps {
  pickId: number;
  onClose: () => void;
}

// Format odds
function formatOdds(odds: number | null): string {
  if (odds === null) return '-';
  return odds > 0 ? `+${odds}` : odds.toString();
}

// Format percentage
function formatPercent(value: number | null): string {
  if (value === null) return '-';
  return `${(value * 100).toFixed(1)}%`;
}

// EV badge color
function getEvColor(ev: number | null): string {
  if (ev === null) return 'text-gray-500';
  if (ev > 0.05) return 'text-green-400';
  if (ev > 0) return 'text-green-500';
  if (ev > -0.03) return 'text-yellow-400';
  return 'text-red-400';
}

// Line row component
function LineRow({ line, isSelected }: { line: AltLine; isSelected: boolean }) {
  return (
    <tr className={`border-b border-gray-700 ${line.is_main_line ? 'bg-blue-900/20' : ''} ${isSelected ? 'ring-2 ring-green-500' : ''}`}>
      {/* Line */}
      <td className="px-3 py-2 text-center">
        <span className={`font-medium ${line.is_main_line ? 'text-blue-400' : 'text-white'}`}>
          {line.line}
        </span>
        {line.is_main_line && (
          <span className="ml-1 text-xs text-blue-400">(main)</span>
        )}
      </td>
      
      {/* Over */}
      <td className="px-3 py-2 text-center">
        <div className="text-white">{formatOdds(line.over_odds)}</div>
        <div className="text-xs text-gray-500">{formatPercent(line.over_prob)}</div>
      </td>
      
      {/* Over EV */}
      <td className={`px-3 py-2 text-center font-medium ${getEvColor(line.over_ev)}`}>
        {line.over_ev !== null ? (line.over_ev > 0 ? '+' : '') + formatPercent(line.over_ev) : '-'}
      </td>
      
      {/* Under */}
      <td className="px-3 py-2 text-center">
        <div className="text-white">{formatOdds(line.under_odds)}</div>
        <div className="text-xs text-gray-500">{formatPercent(line.under_prob)}</div>
      </td>
      
      {/* Under EV */}
      <td className={`px-3 py-2 text-center font-medium ${getEvColor(line.under_ev)}`}>
        {line.under_ev !== null ? (line.under_ev > 0 ? '+' : '') + formatPercent(line.under_ev) : '-'}
      </td>
      
      {/* Fair Odds */}
      <td className="px-3 py-2 text-center text-gray-400 text-sm">
        <div>{formatOdds(line.over_fair_odds)}</div>
        <div>{formatOdds(line.under_fair_odds)}</div>
      </td>
    </tr>
  );
}

// Best line recommendation card
function BestLineCard({ title, line, side }: { title: string; line: AltLine | null; side: 'over' | 'under' }) {
  if (!line) return null;
  
  const ev = side === 'over' ? line.over_ev : line.under_ev;
  const odds = side === 'over' ? line.over_odds : line.under_odds;
  const prob = side === 'over' ? line.over_prob : line.under_prob;
  
  if (!ev || ev <= 0) return null;
  
  return (
    <div className={`p-3 rounded-lg border ${side === 'over' ? 'border-green-700 bg-green-900/20' : 'border-red-700 bg-red-900/20'}`}>
      <div className="text-xs text-gray-400 mb-1">{title}</div>
      <div className="flex items-center justify-between">
        <div>
          <span className={`font-bold ${side === 'over' ? 'text-green-400' : 'text-red-400'}`}>
            {side.toUpperCase()} {line.line}
          </span>
          <span className="ml-2 text-white">{formatOdds(odds)}</span>
        </div>
        <div className="text-right">
          <div className="text-green-400 font-medium">+{formatPercent(ev)} EV</div>
          <div className="text-xs text-gray-500">{formatPercent(prob)} prob</div>
        </div>
      </div>
    </div>
  );
}

export function AltLineExplorer({ pickId, onClose }: AltLineExplorerProps) {
  const { data, isLoading, error } = useAltLines(pickId);
  
  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-gray-800 rounded-lg p-8">
          <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto" />
          <div className="text-gray-400 mt-4">Loading alt lines...</div>
        </div>
      </div>
    );
  }
  
  if (error || !data) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-gray-800 rounded-lg p-8 max-w-md">
          <div className="text-red-400 mb-4">Error loading alt lines</div>
          <div className="text-gray-500 text-sm">{error?.message}</div>
          <button
            onClick={onClose}
            className="mt-4 px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600"
          >
            Close
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-white">
              {data.player_name} - {data.stat_type.replace('player_', '').replace(/_/g, ' ').toUpperCase()}
            </h3>
            <div className="text-sm text-gray-400">
              {data.team_abbr} vs {data.opponent_abbr}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            &times;
          </button>
        </div>
        
        {/* Model info */}
        <div className="p-4 bg-gray-700/30 border-b border-gray-700">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-400">{data.model_projection}</div>
              <div className="text-xs text-gray-500">Model Projection</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">{data.season_avg ?? '-'}</div>
              <div className="text-xs text-gray-500">Season Avg</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">
                {data.hit_rate_5g !== null ? `${(data.hit_rate_5g * 100).toFixed(0)}%` : '-'}
              </div>
              <div className="text-xs text-gray-500">L5 Hit Rate</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-400">±{data.projection_std ?? '-'}</div>
              <div className="text-xs text-gray-500">Std Dev</div>
            </div>
          </div>
        </div>
        
        {/* Best lines */}
        <div className="p-4 grid grid-cols-2 gap-4">
          <BestLineCard title="Best Over" line={data.best_over_line} side="over" />
          <BestLineCard title="Best Under" line={data.best_under_line} side="under" />
        </div>
        
        {/* Lines table */}
        <div className="flex-1 overflow-auto p-4">
          <table className="w-full text-sm">
            <thead className="bg-gray-700/50 text-gray-400 text-xs uppercase sticky top-0">
              <tr>
                <th className="px-3 py-2">Line</th>
                <th className="px-3 py-2">Over Odds</th>
                <th className="px-3 py-2">Over EV</th>
                <th className="px-3 py-2">Under Odds</th>
                <th className="px-3 py-2">Under EV</th>
                <th className="px-3 py-2">Fair</th>
              </tr>
            </thead>
            <tbody>
              {data.alt_lines.map((line, idx) => (
                <LineRow
                  key={idx}
                  line={line}
                  isSelected={
                    (data.best_over_line?.line === line.line) ||
                    (data.best_under_line?.line === line.line)
                  }
                />
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Footer */}
        <div className="p-4 border-t border-gray-700 bg-gray-800">
          <div className="text-xs text-gray-500">
            <strong>Tip:</strong> Look for lines where market odds are worse than fair odds (positive EV).
            Green lines indicate good value, yellow is marginal, red is negative EV.
          </div>
        </div>
      </div>
    </div>
  );
}

export default AltLineExplorer;
