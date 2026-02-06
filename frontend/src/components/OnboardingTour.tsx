/**
 * OnboardingTour - First-time user walkthrough.
 * 
 * A 3-step overlay that guides new users through:
 * 1. Choosing sports to follow
 * 2. Understanding stat types / markets
 * 3. Running their first board scan (props page)
 * 
 * Stores completion flag in localStorage so it doesn't repeat.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ALL_SPORTS, SPORT_NAMES, FREE_SPORTS } from '../utils/planLimits';
import { useUserPlan } from '../context/AuthContext';

// Local storage key
const ONBOARDING_KEY = 'onboarding_complete';

// =============================================================================
// Types
// =============================================================================

interface OnboardingTourProps {
  /** Called when onboarding is completed or skipped */
  onComplete?: () => void;
}

type Step = 1 | 2 | 3;

// =============================================================================
// Main Component
// =============================================================================

export function OnboardingTour({ onComplete }: OnboardingTourProps) {
  const navigate = useNavigate();
  const { plan } = useUserPlan();
  const [step, setStep] = useState<Step>(1);
  const [selectedSports, setSelectedSports] = useState<number[]>([30, 31]); // NBA + NFL default
  const [selectedMarkets, setSelectedMarkets] = useState<string[]>(['PTS', 'REB', 'AST']);
  const [isVisible, setIsVisible] = useState(false);

  // Check if onboarding should show
  useEffect(() => {
    const completed = localStorage.getItem(ONBOARDING_KEY);
    if (!completed) {
      setIsVisible(true);
    }
  }, []);

  // Get available sports based on plan
  const availableSports = plan === 'free' ? FREE_SPORTS : ALL_SPORTS;

  // Complete onboarding
  const completeOnboarding = () => {
    localStorage.setItem(ONBOARDING_KEY, 'true');
    setIsVisible(false);
    onComplete?.();
  };

  // Skip onboarding
  const skipOnboarding = () => {
    localStorage.setItem(ONBOARDING_KEY, 'skipped');
    setIsVisible(false);
    onComplete?.();
  };

  // Handle step navigation
  const nextStep = () => {
    if (step < 3) {
      setStep((s) => (s + 1) as Step);
    } else {
      // Complete and navigate to props
      completeOnboarding();
      navigate('/props');
    }
  };

  const prevStep = () => {
    if (step > 1) {
      setStep((s) => (s - 1) as Step);
    }
  };

  // Toggle sport selection
  const toggleSport = (sportId: number) => {
    if (!availableSports.includes(sportId)) return;
    
    setSelectedSports((prev) =>
      prev.includes(sportId)
        ? prev.filter((id) => id !== sportId)
        : [...prev, sportId]
    );
  };

  // Toggle market selection
  const toggleMarket = (market: string) => {
    setSelectedMarkets((prev) =>
      prev.includes(market)
        ? prev.filter((m) => m !== market)
        : [...prev, market]
    );
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80">
      <div className="bg-gray-800 rounded-2xl border border-gray-700 max-w-lg w-full shadow-2xl overflow-hidden">
        {/* Progress Bar */}
        <div className="h-1 bg-gray-700">
          <div 
            className="h-full bg-blue-500 transition-all duration-300"
            style={{ width: `${(step / 3) * 100}%` }}
          />
        </div>

        {/* Header */}
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">
                {step === 1 && 'Choose Your Sports'}
                {step === 2 && 'Select Market Types'}
                {step === 3 && 'Ready to Find Edge'}
              </h2>
              <p className="text-sm text-gray-400 mt-1">
                Step {step} of 3
              </p>
            </div>
            <button
              onClick={skipOnboarding}
              className="text-gray-400 hover:text-white text-sm"
            >
              Skip
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Step 1: Sports Selection */}
          {step === 1 && (
            <div className="space-y-4">
              <p className="text-gray-300 text-sm">
                Select the sports you want to track. You can change this anytime.
              </p>
              
              <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                {ALL_SPORTS.map((sportId) => {
                  const isAvailable = availableSports.includes(sportId);
                  const isSelected = selectedSports.includes(sportId);
                  
                  return (
                    <button
                      key={sportId}
                      onClick={() => toggleSport(sportId)}
                      disabled={!isAvailable}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                        isSelected
                          ? 'bg-blue-600 text-white'
                          : isAvailable
                          ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                          : 'bg-gray-800 text-gray-500 cursor-not-allowed'
                      }`}
                    >
                      {SPORT_NAMES[sportId]}
                      {!isAvailable && (
                        <span className="ml-1 text-[10px] text-yellow-500">PRO</span>
                      )}
                    </button>
                  );
                })}
              </div>
              
              {plan === 'free' && (
                <p className="text-xs text-yellow-400/80">
                  Free tier includes NBA and NFL. Upgrade to Pro for all 16 sports.
                </p>
              )}
            </div>
          )}

          {/* Step 2: Market Types */}
          {step === 2 && (
            <div className="space-y-4">
              <p className="text-gray-300 text-sm">
                Choose the stat types you're most interested in betting on.
              </p>
              
              <div className="space-y-3">
                <div>
                  <h4 className="text-xs text-gray-400 uppercase mb-2">Basketball Stats</h4>
                  <div className="flex flex-wrap gap-2">
                    {['PTS', 'REB', 'AST', 'PRA', 'PR', 'PA', 'RA'].map((market) => (
                      <button
                        key={market}
                        onClick={() => toggleMarket(market)}
                        className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                          selectedMarkets.includes(market)
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        {market}
                      </button>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="text-xs text-gray-400 uppercase mb-2">Football Stats</h4>
                  <div className="flex flex-wrap gap-2">
                    {['Pass Yds', 'Rush Yds', 'Rec Yds', 'TDs', 'Receptions'].map((market) => (
                      <button
                        key={market}
                        onClick={() => toggleMarket(market)}
                        className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                          selectedMarkets.includes(market)
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        {market}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              
              <p className="text-xs text-gray-500">
                Don't worry - you'll see all market types on the board. These are just your defaults.
              </p>
            </div>
          )}

          {/* Step 3: Ready to Go */}
          {step === 3 && (
            <div className="space-y-4 text-center">
              <div className="w-20 h-20 mx-auto bg-green-600/20 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-white">You're all set!</h3>
                <p className="text-gray-400 text-sm mt-1">
                  Let's run your first board scan and find some edges.
                </p>
              </div>
              
              <div className="bg-gray-700/50 rounded-lg p-4 text-left text-sm text-gray-300">
                <p className="font-medium text-white mb-2">Quick tips:</p>
                <ul className="space-y-1 text-xs">
                  <li className="flex items-start gap-2">
                    <span className="text-green-400">+</span>
                    <span>Higher EV% = more expected profit</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-400">+</span>
                    <span>Green tier picks have the best model confidence</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-400">+</span>
                    <span>Use filters to narrow down the board</span>
                  </li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-700 flex justify-between">
          <button
            onClick={prevStep}
            disabled={step === 1}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              step === 1
                ? 'text-gray-500 cursor-not-allowed'
                : 'text-gray-300 hover:text-white hover:bg-gray-700'
            }`}
          >
            Back
          </button>
          
          <button
            onClick={nextStep}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg transition-colors"
          >
            {step === 3 ? 'Go to Props Board' : 'Continue'}
          </button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Hook for controlling onboarding visibility
// =============================================================================

export function useOnboarding() {
  const [showOnboarding, setShowOnboarding] = useState(false);
  
  useEffect(() => {
    const completed = localStorage.getItem(ONBOARDING_KEY);
    if (!completed) {
      setShowOnboarding(true);
    }
  }, []);
  
  const resetOnboarding = () => {
    localStorage.removeItem(ONBOARDING_KEY);
    setShowOnboarding(true);
  };
  
  const completeOnboarding = () => {
    localStorage.setItem(ONBOARDING_KEY, 'true');
    setShowOnboarding(false);
  };
  
  return {
    showOnboarding,
    resetOnboarding,
    completeOnboarding,
  };
}

// =============================================================================
// Check function (can be used to conditionally render)
// =============================================================================

export function hasCompletedOnboarding(): boolean {
  return localStorage.getItem(ONBOARDING_KEY) !== null;
}

export default OnboardingTour;
