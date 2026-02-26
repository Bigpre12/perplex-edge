"use client";

import { useState, useEffect } from "react";
import { Bell, BellOff, ShieldCheck, Loader2 } from "lucide-react";
import { getAuthToken, getUser } from "@/lib/auth";

export default function NotificationManager() {
    const [status, setStatus] = useState<"default" | "granted" | "denied">("default");
    const [isSubscribing, setIsSubscribing] = useState(false);

    useEffect(() => {
        if ("Notification" in window) {
            setStatus(Notification.permission);
        }
    }, []);

    const urlBase64ToUint8Array = (base64String: string) => {
        const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
        const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    };

    const subscribeToPush = async () => {
        if (!("serviceWorker" in navigator)) return;

        setIsSubscribing(true);
        try {
            const registration = await navigator.serviceWorker.register("/sw.js");
            const permission = await Notification.requestPermission();
            setStatus(permission);

            if (permission === "granted") {
                const subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY || "")
                });

                // Send to backend
                const token = getAuthToken();
                const user = getUser();
                if (token && user) {
                    await fetch("http://localhost:8000/api/push/subscribe", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            user_id: user.id,
                            endpoint: subscription.endpoint,
                            keys: {
                                p256dh: btoa(String.fromCharCode.apply(null, Array.from(new Uint8Array(subscription.getKey("p256dh")!)))),
                                auth: btoa(String.fromCharCode.apply(null, Array.from(new Uint8Array(subscription.getKey("auth")!))))
                            }
                        })
                    });
                }
            }
        } catch (err) {
            console.error("Subscription failed:", err);
        } finally {
            setIsSubscribing(false);
        }
    };

    return (
        <div className="glass-panel p-6 rounded-2xl border-white/[0.05]">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${status === 'granted' ? 'bg-primary/20 text-primary' : 'bg-slate-800 text-slate-500'}`}>
                        <Bell size={20} />
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-white uppercase tracking-tight">Intelligence Alerts</h3>
                        <p className="text-[10px] text-slate-500 font-medium">Real-time win/loss and market move notifications</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {status === "granted" ? (
                        <span className="text-[10px] font-black text-primary uppercase flex items-center gap-1.5">
                            <ShieldCheck size={12} /> ACTIVE
                        </span>
                    ) : (
                        <button
                            onClick={subscribeToPush}
                            disabled={isSubscribing}
                            className="px-4 py-2 bg-primary text-background-dark font-black rounded-lg text-[10px] hover:scale-105 transition-all disabled:opacity-50"
                        >
                            {isSubscribing ? <Loader2 className="animate-spin" /> : "ENABLE ALERTS"}
                        </button>
                    )}
                </div>
            </div>

            {status === "denied" && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl">
                    <p className="text-[10px] text-red-500 font-bold flex items-center gap-2">
                        <BellOff size={12} /> Notifications are blocked in your browser settings.
                    </p>
                </div>
            )}
        </div>
    );
}
