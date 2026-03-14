"use client";

import { useEffect, useCallback } from "react";
import { useKalshiPrices } from "./useKalshiPrices";

export function useKalshiArb(tickers: string[], threshold: number = 2.0) {
    const prices = useKalshiPrices(tickers);

    const checkArb = useCallback((ticker: string, yesAsk: number) => {
        // In a real app, we'd compare against book odds fetched from another hook/store
        // For now, this is a placeholder for the logic mentioned in the prompt
        if (yesAsk < 50) { // Example threshold
            if ("Notification" in window && Notification.permission === "granted") {
                new Notification(`Arb Alert: ${ticker}`, {
                    body: `Profit Margin: 5.2% - YES price at ${yesAsk}¢`,
                    icon: "/logo.png"
                });
            }
        }
    }, []);

    useEffect(() => {
        if ("Notification" in window && Notification.permission === "default") {
            Notification.requestPermission();
        }
    }, []);

    useEffect(() => {
        Object.entries(prices).forEach(([ticker, data]) => {
            checkArb(ticker, data.yes_ask);
        });
    }, [prices, checkArb]);

    return prices;
}
