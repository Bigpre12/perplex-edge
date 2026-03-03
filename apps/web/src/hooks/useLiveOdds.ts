"use client";

import { useEffect, useRef, useState, useCallback } from 'react';
import { API_ENDPOINTS } from '@/lib/apiConfig';

export function useLiveOdds(sportId: string | number) {
    const [props, setProps] = useState<any[]>([]);
    const [connected, setConnected] = useState(false);
    const [lastUpdate, setLastUpdate] = useState<string | null>(null);
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        let reconnectTimeout: NodeJS.Timeout;

        const connect = () => {
            // Use the central WS endpoint from apiConfig
            const ws = new WebSocket(API_ENDPOINTS.WS_ODDS);
            wsRef.current = ws;

            ws.onopen = () => {
                setConnected(true);
                console.log('🔴 LUCRIX LIVE CONNECTED');
            };

            ws.onmessage = (event) => {
                try {
                    if (event.data === 'pong') return;
                    const msg = JSON.parse(event.data);

                    if (msg.type === 'welcome' && msg.items) {
                        setProps(msg.items);
                    }

                    if (msg.type === 'LIVE_EV_UPDATE' && msg.data?.items) {
                        setProps(msg.data.items);
                        setLastUpdate(msg.timestamp || new Date().toISOString());
                    }

                    if (msg.type === 'props_update') {
                        setLastUpdate(msg.timestamp);
                    }
                } catch (err) {
                    console.error('WS Parse Error:', err);
                }
            };

            ws.onclose = () => {
                setConnected(false);
                reconnectTimeout = setTimeout(connect, 5000);
            };

            ws.onerror = () => {
                ws.close();
            };
        };

        connect();

        // Keepalive ping every 30s
        const pingInterval = setInterval(() => {
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.send('ping');
            }
        }, 30000);

        return () => {
            if (wsRef.current) {
                // To avoid "WebSocket is closed before the connection is established" warning,
                // we only call close if it's actually connecting or open.
                const state = wsRef.current.readyState;
                if (state === WebSocket.CONNECTING || state === WebSocket.OPEN) {
                    wsRef.current.close();
                }
            }
            clearTimeout(reconnectTimeout);
            clearInterval(pingInterval);
        };
    }, [sportId]);

    return { props, connected, lastUpdate };
}
