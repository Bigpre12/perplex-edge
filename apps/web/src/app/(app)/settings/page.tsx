"use client";

import React, { useState, Suspense } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { api, isApiError } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { SPORTS_CONFIG, SportKey } from "@/lib/sports.config";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { 
  Settings, 
  Bell, 
  CheckCircle, 
  User, 
  Database, 
  Key, 
  AlertTriangle, 
  LogOut,
  RefreshCw,
  Copy,
  Trash2,
  DollarSign,
  Monitor,
  Globe,
  ChevronDown
} from "lucide-react";
import { clsx } from "clsx";
import { motion } from "framer-motion";
import { EmptyState } from "@/components/shared/EmptyState";

const DEFAULT_USER_SETTINGS: Record<string, unknown> = {
  unit_size: 100,
  default_sport: "basketball_nba",
  default_sportsbook: "draftkings",
  theme: "dark",
  notifications_enabled: true,
  api_enabled: false,
  tier: "Free",
};

export default function SettingsPage() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<div className="p-10 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">SYNCING COMMAND CENTER...</div>}>
        <SettingsContent />
      </Suspense>
    </ErrorBoundary>
  );
}

function SettingsContent() {
  const { token, user, signOut, loading: authLoading } = useAuth();
  const queryClient = useQueryClient();
  const [localSettings, setLocalSettings] = useState<any>(() => ({
    ...DEFAULT_USER_SETTINGS,
  }));
  const [isSaved, setIsSaved] = useState(false);
  const [lastSavedField, setLastSavedField] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const { data: settings, isLoading, error, refetch, failureCount } = useQuery({
    queryKey: ['user-settings'],
    queryFn: async () => {
      const { data } = await api.get('/api/user/settings');
      return data;
    },
    enabled: !!token,
    retry: 2,
    retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 10_000),
    staleTime: 60_000,
  });

  const [settingsLoadSlow, setSettingsLoadSlow] = React.useState(false);
  React.useEffect(() => {
    if (!token || !isLoading) {
      setSettingsLoadSlow(false);
      return;
    }
    const t = window.setTimeout(() => setSettingsLoadSlow(true), 12_000);
    return () => window.clearTimeout(t);
  }, [token, isLoading]);

  React.useEffect(() => {
    if (settings && typeof settings === "object") {
      setLocalSettings(settings);
    }
  }, [settings]);

  const mutation = useMutation({
    mutationFn: async ({ field, value }: { field: string, value: any }) => {
      const { data } = await api.patch('/api/user/settings', { [field]: value });
      return { data, field };
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['user-settings'] });
      setIsSaved(true);
      setLastSavedField(data.field);
      setTimeout(() => {
        setIsSaved(false);
        setLastSavedField(null);
      }, 3000);
    }
  });

  const handleUpdate = (field: string, value: any) => {
    setLocalSettings((prev: any) => ({ ...prev, [field]: value }));
  };

  const handleSaveAll = () => {
    if (!localSettings) return;
    const baseline = settings ?? DEFAULT_USER_SETTINGS;
    let anyChanges = false;
    Object.keys(localSettings).forEach((field) => {
      if (localSettings[field] !== baseline[field]) {
        mutation.mutate({ field, value: localSettings[field] });
        anyChanges = true;
      }
    });
    if (!anyChanges) {
       setIsSaved(true);
       setTimeout(() => setIsSaved(false), 3000);
    }
  };

  const copyToClipboard = (text: string) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (isLoading || authLoading) {
    return (
      <div className="max-w-5xl mx-auto space-y-10 pt-16 px-6">
        {settingsLoadSlow && (
          <div className="rounded-2xl border border-yellow-500/30 bg-yellow-500/10 p-4 text-[10px] font-black uppercase tracking-widest text-yellow-200 space-y-3">
            <p>Settings are taking longer than usual. Check your connection or try again.</p>
            <button
              type="button"
              onClick={() => refetch()}
              className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-[9px] font-black uppercase"
            >
              Retry load
            </button>
          </div>
        )}
        <Skeleton className="h-16 w-80 mb-12" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
           <Skeleton className="h-64 w-full rounded-[2rem]" />
           <Skeleton className="h-64 w-full rounded-[2rem]" />
        </div>
        {failureCount > 0 && (
          <p className="text-[10px] text-textMuted font-bold uppercase tracking-widest">
            Retry attempt {failureCount}…
          </p>
        )}
      </div>
    );
  }

  if (!token && !authLoading) {
    return (
      <div className="max-w-5xl mx-auto pt-32 px-6 text-center space-y-6">
        <h1 className="text-4xl font-black uppercase italic font-display">Authentication Required</h1>
        <p className="text-textMuted uppercase tracking-widest text-[10px] font-black">Please log in to access the Command Center.</p>
        <button 
           onClick={() => window.location.href = "/login"}
           className="px-8 py-4 bg-brand-primary text-white font-black uppercase tracking-widest rounded-xl hover:bg-brand-primary/80 transition-all"
        >
          Return to Base
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto pb-32 space-y-12 pt-16 px-6 text-white">
      {(error || settings === null || settings === undefined) && !isLoading ? (
        <EmptyState
          title="Unable to load settings."
          description="Showing defaults — your changes will still save."
          onRetry={() => refetch()}
        />
      ) : null}
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-8 border-b border-white/5 pb-10">
        <div>
          <div className="flex items-center gap-4 mb-2">
            <div className="bg-brand-primary/10 p-3 rounded-2xl border border-brand-primary/20">
              <Settings size={32} className="text-brand-primary" />
            </div>
            <h1 className="text-5xl font-black italic tracking-tighter uppercase font-display leading-none">
              Command <span className="text-brand-primary">Center</span>
            </h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-[0.2em] italic">Institutional Matrix Compliance v2.1</p>
        </div>
        
        <div className="flex items-center gap-4">
           {isSaved && (
             <motion.div 
               initial={{ opacity: 0, x: 20 }}
               animate={{ opacity: 1, x: 0 }}
               className="flex items-center gap-2 text-brand-success text-[10px] font-black uppercase tracking-widest italic"
             >
               <CheckCircle size={14} /> Matrix Synced
             </motion.div>
           )}
           <button 
             onClick={() => signOut()}
             aria-label="Terminate Session"
             className="px-6 py-3 bg-white/5 hover:bg-red-500/10 border border-white/10 rounded-xl text-[9px] font-black uppercase tracking-widest text-textMuted hover:text-red-400 transition-all font-sans flex items-center gap-2"
           >
             <LogOut size={14} /> Terminate
           </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-12">
        {/* Core Settings */}
        <div className="md:col-span-8 space-y-12">
           
           {/* Section 1: Identity */}
           <SectionContainer 
             title="Identity Matrix" 
             icon={<User size={18} className="text-brand-primary" />}
             description="Verified authentication profile."
           >
              <div className="bg-white/5 border border-white/5 rounded-[2rem] p-6 flex flex-col sm:flex-row items-center gap-6">
                <div className="w-20 h-20 bg-brand-primary/10 rounded-2xl border border-brand-primary/20 flex items-center justify-center text-3xl font-black text-brand-primary italic">
                  {user?.email?.[0]?.toUpperCase() || "?"}
                </div>
                <div className="flex-1 space-y-1 text-center sm:text-left">
                  <div className="text-[9px] font-black text-textMuted uppercase tracking-[0.2em] leading-none mb-1">Authenticated Terminal</div>
                  <div className="text-xl font-black text-white leading-tight uppercase font-display">{user?.email}</div>
                  <div className="flex justify-center sm:justify-start gap-2 pt-1">
                    <span className="text-[8px] px-2 py-0.5 bg-brand-primary/20 text-brand-primary rounded border border-brand-primary/30 font-black uppercase tracking-widest leading-none">
                      {(settings?.tier as string) || (localSettings?.tier as string) || "Free"} ACCESS
                    </span>
                    <span className="text-[8px] px-2 py-0.5 bg-brand-success/20 text-brand-success rounded border border-brand-success/30 font-black uppercase tracking-widest leading-none">
                      SECURED
                    </span>
                  </div>
                </div>
                <div className="text-[8px] font-black text-textMuted uppercase italic sm:max-w-[120px] text-center opacity-50 px-4">
                  Email is locked to current session and cannot be modified inline.
                </div>
              </div>
           </SectionContainer>

           {/* Section 2: Core Platform Config (6 Fields) */}
           <SectionContainer 
             title="Logistical Infrastructure" 
             icon={<Monitor size={18} className="text-brand-cyan" />}
             description="Primary dashboard behavior overrides."
           >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Field 1: Unit Size */}
                  <InputRow 
                    label="Bet Unit Size" 
                    icon={<DollarSign size={14} />}
                    description="Standard sizing for parlay math"
                    value={localSettings?.unit_size ?? settings?.unit_size ?? 100}
                    type="number"
                    onChange={(val: string) => handleUpdate("unit_size", parseFloat(val))}
                    isSaving={mutation.isPending && lastSavedField === "unit_size"}
                    isSaved={isSaved && lastSavedField === "unit_size"}
                  />

                  {/* Field 2: Default Sport */}
                  <SelectRow 
                    label="Primary Sport" 
                    icon={<Globe size={14} />}
                    description="Dashboard focus on boot"
                    value={localSettings?.default_sport ?? settings?.default_sport ?? "basketball_nba"}
                    options={Object.keys(SPORTS_CONFIG).map(k => ({
                      value: k,
                      label: (SPORTS_CONFIG[k as SportKey] as any).label
                    }))}
                    onChange={(val: any) => handleUpdate("default_sport", val)}
                    isSaving={mutation.isPending && lastSavedField === "default_sport"}
                    isSaved={isSaved && lastSavedField === "default_sport"}
                  />

                  {/* Field 3: Default Sportsbook */}
                  <SelectRow 
                    label="Primary Sportsbook" 
                    icon={<Database size={14} />}
                    description="Preferred pricing source"
                    value={localSettings?.default_sportsbook ?? settings?.default_sportsbook ?? "draftkings"}
                    options={[
                      { value: "draftkings", label: "DraftKings" },
                      { value: "fanduel", label: "FanDuel" },
                      { value: "betmgm", label: "BetMGM" },
                      { value: "pinnacle", label: "Pinnacle" },
                      { value: "caesars", label: "Caesars" },
                      { value: "bet365", label: "Bet365" },
                      { value: "bovada", label: "Bovada" },
                    ]}
                    onChange={(val: any) => handleUpdate("default_sportsbook", val)}
                    isSaving={mutation.isPending && lastSavedField === "default_sportsbook"}
                    isSaved={isSaved && lastSavedField === "default_sportsbook"}
                  />

                  {/* Field 4: Theme Mode */}
                  <SelectRow 
                    label="Interface Matrix" 
                    icon={<Monitor size={14} />}
                    description="Visual rendering protocol"
                    value={localSettings?.theme ?? settings?.theme ?? "dark"}
                    options={[
                      { value: "dark", label: "Neural Dark" },
                      { value: "light", label: "High Contrast Light" },
                    ]}
                    onChange={(val: any) => handleUpdate("theme", val)}
                    isSaving={mutation.isPending && lastSavedField === "theme"}
                    isSaved={isSaved && lastSavedField === "theme"}
                  />

                  {/* Field 5: Notifications */}
                  <ToggleRow 
                    label="Direct Relay" 
                    icon={<Bell size={14} />}
                    description="Mobile signal push protocol" 
                    active={localSettings?.notifications_enabled ?? settings?.notifications_enabled} 
                    onToggle={() => handleUpdate("notifications_enabled", !(localSettings?.notifications_enabled ?? settings?.notifications_enabled))}
                    isSaving={mutation.isPending && lastSavedField === "notifications_enabled"}
                    isSaved={isSaved && lastSavedField === "notifications_enabled"}
                  />

                  {/* Field 6: Data Grid (Extra) */}
                  <ToggleRow 
                    label="API Grid Access" 
                    icon={<Key size={14} />}
                    description="Enable raw intelligence keys" 
                    active={localSettings?.api_enabled ?? settings?.api_enabled} 
                    onToggle={() => handleUpdate("api_enabled", !(localSettings?.api_enabled ?? settings?.api_enabled))}
                    isSaving={mutation.isPending && lastSavedField === "api_enabled"}
                    isSaved={isSaved && lastSavedField === "api_enabled"}
                  />
              </div>
              <div className="mt-8">
                 <button 
                    onClick={handleSaveAll}
                    disabled={mutation.isPending}
                    className="w-full py-4 bg-brand-primary text-white font-black uppercase tracking-widest text-xs rounded-2xl hover:bg-brand-primary-hover hover:scale-[1.01] transition-all shadow-glow shadow-brand-primary/20 flex flex-col items-center justify-center gap-1"
                 >
                    <span>{mutation.isPending ? "Syncing..." : "Save Configuration"}</span>
                 </button>
              </div>
           </SectionContainer>
        </div>

        {/* Sidebar Settings */}
        <div className="md:col-span-4 space-y-12">
            
            {/* Access Tokens */}
            <div className="bg-lucrix-surface border border-white/10 rounded-[2.5rem] p-8 space-y-8">
              <div className="flex items-center gap-3">
                 <div className="p-2 bg-brand-primary/10 rounded-xl text-brand-primary">
                    <Key size={20} />
                 </div>
                 <h3 className="text-[10px] font-black uppercase tracking-widest">Access Tokens</h3>
              </div>
              <div className="space-y-6">
                 <div>
                    <label className="text-[8px] font-black text-textMuted uppercase tracking-widest mb-3 block italic">Production RSA Key</label>
                    <div className="flex items-center gap-2 bg-lucrix-dark/50 border border-white/5 rounded-xl p-3">
                       <input 
                         type="password" 
                         readOnly 
                         id="rsa-key-input"
                         aria-label="Production RSA Key"
                         value={settings?.api_key || "px_edge_*******************"}
                         className="bg-transparent border-none text-[10px] text-white outline-none w-full font-mono"
                       />
                       <button 
                         onClick={() => copyToClipboard(settings?.api_key || "")} 
                         aria-label="Copy API Key"
                         className="p-2 text-textMuted hover:text-brand-primary transition-colors"
                       >
                          {copied ? <CheckCircle size={16} className="text-brand-success" /> : <Copy size={16} />}
                       </button>
                    </div>
                 </div>
                 <button 
                   aria-label="Re-Generate RSA Key"
                   className="w-full py-4 bg-brand-primary/10 border border-brand-primary/20 text-brand-primary font-black uppercase tracking-widest text-[9px] rounded-xl hover:bg-brand-primary hover:text-white transition-all"
                 >
                   <RefreshCw size={14} className="inline mr-2 mb-0.5" /> Re-Generate RSA
                 </button>
              </div>
            </div>

            {/* Danger Zone */}
            <div className="bg-red-500/5 border border-red-500/10 rounded-[2.5rem] p-8 space-y-8">
               <div className="flex items-center gap-3">
                  <div className="p-2 bg-red-500/10 rounded-xl text-red-500">
                     <AlertTriangle size={20} />
                  </div>
                  <h3 className="text-[10px] font-black uppercase tracking-widest text-red-500">Clearance Level 5</h3>
               </div>
               <div className="space-y-3">
                  <button 
                    aria-label="Flush History"
                    className="w-full py-4 px-5 bg-white/5 border border-white/5 rounded-xl flex items-center justify-between group hover:bg-red-500/10 transition-all"
                  >
                     <div className="text-left">
                        <div className="text-[10px] font-black text-white uppercase mb-0.5">Flush History</div>
                        <div className="text-[8px] font-bold text-textMuted uppercase italic">Clear Intelligence Buffer</div>
                     </div>
                     <RefreshCw size={14} className="text-textMuted group-hover:rotate-180 transition-all duration-700" />
                  </button>
                  <button 
                    aria-label="Deactivate Matrix"
                    className="w-full py-4 px-5 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center justify-between group hover:bg-red-500 hover:text-white transition-all"
                  >
                     <div className="text-left">
                        <div className="text-[10px] font-black uppercase mb-0.5">Deactivate Matrix</div>
                        <div className="text-[8px] font-bold uppercase opacity-60">Permanently Remove Data</div>
                     </div>
                     <Trash2 size={14} />
                  </button>
               </div>
            </div>
        </div>
      </div>
    </div>
  );
}

