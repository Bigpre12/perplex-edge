"use client";

import { useState, useEffect, useCallback, useRef } from "react";

interface PriceUpdate {
    ticker: string;
    yes_bid: number;
    yes_ask: number;
    last_price: number;
}

export function useKalshiPrices(tickers: string[]) {
    const [prices, setPrices] = useState<Record<string, PriceUpdate>>({});
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const retryCountRef = useRef(0);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        const tickerParams = tickers.length > 0 ? `&tickers=${tickers.join(",")}` : "";
        // In production, get token from Clerk/Supabase
        const token = "mock_token";
        const wsUrl = `ws://localhost:8000/ws/kalshi?token=${token}${tickerParams}`;

        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log("KalshiWS: Connected");
            retryCountRef.current = 0;
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.ticker) {
                    setPrices((prev) => ({
                        ...prev,
                        [data.ticker]: data,
                    }));
                }
            } catch (err) {
                console.error("KalshiWS: Error parsing message", err);
            }
        };

        ws.onclose = () => {
            console.log("KalshiWS: Disconnected");
            const delay = Math.min(1000 * Math.pow(2, retryCountRef.current), 30000);
            reconnectTimeoutRef.current = setTimeout(() => {
                retryCountRef.current += 1;
                connect();
            }, delay);
        };

        ws.onerror = (err) => {
            console.error("KalshiWS: Error", err);
            ws.close();
        };
    }, [tickers]);

    useEffect(() => {
        connect();
        return () => {
            if (wsRef.current) {
                wsRef.current.onclose = null;
                wsRef.current.close();
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
        };
    }, [connect]);

    return prices;
}
