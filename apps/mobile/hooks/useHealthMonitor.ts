import { useEffect, useRef } from 'react';
import { API, apiFetch } from '@/lib/api';
import { useLucrixStore } from '@/store/useLucrixStore';

export function useHealthMonitor(intervalMs = 15000) {
    const { setBackendOnline } = useLucrixStore();
    const failRef = useRef(0);
    const timerRef = useRef<ReturnType<typeof setInterval>>();

    const check = async () => {
        try {
            await apiFetch(API.health());
            failRef.current = 0;
            setBackendOnline(true);
        } catch {
            failRef.current++;
            if (failRef.current >= 3) setBackendOnline(false);
        }
    };

    useEffect(() => {
        check();
        timerRef.current = setInterval(check, intervalMs);
        return () => clearInterval(timerRef.current);
    }, []);
}
