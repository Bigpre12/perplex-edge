"use client";

import React, { useState, Suspense } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { Settings, Shield, Bell, CreditCard, Save, CheckCircle, Smartphone, User, Database } from "lucide-react";
import { clsx } from "clsx";

export default function SettingsPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">SYNCING PREFERENCES...</div>}>
      <SettingsContent />
    </Suspense>
  );
}

function SettingsContent() {
  const { token, user } = useAuth();
  const queryClient = useQueryClient();
  const [isSaved, setIsSaved] = useState(false);

  const { data: settings, isLoading, error } = useQuery({
    queryKey: ['user-settings'],
    queryFn: () => fetch(`${API_BASE}/api/user/settings`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.json()),
    enabled: !!token,
  });

  const mutation = useMutation({
    mutationFn: (newSettings: any) => fetch(`${API_BASE}/api/user/settings`, {
      method: "PUT",
      headers: { 
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}` 
      },
      body: JSON.stringify(newSettings)
    }).then(r => r.json()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-settings'] });
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    }
  });

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6 pt-12 px-4">
        <Skeleton className="h-12 w-64 mb-12" />
        <Skeleton className="h-48 w-full rounded-3xl" />
        <Skeleton className="h-48 w-full rounded-3xl" />
      </div>
    );
  }

  if (error) {
    return <div className="p-6"><ErrorBanner message="Settings Sync Failed." /></div>;
  }

  return (
    <div className="max-w-4xl mx-auto pb-24 space-y-12 pt-12 px-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-purple/10 p-2 rounded-lg border border-brand-purple/20">
              <Settings size={24} className="text-brand-purple" />
            </div>
            <h1 className="text-4xl font-black italic tracking-tighter uppercase text-white font-display">Command Center</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest italic">User Configuration & Auth Logic</p>
        </div>
        <button 
          onClick={() => mutation.mutate(settings)}
          disabled={mutation.isPending}
          className={clsx(
            "flex items-center gap-2 px-8 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all shadow-glow",
            isSaved ? "bg-brand-success text-white shadow-brand-success/20" : "bg-white text-black hover:bg-brand-purple hover:text-white"
          )}
        >
          {isSaved ? <CheckCircle size={14} /> : <Save size={14} />}
          {isSaved ? "Saved" : mutation.isPending ? "Syncing..." : "Sync Changes"}
        </button>
      </div>

      <div className="grid grid-cols-1 gap-8">
        {/* Profile Segment */}
        <section className="bg-lucrix-surface border border-lucrix-border rounded-3xl p-8 shadow-card relative overflow-hidden group">
          <div className="flex items-center gap-3 mb-8">
             <User size={18} className="text-brand-purple" />
             <h2 className="text-xs font-black text-white uppercase tracking-[0.2em]">Identity & Access</h2>
          </div>
          <div className="flex items-center gap-6">
             <div className="w-20 h-20 bg-lucrix-dark rounded-3xl border border-lucrix-border flex items-center justify-center text-3xl font-black text-brand-purple group-hover:shadow-glow group-hover:shadow-brand-purple/20 transition-all">
                {user?.email?.[0].toUpperCase()}
             </div>
             <div>
                <div className="text-xl font-black text-white italic uppercase tracking-tight">{user?.email?.split('@')[0]}</div>
                <div className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mt-1">{user?.email}</div>
                <div className="mt-4 flex gap-2">
                   <span className="bg-brand-purple/10 text-brand-purple border border-brand-purple/20 px-3 py-1 rounded-lg text-[8px] font-black uppercase tracking-widest">
                     {settings?.tier || "Free"} Access
                   </span>
                </div>
             </div>
          </div>
        </section>

        {/* Preferences */}
        <section className="bg-lucrix-surface border border-lucrix-border rounded-3xl p-8 shadow-card">
           <div className="flex items-center gap-3 mb-8">
             <Bell size={18} className="text-brand-cyan" />
             <h2 className="text-xs font-black text-white uppercase tracking-[0.2em]">Signal Routing</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
             <ToggleRow label="Push Alerts" description="Low-latency mobile notifications" active={true} />
             <ToggleRow label="Email Ingest" description="Daily sharp move summaries" active={false} />
             <ToggleRow label="Discord Bridge" description="Relay signals to private server" active={settings?.discord_connected} />
             <ToggleRow label="API Access" description="Enable raw data endpoints" active={settings?.tier === "Elite"} />
          </div>
        </section>

        {/* Sportsbooks */}
        <section className="bg-lucrix-surface border border-lucrix-border rounded-3xl p-8 shadow-card">
           <div className="flex items-center gap-3 mb-8">
             <Database size={18} className="text-brand-warning" />
             <h2 className="text-xs font-black text-white uppercase tracking-[0.2em]">Market Liquidity</h2>
          </div>
          <div className="flex flex-wrap gap-2">
             {["Fanduel", "Draftkings", "Pinnacle", "BetMGM", "Circa", "Caesars"].map((book) => (
                <button 
                  key={book}
                  className={clsx(
                    "px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest border transition-all",
                    settings?.books?.includes(book) ? "bg-brand-warning/10 text-brand-warning border-brand-warning/20 shadow-glow shadow-brand-warning/5" : "bg-lucrix-dark text-textMuted border-lucrix-border hover:border-textSecondary"
                  )}
                >
                  {book}
                </button>
             ))}
          </div>
        </section>
      </div>
    </div>
  );
}

function ToggleRow({ label, description, active }: any) {
  return (
    <div className="bg-lucrix-dark/50 border border-lucrix-border rounded-2xl p-4 flex items-center justify-between group hover:border-brand-cyan/20 transition-all">
      <div>
        <div className="text-[10px] font-black text-white uppercase tracking-widest mb-0.5">{label}</div>
        <div className="text-[9px] font-bold text-textMuted uppercase">{description}</div>
      </div>
      <div className={clsx(
        "w-10 h-5 rounded-full relative transition-all shadow-inner",
        active ? "bg-brand-cyan shadow-glow shadow-brand-cyan/20" : "bg-lucrix-surface border border-lucrix-border"
      )}>
        <div className={clsx(
          "absolute top-1 w-3 h-3 rounded-full bg-white transition-all",
          active ? "right-1" : "left-1 bg-textMuted"
        )} />
      </div>
    </div>
  );
}
