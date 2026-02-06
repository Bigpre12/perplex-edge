/**
 * Whop checkout configuration.
 */

export const WHOP_CHECKOUT_URLS = {
  free: 'https://whop.com/checkout/plan_WxHa3UGwMmjdd',
  pro_monthly: 'https://whop.com/checkout/plan_8Qztt62kvlW8y',
  pro_yearly: 'https://whop.com/checkout/plan_eeIAyl9zqIhfb',
};

/**
 * Get Whop checkout URL for a plan.
 */
export function getWhopCheckoutUrl(plan: 'free' | 'pro_monthly' | 'pro_yearly'): string {
  return WHOP_CHECKOUT_URLS[plan] || WHOP_CHECKOUT_URLS.free;
}

/**
 * Open Whop checkout in a new tab.
 */
export function openWhopCheckout(plan: 'free' | 'pro_monthly' | 'pro_yearly'): void {
  const url = getWhopCheckoutUrl(plan);
  if (url) {
    window.open(url, '_blank', 'noopener,noreferrer');
  }
}

/**
 * Get all Pro checkout URLs.
 */
export function getProCheckoutUrls(): { monthly: string; yearly: string } {
  return {
    monthly: WHOP_CHECKOUT_URLS.pro_monthly,
    yearly: WHOP_CHECKOUT_URLS.pro_yearly,
  };
}
