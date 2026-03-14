"use client";
import { useEffect, useRef, useState, useCallback } from 'react';
import { API, apiFetch } from '@/lib/api';
import { SportKey } from '@/lib/sports.config';
import { useBackendStatus } from './useBackendStatus';

export function useLiveOdds(sportId: SportKey) {
    const [props, setProps] = useState<any[]>([]);
    const [connected, setConnected] = useState(false);
    const [lastUpdate, setLastUpdate] = useState<string | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const pollRef = useRef<NodeJS.Timeout | null>(null);
    const mountedRef = useRef(true);
    const { isDown } = useBackendStatus();

    const fetchHTTP = useCallback(async () => {
        if (isDown) return;
        try {
            const data = await apiFetch<any>(API.odds(sportId));
            const items: any[] = data?.data ?? data?.items ?? [];
            if (items.length > 0 && mountedRef.current) {
                setProps(items);
                setLastUpdate(new Date().toISOString());
                setConnected(true);
            }
        } catch (err) {
            console.warn('[useLiveOdds] HTTP fetch failed:', err);
            if (mountedRef.current) setConnected(false);
        }
    }, [sportId, isDown]);

    useEffect(() => {
        mountedRef.current = true;
        fetchHTTP();
        pollRef.current = setInterval(() => {
            if (!isDown) fetchHTTP();
        }, API.POLL_MS);

        let reconnectTimeout: NodeJS.Timeout;
        const tryWS = () => {
            if (isDown) return;
            try {
                const ws = new WebSocket(API.wsOdds);
                wsRef.current = ws;
                const killTimer = setTimeout(() => { if (ws.readyState !== WebSocket.OPEN) ws.close(); }, 5000);
                ws.onopen = () => { clearTimeout(killTimer); if (mountedRef.current) setConnected(true); };
                ws.onmessage = (e) => {
                    try {
                        if (e.data === 'pong') return;
                        const msg = JSON.parse(e.data);
                        const items = msg?.items ?? msg?.data?.items;
                        if (items?.length && mountedRef.current) {
                            setProps(items);
                            setLastUpdate(msg.timestamp ?? new Date().toISOString());
                        }
                    } catch (err) { console.warn('[useLiveOdds] WS message parse error:', err); }
                };
                ws.onclose = () => { reconnectTimeout = setTimeout(tryWS, 30000); };
                ws.onerror = () => ws.close();
            } catch (err) { console.warn('[useLiveOdds] WS connection error:', err); }
        };
        tryWS();

        const ping = setInterval(() => {
            if (wsRef.current?.readyState === WebSocket.OPEN) wsRef.current.send('ping');
        }, 30000);

        return () => {
            mountedRef.current = false;
            if (pollRef.current) clearInterval(pollRef.current);
            clearInterval(ping);
            clearTimeout(reconnectTimeout);
            if (wsRef.current && wsRef.current.readyState <= 1) wsRef.current.close();
        };
    }, [sportId, fetchHTTP, isDown]);

    return { props, connected, lastUpdate };
}
