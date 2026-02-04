/**
 * TrialBanner - Shows trial countdown for users on trial plan.
 * 
 * Displayed at the top of the page when user has an active trial.
 * Links to pricing page for upgrade.
 */

import { Link } from 'react-router-dom';
import { useAuthContext } from '../context/AuthContext';

export function TrialBanner() {
  const { isSignedIn, isTrial, trialDaysLeft, isPro } = useAuthContext();

  // Don't show if not signed in, not on trial, or already pro
  if (!isSignedIn || !isTrial || isPro) {
    return null;
  }

  // Urgency colors based on days left
  const urgencyClass = trialDaysLeft !== null && trialDaysLeft <= 2
    ? 'bg-amber-900/50 border-amber-700 text-amber-200'
    : 'bg-blue-900/50 border-blue-700 text-blue-200';

  const daysText = trialDaysLeft === 1 
    ? '1 day' 
    : trialDaysLeft === 0 
      ? 'less than a day'
      : `${trialDaysLeft} days`;

  return (
    <div className={`border-b py-2 px-4 ${urgencyClass}`}>
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-sm">
            <strong>Trial:</strong> {daysText} remaining
          </span>
        </div>
        
        <Link
          to="/pricing"
          className="text-sm font-medium hover:underline flex items-center gap-1"
        >
          Keep full access
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </Link>
      </div>
    </div>
  );
}

export default TrialBanner;