function SectionContainer({ title, icon, description, children }: any) {
  return (
    <div className="space-y-6">
       <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-3">
             {icon}
             <h2 className="text-xs font-black text-white uppercase tracking-[0.2em]">{title}</h2>
          </div>
          <span className="text-[8px] font-black text-textMuted uppercase tracking-widest italic">{description}</span>
       </div>
       {children}
    </div>
  );
}

function InputRow({ label, description, icon, value, onChange, type = "text", isSaved, isSaving }: any) {
  return (
    <div className="bg-white/5 border border-white/5 rounded-2xl p-5 flex flex-col gap-3 group hover:border-brand-primary/30 transition-all">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="text-brand-primary">{icon}</div>
          <div className="text-[10px] font-black text-white uppercase tracking-widest italic">{label}</div>
        </div>
        {isSaved && <span className="text-[9px] font-black text-brand-success uppercase italic">Saved ✓</span>}
      </div>
      <input 
        type={type}
        value={value}
        aria-label={label}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-lucrix-dark/50 border border-white/10 rounded-xl p-3 text-xs text-white outline-none focus:border-brand-primary/50 transition-all font-sans"
      />
      <div className="text-[8px] font-bold text-textMuted uppercase leading-none px-1 italic">{description}</div>
    </div>
  );
}

