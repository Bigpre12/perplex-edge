"use client";

import { useState, useEffect } from "react";
import { Bell, BellRing, Loader2 } from "lucide-react";

// The VAPID Public Key (replace with the generated env key in production)
const PUBLIC_VAPID_KEY = "BKQ9P9RY1ZcQf97K13tOOhM6g1x4Uq1sxgC-N32bLhC2B3n_b5G7Y6yB_y302B6a0xZ1-B8Z8_tT02d1z2x2Q";

import { api, isApiError } from "@/lib/api";

export default function PushSubscriber() {
    const [isSubscribed, setIsSubscribed] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if already subscribed on mount
        const checkSubscription = async () => {
            if ("serviceWorker" in navigator && "PushManager" in window) {
                try {
                    // Service worker disabled to prevent caching issues
                    // const registration = await navigator.serviceWorker.register("/sw.js?v=4");
                    // const subscription = await registration.pushManager.getSubscription();
                    // setIsSubscribed(!!subscription);
                } catch (e) {
                    console.error("SW Registration failed:", e);
                }
            }
            setLoading(false);
        };
        checkSubscription();
    }, []);

    const urlBase64ToUint8Array = (base64String: string) => {
        const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
        const base64 = (base64String + padding).replace(/\-/g, "+").replace(/_/g, "/");
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    };

    const subscribeToPush = async () => {
        if (!("serviceWorker" in navigator)) return;
        setLoading(true);

        try {
            // Service worker disabled to prevent caching issues
            // const registration = await navigator.serviceWorker.ready;
            // const subscription = await registration.pushManager.subscribe({
            //     userVisibleOnly: true,
            //     applicationServerKey: urlBase64ToUint8Array(PUBLIC_VAPID_KEY)
            // });

            // Post to backend
            // const subData = JSON.parse(JSON.stringify(subscription));

            // await api.post('/push/subscribe', {
            //     user_id: "1", // Hardcoded admin user id for demo
            //     endpoint: subData.endpoint,
            //     keys: subData.keys
            // });

            // setIsSubscribed(true);
        } catch (error) {
            console.error("Failed to subscribe to push", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <button
            onClick={subscribeToPush}
            disabled={loading || isSubscribed}
            className={`flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-lg transition-all ${isSubscribed
                ? "bg-accent-green/20 text-accent-green border border-accent-green/30"
                : "bg-surface text-secondary hover:text-white border border-slate-700 hover:border-primary/50"
                }`}
        >
            {loading ? <Loader2 size={16} className="animate-spin" /> : (isSubscribed ? <BellRing size={16} /> : <Bell size={16} />)}
            {isSubscribed ? "Alerts Active" : "Subscribe to Steam Alerts"}
        </button>
    );
}
