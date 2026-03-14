import { useEffect, useRef, useState } from 'react';
import { SportKey } from '@/lib/sports.config';

const WS_URL = process.env.EXPO_PUBLIC_WS_URL || 'ws://localhost:3300/ws';

export function useWebSocket<T>(sport: SportKey, type: 'odds' | 'alerts' | 'brain') {
    const [data, setData] = useState<T | null>(null);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        const connect = () => {
            ws.current = new WebSocket(`${WS_URL}/${type}/${sport}`);

            ws.current.onmessage = (event) => {
                try {
                    const parsed = JSON.parse(event.data);
                    setData(parsed);
                } catch (err) {
                    console.error('[WS] Parse error:', err);
                }
            };

            ws.current.onerror = (err) => {
                console.error('[WS] Error:', err);
            };

            ws.current.onclose = () => {
                console.log('[WS] Closed, retrying in 5s...');
                setTimeout(connect, 5000);
            };
        };

        connect();

        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, [sport, type]);

    return data;
}