function SelectRow({ label, description, icon, value, options, onChange, isSaved, isSaving }: any) {
  return (
    <div className="bg-white/5 border border-white/5 rounded-2xl p-5 flex flex-col gap-3 group hover:border-brand-primary/30 transition-all">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="text-brand-cyan">{icon}</div>
          <div className="text-[10px] font-black text-white uppercase tracking-widest italic">{label}</div>
        </div>
        {isSaved && <span className="text-[9px] font-black text-brand-success uppercase italic">Saved ✓</span>}
      </div>
      <div className="relative">
        <select 
          value={value}
          aria-label={label}
          onChange={(e) => onChange(e.target.value)}
          className="w-full bg-lucrix-dark/50 border border-white/10 rounded-xl p-3 px-4 text-xs text-white appearance-none outline-none focus:border-brand-cyan/50 transition-all font-sans"
        >
          {options.map((opt: any) => (
            <option key={opt.value} value={opt.value} className="bg-lucrix-dark">{opt.label}</option>
          ))}
        </select>
        <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-textMuted pointer-events-none" />
      </div>
      <div className="text-[8px] font-bold text-textMuted uppercase leading-none px-1 italic">{description}</div>
    </div>
  );
}

function ToggleRow({ label, description, icon, active, onToggle, disabled, isSaved, isSaving }: any) {
  return (
    <div className={clsx(
      "bg-white/5 border border-white/5 rounded-2xl p-5 flex items-center justify-between group hover:border-brand-primary/20 transition-all relative overflow-hidden",
      disabled && "opacity-50 cursor-not-allowed"
    )}>
      <div className="flex items-center gap-4">
        <div className={clsx(active ? "text-brand-primary" : "text-textMuted")}>{icon}</div>
        <div>
          <div className="text-[10px] font-black text-white uppercase tracking-widest mb-1 italic flex items-center gap-2">
            {label}
            {isSaved && <span className="text-[9px] font-black text-brand-success uppercase italic">Saved ✓</span>}
          </div>
          <div className="text-[8px] font-bold text-textMuted uppercase leading-none">{description}</div>
        </div>
      </div>
      <button 
        onClick={onToggle}
        disabled={disabled}
        aria-label={`Toggle ${label}`}
        className={clsx(
          "w-10 h-5 rounded-full relative transition-all duration-300 p-0.5 flex items-center",
          active ? "bg-brand-primary shadow-glow shadow-brand-primary/20" : "bg-white/10 border border-white/10"
        )}
      >
        <div className={clsx(
          "w-4 h-4 rounded-full bg-white transition-all shadow-md",
          active ? "translate-x-5" : "translate-x-0 opacity-40"
        )} />
      </button>
    </div>
  );
}
