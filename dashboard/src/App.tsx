import { useState, useEffect } from 'react'
import {
  Activity,
  Brain,
  Cpu,
  TrendingUp,
  ShieldCheck,
  RefreshCw,
  LayoutDashboard,
  Zap,
  ArrowRight
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

import { useBrainData } from './hooks/useBrainData'

// Utility for Tailwind class merging
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const { decisions, health, loading, refetch } = useBrainData()
  const [lastCheck, setLastCheck] = useState(new Date().toLocaleTimeString())

  // Dynamic heartbeat time
  useEffect(() => {
    if (health) {
      setLastCheck(new Date().toLocaleTimeString())
    }
  }, [health])

  const currentDecision = decisions.length > 0 ? decisions[0] : null

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-slate-200">
      {/* Sidebar */}
      <aside className="w-64 glass border-r border-white/5 flex flex-col p-4 z-20">
        <div className="flex items-center gap-3 px-2 mb-8">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center glow-emerald">
            <Zap className="text-white fill-white" size={24} />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-tight">Perplex Edge</h1>
            <span className="text-[10px] text-primary font-mono uppercase tracking-widest">Command Center</span>
          </div>
        </div>

        <nav className="flex-1 space-y-1">
          <NavItem
            icon={<LayoutDashboard size={20} />}
            label="Dashboard"
            active={activeTab === 'dashboard'}
            onClick={() => setActiveTab('dashboard')}
          />
          <NavItem
            icon={<Brain size={20} />}
            label="AI Decisions"
            active={activeTab === 'decisions'}
            onClick={() => setActiveTab('decisions')}
          />
          <NavItem
            icon={<TrendingUp size={20} />}
            label="Monte Carlo"
            active={activeTab === 'monte-carlo'}
            onClick={() => setActiveTab('monte-carlo')}
          />
          <NavItem
            icon={<ShieldCheck size={20} />}
            label="System SRE"
            active={activeTab === 'sre'}
            onClick={() => setActiveTab('sre')}
          />
        </nav>

        {/* System Heartbeat Widget */}
        <div className="mt-auto p-4 rounded-2xl glass-emerald glow-emerald">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Cpu size={16} className="text-primary animate-pulse" />
              <span className="text-xs font-medium text-emerald-400">Auto-Healing</span>
            </div>
            <div className={cn(
              "w-2 h-2 rounded-full",
              health ? "bg-primary animate-pulse" : "bg-slate-500"
            )} />
          </div>
          <div className="text-[10px] text-emerald-400/60 font-mono">
            STATUS: {health?.status.toUpperCase() || 'IDLE'}
            <br />
            LAST_CYCLE: {lastCheck}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8 relative">
        {/* Background Gradients */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-secondary/10 blur-[120px] rounded-full pointer-events-none -z-10" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-primary/5 blur-[120px] rounded-full pointer-events-none -z-10" />

        <header className="flex items-center justify-between mb-10">
          <div>
            <h2 className="text-3xl font-bold tracking-tight mb-1">Intelligence Feed</h2>
            <p className="text-slate-400 text-sm">Real-time betting edges and system signals.</p>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={refetch}
              className="flex items-center gap-2 px-4 py-2 rounded-xl glass hover:bg-white/5 transition-all text-sm font-medium"
            >
              <RefreshCw size={16} className={cn("text-slate-400", loading && "animate-spin")} />
              Sync Data
            </button>
            <div className="w-10 h-10 rounded-full glass border border-white/10 flex items-center justify-center">
              <div className="w-2 h-2 rounded-full bg-primary" />
            </div>
          </div>
        </header>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-12 gap-6">
          {/* AI Decision Card (Large) */}
          <div className="col-span-8 p-6 rounded-3xl glass relative overflow-hidden group min-h-[300px]">
            <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
              <Brain size={120} />
            </div>

            {loading && !currentDecision ? (
              <div className="space-y-4 animate-pulse">
                <div className="h-4 w-32 bg-white/5 rounded" />
                <div className="h-8 w-64 bg-white/5 rounded" />
                <div className="h-20 w-full bg-white/5 rounded" />
              </div>
            ) : currentDecision ? (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative z-10"
              >
                <div className="flex items-center gap-2 mb-4">
                  <span className="bg-primary/20 text-primary text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider">
                    Live Recommendation
                  </span>
                  <span className="text-slate-500 text-[10px] font-mono">ID: {currentDecision.action.slice(-8).toUpperCase()}</span>
                </div>
                <h3 className="text-2xl font-bold mb-4">
                  {currentDecision.details.player_name}{' '}
                  <span className="text-primary">{currentDecision.details.side.toUpperCase()}</span>{' '}
                  {currentDecision.details.line_value} {currentDecision.details.stat_type}
                </h3>
                <p className="text-slate-400 text-sm leading-relaxed max-w-xl mb-6">
                  {currentDecision.reasoning}
                </p>
                <div className="flex gap-8">
                  <StatItem label="Hit Rate" value={`${(currentDecision.details.confidence * 100).toFixed(1)}%`} color="text-primary" />
                  <StatItem label="Market Edge" value={`+${(currentDecision.details.edge * 100).toFixed(1)}%`} color="text-primary" />
                  <StatItem label="Confidence" value={currentDecision.details.confidence > 0.6 ? 'High' : 'Fair'} color="text-primary" />
                </div>
              </motion.div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-slate-500">
                <Brain size={48} className="mb-4 opacity-20" />
                <p>No active recommendations found.</p>
              </div>
            )}
          </div>

          {/* Stats Column */}
          <div className="col-span-4 space-y-6">
            <div className="p-6 rounded-3xl glass h-full flex flex-col">
              <h4 className="flex items-center gap-2 text-sm font-semibold mb-4 text-secondary">
                <TrendingUp size={16} />
                Market Volatility
              </h4>
              <div className="flex-1 flex items-end gap-1.5 px-2 mb-4">
                {[40, 60, 45, 90, 65, 80, 55, 70, 95, 60, 45, 80].map((h, i) => (
                  <motion.div
                    key={i}
                    initial={{ scaleY: 0 }}
                    animate={{ scaleY: 1 }}
                    style={{ height: `${h}%`, transformOrigin: 'bottom' }}
                    className="flex-1 bg-gradient-to-t from-secondary/40 to-secondary/10 rounded-t-sm"
                  />
                ))}
              </div>
              <div className="mt-auto flex justify-between items-center text-[10px] text-slate-500 font-mono">
                <span>00:00</span>
                <span className="text-secondary/60">LIVE VOLUME</span>
                <span>NOW</span>
              </div>
            </div>
          </div>

          {/* SRE Agent Status */}
          <div className="col-span-12 grid grid-cols-3 gap-6">
            <div className="p-6 rounded-3xl glass border border-white/5 flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                <Activity size={24} />
              </div>
              <div>
                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">API Latency</p>
                <p className="text-xl font-bold">12ms</p>
              </div>
            </div>
            <div className="p-6 rounded-3xl glass border border-white/5 flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center text-emerald-400">
                <Cpu size={24} />
              </div>
              <div>
                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">Node Load</p>
                <p className="text-xl font-bold">{health ? (health.system_metrics_evaluated.cpu_usage * 100).toFixed(1) : '0'}%</p>
              </div>
            </div>
            <div className="p-6 rounded-3xl glass border border-white/5 flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-red-500/10 flex items-center justify-center text-red-400">
                <ShieldCheck size={24} />
              </div>
              <div>
                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">Security Filter</p>
                <p className="text-xl font-bold">Active</p>
              </div>
            </div>
          </div>

          {/* Recent Signals Feed */}
          <div className="col-span-12">
            <div className="flex items-center justify-between mb-4 px-2">
              <h3 className="text-lg font-bold">Live Intelligence Signals</h3>
              <span className="text-xs text-slate-500">Auto-refresh active</span>
            </div>
            <div className="space-y-3">
              <AnimatePresence mode="popLayout">
                {decisions.slice(1).map((dec, i) => (
                  <motion.div
                    key={dec.action + i}
                    layout
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="p-4 rounded-2xl glass hover:bg-white/[0.04] transition-all flex items-center justify-between group cursor-pointer"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-xl glass flex items-center justify-center group-hover:bg-primary/10 transition-colors">
                        <TrendingUp size={18} className="text-slate-400 group-hover:text-primary transition-colors" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">
                          Market Edge: {dec.details.player_name} {dec.details.side.toUpperCase()}
                        </p>
                        <span className="text-[10px] text-slate-500 font-mono">Detected by Brain • Edge +{(dec.details.edge * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 pr-2">
                      <div className="text-right mr-4">
                        <p className="text-xs font-mono text-primary">{(dec.details.confidence * 100).toFixed(0)}% HITV</p>
                      </div>
                      <ArrowRight size={16} className="text-slate-600 group-hover:text-primary transition-all group-hover:translate-x-1" />
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function NavItem({ icon, label, active, onClick }: { icon: React.ReactNode, label: string, active: boolean, onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-sm font-medium",
        active
          ? "bg-white/5 text-primary"
          : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.03]"
      )}
    >
      {icon}
      {label}
    </button>
  )
}

function StatItem({ label, value, color }: { label: string, value: string, color: string }) {
  return (
    <div>
      <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">{label}</p>
      <p className={cn("text-xl font-bold", color)}>{value}</p>
    </div>
  )
}
