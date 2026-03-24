"use client";
import { useEffect, useRef } from 'react';
import { api, resetCircuit, isApiError } from '@/lib/api';
import { useLucrixStore } from "@/store";

export function useHealthMonitor(intervalMs = 15_000) {
    const { setBackendOnline } = useLucrixStore();
    const failRef = useRef(0);
    const timerRef = useRef<NodeJS.Timeout>();

    const check = async () => {
        try {
            const result = await api.health();
            if (!isApiError(result)) {
                failRef.current = 0;
                resetCircuit();           // reset breaker when back online
                setBackendOnline(true);
            } else {
                throw new Error(result.error);
            }
        } catch {
            failRef.current++;
            if (failRef.current >= 2) { // More aggressive offline detection
                setBackendOnline(false);
            }
        }
    };

    useEffect(() => {
        check();
        const interval = setInterval(check, intervalMs);
        timerRef.current = interval;
        return () => clearInterval(interval);
    }, [intervalMs]);

    return { check };
}
