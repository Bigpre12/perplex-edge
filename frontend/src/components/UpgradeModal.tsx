/**
 * UpgradeModal - Prompts free users to upgrade when they hit limits.
 * 
 * Shown when:
 * - User views more than 10 props (daily limit)
 * - User tries to access a locked sport
 * - User tries to use premium features (stats filters, etc.)
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export type UpgradeReason = 
  | 'props_limit'
  | 'locked_sport'
  | 'stats_filters'
  | 'live_ev'
  | 'alt_lines'
  | 'watchlists'
  | 'backtest'
  | 'analytics'
  | 'my_edge'
  | 'parlay_legs'
  | 'export';

interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  reason: UpgradeReason;
  sportName?: string;  // For locked_sport reason
}

// Messages for each upgrade reason
const UPGRADE_MESSAGES: Record<UpgradeReason, { title: string; description: string }> = {
  props_limit: {
    title: "Daily Prop Limit Reached",
    description: "Free accounts can view up to 10 props per day. Upgrade for unlimited access to all props across every sport.",
  },
  locked_sport: {
    title: "Sport Locked",
    description: "Free accounts only have access to NBA and NFL. Upgrade to unlock all sports including MLB, NHL, NCAAB, and more.",
  },
  stats_filters: {
    title: "Advanced Stats Filters",
    description: "Filter hot/cold players by market and side with Pro. See exactly which stat types are trending.",
  },
  live_ev: {
    title: "Live EV Feed",
    description: "Get real-time EV updates as lines move. Never miss a value opportunity.",
  },
  alt_lines: {
    title: "Alt Line Explorer",
    description: "Explore alternate lines to find the best value for any prop.",
  },
  watchlists: {
    title: "Watchlists",
    description: "Save and track your favorite filters. Get notified when new picks match.",
  },
  backtest: {
    title: "Backtest Tool",
    description: "Test your strategies against historical data to validate your edge.",
  },
  analytics: {
    title: "Advanced Analytics",
    description: "Deep dive into model performance, calibration, and ROI analysis.",
  },
  my_edge: {
    title: "My Edge Tracking",
    description: "Track your betting performance, ROI by sport, and EV realization.",
  },
  parlay_legs: {
    title: "Unlimited Parlay Legs",
    description: "Free accounts are limited to 3-leg parlays. Upgrade for unlimited legs.",
  },
  export: {
    title: "Export Data",
    description: "Export picks and analytics data for your own analysis.",
  },
};

export function UpgradeModal({ isOpen, onClose, reason, sportName }: UpgradeModalProps) {
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsAnimating(true);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const message = UPGRADE_MESSAGES[reason];
  const title = reason === 'locked_sport' && sportName 
    ? `${sportName} is Locked`
    : message.title;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div 
        className={`absolute inset-0 bg-black transition-opacity duration-300 ${
          isAnimating ? 'opacity-70' : 'opacity-0'
        }`}
      />
      
      {/* Modal */}
      <div 
        className={`relative bg-gray-800 rounded-xl border border-gray-700 max-w-md w-full shadow-2xl transform transition-all duration-300 ${
          isAnimating ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
        }`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Content */}
        <div className="p-6">
          {/* Icon */}
          <div className="w-16 h-16 mx-auto mb-4 bg-blue-600/20 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>

          {/* Title */}
          <h2 className="text-xl font-bold text-white text-center mb-2">
            {title}
          </h2>

          {/* Description */}
          <p className="text-gray-400 text-center mb-6">
            {message.description}
          </p>

          {/* Features list */}
          <div className="bg-gray-900/50 rounded-lg p-4 mb-6">
            <h3 className="text-sm font-medium text-gray-300 mb-3">Pro includes:</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li className="flex items-center gap-2">
                <span className="text-green-400">+</span>
                All 16 sports (NBA, NFL, MLB, NHL, NCAAB, NCAAF, WNBA, ATP, WTA, EPL, UCL, UEL, UECL, MLS, PGA, UFC)
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-400">+</span>
                Unlimited daily props
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-400">+</span>
                Full Stats with market filters
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-400">+</span>
                My Edge performance tracking
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-400">+</span>
                Alt lines, watchlists, and more
              </li>
            </ul>
          </div>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Link
              to="/pricing"
              className="flex-1 px-4 py-3 bg-blue-600 hover:bg-blue-500 text-white font-medium text-center rounded-lg transition-colors"
              onClick={onClose}
            >
              View Plans
            </Link>
            <button
              onClick={onClose}
              className="flex-1 px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
            >
              Maybe Later
            </button>
          </div>

          {/* Trial note */}
          <p className="text-xs text-gray-500 text-center mt-4">
            Start with a 7-day free trial. No credit card required.
          </p>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Hook for managing upgrade modal state
// =============================================================================

interface UseUpgradeModalReturn {
  isOpen: boolean;
  reason: UpgradeReason;
  sportName?: string;
  showUpgrade: (reason: UpgradeReason, sportName?: string) => void;
  closeUpgrade: () => void;
}

export function useUpgradeModal(): UseUpgradeModalReturn {
  const [isOpen, setIsOpen] = useState(false);
  const [reason, setReason] = useState<UpgradeReason>('props_limit');
  const [sportName, setSportName] = useState<string | undefined>();

  const showUpgrade = (r: UpgradeReason, sport?: string) => {
    setReason(r);
    setSportName(sport);
    setIsOpen(true);
  };

  const closeUpgrade = () => {
    setIsOpen(false);
  };

  return {
    isOpen,
    reason,
    sportName,
    showUpgrade,
    closeUpgrade,
  };
}

export default UpgradeModal;
