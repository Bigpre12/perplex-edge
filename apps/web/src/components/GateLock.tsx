"use client";
import React from "react";
import { useLucrixStore } from "@/store";
import { canAccess as checkAccess } from "@/lib/permissions";

interface Props {
    feature: string;
    children: React.ReactNode;
    reason?: string;
}

export default function GateLock({ feature, children, reason }: Props) {
    const userTier = useLucrixStore((state: any) => state.userTier);
    const hasAccess = checkAccess(userTier, feature as any);
    
    const [mounted, setMounted] = React.useState(false);
    React.useEffect(() => {
        setMounted(true);
    }, []);

    const isDev = typeof window !== 'undefined' && 
                 (window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1' || 
                  window.location.hostname.startsWith('192.168.') || 
                  window.location.hostname.startsWith('172.'));

    // We MUST keep the outer div structure identical between server and client to avoid hydration errors.
    // Structural mismatch happens if we return children directly on the client but wrapped on the server.
    const showUnlocked = mounted && (isDev || hasAccess);

    return (
        <div className={`relative overflow-hidden rounded-xl ${showUnlocked ? "" : "pointer-events-none select-none"}`}>
            {/* Content container with conditional blur */}
            <div className={showUnlocked ? "h-full" : "blur-sm opacity-40 h-full"}>
                {children}
            </div>
            
            {/* Lock overlay - only show if NOT unlocked */}
            {!showUnlocked && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/90 backdrop-blur-md z-10 p-4 border border-lucrix-gold/20">
                  <div className="size-12 rounded-full bg-lucrix-gold/10 flex items-center justify-center border border-lucrix-gold/20 mb-3 shadow-[0_0_15px_rgba(245,197,24,0.1)]">
                      <span className="text-2xl">🔒</span>
                  </div>
                  <p className="text-white font-black text-xs uppercase tracking-widest">Premium Resource</p>
                  <p className="text-[#6B7280] text-[10px] mt-2 text-center max-w-[200px] font-bold">
                      {reason ?? "Upgrade your account to unlock professional betting intel."}
                  </p>
                  <a
                      href="/pricing"
                      className="mt-4 bg-lucrix-gold text-black text-[10px] font-black uppercase tracking-widest px-5 py-2 rounded-full transition-all hover:scale-105 active:scale-95 shadow-lg shadow-lucrix-gold/10"
                  >
                      Upgrade Now →
                  </a>
              </div>
            )}
        </div>
    );
}
