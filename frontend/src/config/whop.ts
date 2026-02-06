/**
 * Whop checkout configuration.
 */

export const WHOP_CHECKOUT_URLS = {
  free: 'https://whop.com/checkout/plan_WxHa3UGwMmjdd',
  pro: '', // Add when available
};

/**
 * Get Whop checkout URL for a plan.
 */
export function getWhopCheckoutUrl(plan: 'free' | 'pro'): string {
  return WHOP_CHECKOUT_URLS[plan] || WHOP_CHECKOUT_URLS.free;
}

/**
 * Open Whop checkout in a new tab.
 */
export function openWhopCheckout(plan: 'free' | 'pro'): void {
  const url = getWhopCheckoutUrl(plan);
  if (url) {
    window.open(url, '_blank', 'noopener,noreferrer');
  }
}
