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
        let timerId: NodeJS.Timeout;

        const runCheck = async () => {
            const success = await check();
            if (success) {
                timerId = setTimeout(runCheck, 30000);
            } else {
                handleFailure();
                const delays = [0, 3000, 8000, 15000];
                const nextDelay = delays[failCount + 1] || 15000;
                timerId = setTimeout(runCheck, nextDelay);
            }
        };

        runCheck();

        return () => {
            if (timerId) clearTimeout(timerId);
        };
    }, [setBackendOnline, setIsConnecting]); 

    return { 
        checkNow: check 
    };
}
