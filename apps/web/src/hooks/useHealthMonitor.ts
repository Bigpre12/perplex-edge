"use client";
import { useEffect, useState } from 'react';
import API, { isLivePingReachable } from '@/lib/api';
import { useLucrixStore } from "@/store";

export function useHealthMonitor() {
    const { setBackendOnline, setIsConnecting } = useLucrixStore();
    const [failCount, setFailCount] = useState(0);

    const check = async () => {
        try {
            const result = await API.livePing();
            if (isLivePingReachable(result)) {
                setBackendOnline(true);
                setIsConnecting(false);
                setFailCount(0);
                return true;
            } else {
                return false;
            }
        } catch (err) {
            return false;
        }
    };

    const handleFailure = () => {
        setFailCount(prev => {
            const newCount = prev + 1;
            if (newCount < 4) {
                setIsConnecting(true);
            } else {
                setBackendOnline(false);
                setIsConnecting(false);
            }
            return newCount;
        });
    };

    useEffect(() => {
        let failures = 0;

        const interval = setInterval(async () => {
            if (failures >= 3) return; // frontend circuit breaker — stop after 3 fails

            try {
                const data = await API.livePing();
                if (!isLivePingReachable(data)) {
                    throw new Error('health ping not reachable');
                }
                setBackendOnline(true);
                setIsConnecting(false);
                failures = 0;
            } catch (e: any) {
                // Don't retry 401/403 — those are auth errors, not transient
                if (e?.response?.status === 401 || e?.response?.status === 403) {
                    setBackendOnline(false);
                    setIsConnecting(false);
                    failures = 3; // immediately open the frontend breaker
                    return;
                }
                failures++;
                if (failures >= 3) {
                    setBackendOnline(false);
                    setIsConnecting(false);
                }
            }
        }, 30000);

        return () => clearInterval(interval); // CRITICAL cleanup
    }, [setBackendOnline, setIsConnecting]);

    return { 
        checkNow: check 
    };
}
