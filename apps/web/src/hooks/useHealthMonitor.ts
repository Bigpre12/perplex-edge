"use client";
import { useEffect, useState } from 'react';
import API, { isApiError } from '@/lib/api';
import { useLucrixStore } from "@/store";

export function useHealthMonitor() {
    const { setBackendOnline, setIsConnecting } = useLucrixStore();
    const [failCount, setFailCount] = useState(0);

    const check = async () => {
        try {
            const result = await API.health();
            if (!isApiError(result)) {
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
        let cooldownUntil = 0;

        const interval = setInterval(async () => {
            const now = Date.now();
            if (now < cooldownUntil) return;

            try {
                const result = await API.health();
                if (!isApiError(result)) {
                    setBackendOnline(true);
                    setIsConnecting(false);
                    failures = 0;
                } else {
                    throw new Error("API response error");
                }
            } catch (err) {
                failures++;
                if (failures < 3) {
                    setIsConnecting(true);
                } else {
                    setBackendOnline(false);
                    setIsConnecting(false);
                    // 5-minute cooldown (circuit breaker)
                    console.error("[Health Monitor] 3 failures. Opening circuit for 5 minutes.");
                    cooldownUntil = Date.now() + 300000;
                    failures = 0; // Reset count to retry after cooldown
                }
            }
        }, 30000);

        return () => {
            clearInterval(interval);
        };
    }, [setBackendOnline, setIsConnecting]);

    return { 
        checkNow: check 
    };
}
