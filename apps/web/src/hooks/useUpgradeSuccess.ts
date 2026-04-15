"use client";
import { useState, useEffect } from 'react';
import API, { isApiError } from '@/lib/api';
import { useSubscription } from './useSubscription';

/**
 * useUpgradeSuccess
 * Polling hook to detect when a user's tier has successfully transitioned in the DB
 * after a Stripe checkout completion.
 */
export function useUpgradeSuccess(targetTier: string, onSuccess: () => void) {
    const { tier, refresh } = useSubscription();
    const [isPolling, setIsPolling] = useState(false);

    useEffect(() => {
        if (!isPolling || tier === targetTier) {
            if (tier === targetTier && isPolling) {
                setIsPolling(false);
                onSuccess();
            }
            return;
        }

        const interval = setInterval(async () => {
            const res = await API.authMe();
            if (!isApiError(res)) {
                if (res.subscription_tier === targetTier) {
                    setIsPolling(false);
                    refresh();
                    onSuccess();
                }
            }
        }, 3000); // Poll every 3s

        const timeout = setTimeout(() => {
            setIsPolling(false);
        }, 30000); // Stop polling after 30s max

        return () => {
            clearInterval(interval);
            clearTimeout(timeout);
        };
    }, [isPolling, tier, targetTier, onSuccess, refresh]);

    return {
        startPolling: () => setIsPolling(true),
        isPolling
    };
}
