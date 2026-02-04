/**
 * PricingPage - Subscription plans with Whop checkout integration.
 * 
 * Shows:
 * - Monthly and yearly pricing options
 * - Feature comparison (Free vs Pro)
 * - Whop checkout buttons
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuthContext } from '../context/AuthContext';

// Whop product URLs (set these in environment)
const WHOP_MONTHLY_URL = import.meta.env.VITE_WHOP_MONTHLY_URL || 'https://whop.com/checkout/your-monthly-plan';
const WHOP_YEARLY_URL = import.meta.env.VITE_WHOP_YEARLY_URL || 'https://whop.com/checkout/your-yearly-plan';

// Pricing
const MONTHLY_PRICE = 29;
const YEARLY_PRICE = 199;
const YEARLY_MONTHLY_EQUIVALENT = Math.round(YEARLY_PRICE / 12);
const YEARLY_SAVINGS = Math.round((1 - YEARLY_PRICE / (MONTHLY_PRICE * 12)) * 100);

interface PlanFeature {
  name: string;
  free: boolean | string;
  pro: boolean | string;
}

const FEATURES: PlanFeature[] = [
  { name: 'Sports access', free: 'NBA + NFL', pro: 'All 8 sports' },
  { name: 'Daily props', free: '10 per day', pro: 'Unlimited' },
  { name: 'EV calculations', free: true, pro: true },
  { name: 'Kelly sizing', free: true, pro: true },
  { name: 'Hot/Cold players', free: 'Summary only', pro: 'Full with filters' },
  { name: 'Stats market filters', free: false, pro: true },
  { name: 'Parlay Builder', free: '3 legs max', pro: 'Unlimited legs' },
  { name: 'Live EV Feed', free: false, pro: true },
  { name: 'Alt Line Explorer', free: false, pro: true },
  { name: 'Watchlists', free: false, pro: true },
  { name: 'My Edge tracking', free: false, pro: true },
  { name: 'Backtest tool', free: false, pro: true },
  { name: 'Advanced Analytics', free: false, pro: true },
  { name: 'Data export', free: false, pro: true },
];

export function PricingPage() {
  const { isSignedIn, user, isPro, isTrial, trialDaysLeft } = useAuthContext();
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');

  // Handle checkout redirect
  const handleCheckout = () => {
    const url = billingPeriod === 'yearly' ? WHOP_YEARLY_URL : WHOP_MONTHLY_URL;
    
    // Add user ID to URL for Whop webhook matching
    if (user?.id) {
      const checkoutUrl = new URL(url);
      checkoutUrl.searchParams.set('user_id', user.id);
      window.location.href = checkoutUrl.toString();
    } else {
      window.location.href = url;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="max-w-5xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Get full access to all sports, unlimited props, and premium features.
            Start with a 7-day free trial.
          </p>
        </div>

        {/* Current plan status */}
        {isSignedIn && (
          <div className="mb-8 text-center">
            {isPro ? (
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-900/30 border border-green-700 rounded-full">
                <span className="w-2 h-2 bg-green-400 rounded-full" />
                <span className="text-green-400 font-medium">You have Pro access</span>
              </div>
            ) : isTrial ? (
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-900/30 border border-blue-700 rounded-full">
                <span className="w-2 h-2 bg-blue-400 rounded-full" />
                <span className="text-blue-400 font-medium">
                  Trial: {trialDaysLeft} days remaining
                </span>
              </div>
            ) : (
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-800 border border-gray-700 rounded-full">
                <span className="text-gray-400">Free plan</span>
              </div>
            )}
          </div>
        )}

        {/* Billing toggle */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex rounded-lg bg-gray-800 p-1">
            <button
              onClick={() => setBillingPeriod('monthly')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                billingPeriod === 'monthly'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingPeriod('yearly')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                billingPeriod === 'yearly'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Yearly
              <span className="ml-1 text-xs text-green-400">Save {YEARLY_SAVINGS}%</span>
            </button>
          </div>
        </div>

        {/* Pricing cards */}
        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* Free Plan */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-8">
            <h2 className="text-xl font-bold text-white mb-2">Free</h2>
            <p className="text-gray-400 mb-6">Get started with basic features</p>
            
            <div className="mb-6">
              <span className="text-4xl font-bold text-white">$0</span>
              <span className="text-gray-400">/forever</span>
            </div>

            <Link
              to="/today"
              className="block w-full py-3 px-4 bg-gray-700 hover:bg-gray-600 text-white font-medium text-center rounded-lg transition-colors mb-6"
            >
              Get Started Free
            </Link>

            <ul className="space-y-3">
              {FEATURES.slice(0, 7).map((feature) => (
                <li key={feature.name} className="flex items-center gap-3 text-sm">
                  {feature.free ? (
                    <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5 text-gray-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  )}
                  <span className={feature.free ? 'text-gray-300' : 'text-gray-500'}>
                    {feature.name}
                    {typeof feature.free === 'string' && (
                      <span className="text-gray-500 ml-1">({feature.free})</span>
                    )}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          {/* Pro Plan */}
          <div className="bg-gradient-to-br from-blue-900/50 to-purple-900/50 rounded-xl border border-blue-700 p-8 relative">
            {/* Popular badge */}
            <div className="absolute -top-3 left-1/2 -translate-x-1/2">
              <span className="px-3 py-1 bg-blue-600 text-white text-xs font-bold rounded-full">
                MOST POPULAR
              </span>
            </div>

            <h2 className="text-xl font-bold text-white mb-2">Pro</h2>
            <p className="text-gray-400 mb-6">Full access to everything</p>
            
            <div className="mb-6">
              {billingPeriod === 'yearly' ? (
                <>
                  <span className="text-4xl font-bold text-white">${YEARLY_MONTHLY_EQUIVALENT}</span>
                  <span className="text-gray-400">/mo</span>
                  <div className="text-sm text-gray-400 mt-1">
                    Billed ${YEARLY_PRICE}/year
                  </div>
                </>
              ) : (
                <>
                  <span className="text-4xl font-bold text-white">${MONTHLY_PRICE}</span>
                  <span className="text-gray-400">/mo</span>
                </>
              )}
            </div>

            {isPro ? (
              <div className="w-full py-3 px-4 bg-green-600/20 border border-green-600 text-green-400 font-medium text-center rounded-lg mb-6">
                Current Plan
              </div>
            ) : (
              <button
                onClick={handleCheckout}
                className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg transition-colors mb-6"
              >
                {isTrial ? 'Upgrade Now' : 'Start 7-Day Free Trial'}
              </button>
            )}

            <ul className="space-y-3">
              {FEATURES.map((feature) => (
                <li key={feature.name} className="flex items-center gap-3 text-sm">
                  <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-gray-300">
                    {feature.name}
                    {typeof feature.pro === 'string' && (
                      <span className="text-blue-400 ml-1">({feature.pro})</span>
                    )}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* FAQ */}
        <div className="max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-white text-center mb-8">
            Frequently Asked Questions
          </h2>
          
          <div className="space-y-4">
            <details className="bg-gray-800 rounded-lg border border-gray-700">
              <summary className="px-6 py-4 cursor-pointer text-white font-medium">
                What happens after my trial ends?
              </summary>
              <div className="px-6 pb-4 text-gray-400 text-sm">
                After your 7-day trial, you'll be automatically downgraded to the free plan 
                unless you subscribe. You won't be charged anything during the trial.
              </div>
            </details>

            <details className="bg-gray-800 rounded-lg border border-gray-700">
              <summary className="px-6 py-4 cursor-pointer text-white font-medium">
                Can I cancel anytime?
              </summary>
              <div className="px-6 pb-4 text-gray-400 text-sm">
                Yes, you can cancel your subscription at any time. You'll continue to have 
                Pro access until the end of your billing period.
              </div>
            </details>

            <details className="bg-gray-800 rounded-lg border border-gray-700">
              <summary className="px-6 py-4 cursor-pointer text-white font-medium">
                Do you offer refunds?
              </summary>
              <div className="px-6 pb-4 text-gray-400 text-sm">
                We offer a full refund within 7 days of your first payment if you're not satisfied. 
                Contact support and we'll process it right away.
              </div>
            </details>

            <details className="bg-gray-800 rounded-lg border border-gray-700">
              <summary className="px-6 py-4 cursor-pointer text-white font-medium">
                How accurate is the model?
              </summary>
              <div className="px-6 pb-4 text-gray-400 text-sm">
                Our model is calibrated to be accurate within expected variance. Check the 
                Model Performance page to see historical calibration data and realized ROI.
              </div>
            </details>
          </div>
        </div>

        {/* Support CTA */}
        <div className="mt-12 text-center">
          <p className="text-gray-400">
            Have questions? Join our{' '}
            <a 
              href="https://discord.gg/qRMrfn9d" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300"
            >
              Discord community
            </a>
            {' '}or email{' '}
            <a href="mailto:support@perplex.com" className="text-blue-400 hover:text-blue-300">
              support@perplex.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default PricingPage;
