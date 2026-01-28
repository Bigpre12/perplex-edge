interface ConfidenceBadgeProps {
  score: number;
  showValue?: boolean;
}

/**
 * Confidence badge component that displays confidence level with color coding.
 * - High (>=0.7): Green
 * - Medium (0.5-0.69): Yellow/Amber
 * - Low (<0.5): Red/Gray
 */
export function ConfidenceBadge({ score, showValue = true }: ConfidenceBadgeProps) {
  const getLevel = () => {
    if (score >= 0.7) return { label: 'High', className: 'bg-green-900/50 text-green-400 border-green-700' };
    if (score >= 0.5) return { label: 'Medium', className: 'bg-yellow-900/50 text-yellow-400 border-yellow-700' };
    return { label: 'Low', className: 'bg-red-900/50 text-red-400 border-red-700' };
  };

  const { label, className } = getLevel();
  const percentage = (score * 100).toFixed(0);

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium border ${className}`}
    >
      {label}
      {showValue && <span className="opacity-75">({percentage}%)</span>}
    </span>
  );
}

/**
 * Compact confidence indicator with just the bar and percentage.
 */
export function ConfidenceBar({ score }: { score: number }) {
  const getColor = () => {
    if (score >= 0.7) return 'bg-green-500';
    if (score >= 0.5) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden min-w-[60px]">
        <div
          className={`h-full rounded-full transition-all ${getColor()}`}
          style={{ width: `${score * 100}%` }}
        />
      </div>
      <span className="text-xs text-gray-300 w-10 text-right">
        {(score * 100).toFixed(0)}%
      </span>
    </div>
  );
}
