/**
 * StateDisplay - Reusable loading, error, and empty state components.
 * 
 * Provides consistent UI patterns across all tabs and pages.
 */

// =============================================================================
// Loading State
// =============================================================================

interface LoadingStateProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function LoadingState({ 
  message = 'Loading...', 
  size = 'md',
  className = ''
}: LoadingStateProps) {
  const sizeClasses = {
    sm: 'h-5 w-5',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };
  
  const heightClasses = {
    sm: 'h-32',
    md: 'h-64',
    lg: 'h-96',
  };

  return (
    <div className={`flex flex-col items-center justify-center ${heightClasses[size]} ${className}`}>
      <div className={`animate-spin ${sizeClasses[size]} border-2 border-blue-500 border-t-transparent rounded-full`} />
      {message && (
        <p className="mt-3 text-sm text-gray-400">{message}</p>
      )}
    </div>
  );
}

// =============================================================================
// Error State
// =============================================================================

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  retryLabel?: string;
  className?: string;
}

export function ErrorState({ 
  title = 'Something went wrong',
  message = 'Failed to load data. Please try again.',
  onRetry,
  retryLabel = 'Try again',
  className = ''
}: ErrorStateProps) {
  return (
    <div className={`bg-red-900/20 border border-red-800 rounded-lg p-4 ${className}`}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-medium text-red-400">{title}</h3>
          <p className="mt-1 text-sm text-red-400/80">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 px-3 py-1.5 text-xs font-medium text-red-400 bg-red-900/30 rounded hover:bg-red-900/50 transition-colors"
            >
              {retryLabel}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Empty State
// =============================================================================

interface EmptyStateProps {
  icon?: 'search' | 'filter' | 'data' | 'chart' | 'calendar' | 'user' | 'clock' | 'custom';
  customIcon?: React.ReactNode;
  title: string;
  message?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

const ICONS = {
  search: (
    <svg className="w-12 h-12 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  ),
  filter: (
    <svg className="w-12 h-12 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
            d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
    </svg>
  ),
  data: (
    <svg className="w-12 h-12 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
            d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
    </svg>
  ),
  chart: (
    <svg className="w-12 h-12 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  ),
  calendar: (
    <svg className="w-12 h-12 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  ),
  user: (
    <svg className="w-12 h-12 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  ),
  clock: (
    <svg className="w-12 h-12 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  custom: null,
};

export function EmptyState({ 
  icon = 'data',
  customIcon,
  title,
  message,
  action,
  secondaryAction,
  className = ''
}: EmptyStateProps) {
  const iconElement = icon === 'custom' ? customIcon : ICONS[icon];
  
  return (
    <div className={`flex flex-col items-center justify-center py-12 px-4 ${className}`}>
      {iconElement && (
        <div className="mb-4">
          {iconElement}
        </div>
      )}
      <h3 className="text-lg font-medium text-gray-300">{title}</h3>
      {message && (
        <p className="mt-1 text-sm text-gray-500 text-center max-w-md">{message}</p>
      )}
      {(action || secondaryAction) && (
        <div className="mt-4 flex items-center gap-3">
          {action && (
            <button
              onClick={action.onClick}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-500 transition-colors"
            >
              {action.label}
            </button>
          )}
          {secondaryAction && (
            <button
              onClick={secondaryAction.onClick}
              className="px-4 py-2 text-sm font-medium text-gray-300 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
            >
              {secondaryAction.label}
            </button>
          )}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Filtered Empty State (when filters hide results)
// =============================================================================

interface FilteredEmptyStateProps {
  totalCount: number;
  filteredCount: number;
  onResetFilters: () => void;
  entityName?: string;
  className?: string;
}

export function FilteredEmptyState({
  totalCount,
  filteredCount,
  onResetFilters,
  entityName = 'items',
  className = ''
}: FilteredEmptyStateProps) {
  if (filteredCount > 0) {
    return null; // Has data, no need to show
  }
  
  if (totalCount === 0) {
    // Truly empty - no data at all
    return (
      <EmptyState
        icon="data"
        title={`No ${entityName} found`}
        message={`There are no ${entityName} available at this time. Check back later.`}
        className={className}
      />
    );
  }
  
  // Has data but filters hide everything
  return (
    <EmptyState
      icon="filter"
      title={`No ${entityName} match your filters`}
      message={`${totalCount.toLocaleString()} ${entityName} available, but your current filters hide them all.`}
      action={{
        label: 'Reset filters',
        onClick: onResetFilters,
      }}
      className={className}
    />
  );
}

// =============================================================================
// Inline States (for smaller contexts)
// =============================================================================

export function InlineLoading({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-gray-400">
      <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full" />
      <span>{message}</span>
    </div>
  );
}

export function InlineError({ message = 'Failed to load' }: { message?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-red-400">
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{message}</span>
    </div>
  );
}

export function InlineEmpty({ message = 'No data' }: { message?: string }) {
  return (
    <div className="text-sm text-gray-500 py-2">{message}</div>
  );
}

// =============================================================================
// Card Skeleton (for loading placeholders)
// =============================================================================

interface SkeletonProps {
  count?: number;
  className?: string;
}

export function CardSkeleton({ count = 3, className = '' }: SkeletonProps) {
  return (
    <div className={`space-y-3 ${className}`}>
      {[...Array(count)].map((_, i) => (
        <div key={i} className="animate-pulse">
          <div className="h-16 bg-gray-700/50 rounded-lg" />
        </div>
      ))}
    </div>
  );
}

export function TableRowSkeleton({ count = 5, columns = 6, className = '' }: SkeletonProps & { columns?: number }) {
  return (
    <div className={`space-y-2 ${className}`}>
      {[...Array(count)].map((_, i) => (
        <div key={i} className="animate-pulse flex gap-4">
          {[...Array(columns)].map((_, j) => (
            <div 
              key={j} 
              className="h-8 bg-gray-700/50 rounded flex-1" 
              style={{ maxWidth: j === 0 ? '100px' : undefined }}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

// Default export for convenience
export default {
  LoadingState,
  ErrorState,
  EmptyState,
  FilteredEmptyState,
  InlineLoading,
  InlineError,
  InlineEmpty,
  CardSkeleton,
  TableRowSkeleton,
};
