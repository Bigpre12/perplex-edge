'use client';

import React from 'react';
import { useLiveGames, LiveGame } from '@/hooks/useLiveGames';
import { LoadingSkeleton } from '@/components/shared/LoadingSkeleton';
import { ErrorRetry } from '@/components/shared/ErrorRetry';
import { Radio, Clock, Trophy, Activity, Zap } from 'lucide-react';
import { clsx } from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';

export default function LivePage() {
  const { data: games, isLoading, isError, refetch, socketStatus } = useLiveGames() as any;

  const statusMap = {
    connecting: { color: 'text-yellow-400', bg: 'bg-yellow-400/10', label: 'Syncing...' },
    open: { color: 'text-emerald-400', bg: 'bg-emerald-400/10', label: 'Real-time Active' },
    closed: { color: 'text-red-400', bg: 'bg-red-400/10', label: 'Offline (Polling Fallback)' }
  };

  const currentStatus = statusMap[socketStatus as keyof typeof statusMap] || statusMap.closed;

  const ScoreBoard = ({ game, index }: { game: LiveGame, index: number }) => {
    const sportName = (game.sport || 'UNKNOWN').replace('_', ' ').toUpperCase();
    const home_team = game.home_team || (game.matchup?.split(' @ ')[1]) || 'Home';
    const away_team = game.away_team || (game.matchup?.split(' @ ')[0]) || 'Away';
    
    return (
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.05 }}
        className="bg-lucrix-surface border border-white/10 rounded-[2.25rem] p-8 transition-all hover:border-brand-primary/30 group relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-32 h-32 -mr-16 -mt-16 bg-brand-primary/5 rounded-full blur-3xl" />
        
        <div className="flex items-center justify-between mb-8 relative z-10">
          <div className="flex items-center space-x-3">
             <div className="bg-brand-primary/10 p-1.5 rounded-lg border border-brand-primary/20">
                <Radio className="w-3.5 h-3.5 animate-pulse text-brand-primary" />
             </div>
             <span className="text-[10px] font-black uppercase tracking-[0.2em] text-brand-primary italic">Live {sportName}</span>
          </div>
          <div className="flex items-center space-x-2 text-textMuted bg-white/5 px-3 py-1 rounded-full border border-white/5">
             <Clock className="w-3 h-3" />
             <span className="text-[10px] font-black uppercase tracking-widest">{game.period} {game.clock}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-10 items-center mb-10 relative z-10">
          <div className="flex flex-col items-center group/team">
             <div className="w-20 h-20 rounded-3xl bg-lucrix-dark border border-white/10 mb-6 flex items-center justify-center text-2xl font-black italic text-white transition-all group-hover/team:scale-110 group-hover/team:border-brand-primary/50 group-hover/team:shadow-glow group-hover/team:shadow-brand-primary/10">
                {home_team.charAt(0)}
             </div>
             <span className="text-xs font-black uppercase tracking-tight text-center h-8 line-clamp-2 leading-tight max-w-[120px] mb-2">{home_team}</span>
             <span className="text-5xl font-black italic tracking-tighter text-white drop-shadow-lg">{game.home_score ?? 0}</span>
          </div>
          
          <div className="flex flex-col items-center group/team">
             <div className="w-20 h-20 rounded-3xl bg-lucrix-dark border border-white/10 mb-6 flex items-center justify-center text-2xl font-black italic text-white transition-all group-hover/team:scale-110 group-hover/team:border-brand-primary/50 group-hover/team:shadow-glow group-hover/team:shadow-brand-primary/10">
                {away_team.charAt(0)}
             </div>
             <span className="text-xs font-black uppercase tracking-tight text-center h-8 line-clamp-2 leading-tight max-w-[120px] mb-2">{away_team}</span>
             <span className="text-5xl font-black italic tracking-tighter text-white drop-shadow-lg">{game.away_score ?? 0}</span>
          </div>
        </div>

        <div className="relative h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
           <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer" />
            <motion.div 
              className="h-full bg-brand-primary shadow-glow shadow-brand-primary/50" 
              initial={{ width: 0 }}
              animate={{ width: '45%' }}
            />
        </div>
      </motion.div>
    );
  };

  return (
    <div className="pb-32 space-y-12 pt-12 px-8 max-w-[1500px] mx-auto text-white">
      {/* Dynamic Header */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 border-b border-white/10 pb-12">
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-brand-primary/10 border border-brand-primary/20 rounded-2xl text-brand-primary shadow-glow shadow-brand-primary/20">
              <Activity size={32} />
            </div>
            <h1 className="text-7xl font-black tracking-tighter uppercase italic leading-[0.8] font-display">
              Live <span className="text-brand-primary">Systems</span>
            </h1>
          </div>
          <p className="text-textSecondary font-bold text-sm max-w-xl italic opacity-70">
            Real-time scoring and state updates across all tracked leagues. 
            Institutional data stream active with sub-second latency.
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row items-center gap-4">
           <div className={clsx(
             "px-6 py-3 rounded-2xl border transition-all duration-500 backdrop-blur-md flex items-center space-x-3 shadow-lg",
             currentStatus.bg,
             currentStatus.color.replace('text-', 'border-').replace('400', '400/20')
           )}>
              <div className={clsx("w-2 h-2 rounded-full animate-pulse shadow-glow shadow-current", currentStatus.color.replace('text-', 'bg-'))} />
              <span className={clsx("text-[10px] font-black uppercase tracking-[0.2em]", currentStatus.color)}>{currentStatus.label}</span>
           </div>
           
           <button 
              onClick={() => refetch()}
              className="px-6 py-3 bg-white/5 border border-white/10 rounded-2xl text-[10px] font-black uppercase tracking-widest text-textMuted hover:text-white hover:bg-white/10 transition-all"
           >
             Manual Sync
           </button>
        </div>
      </div>

      {/* Main Content Area */}
      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div 
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10"
          >
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-[400px] bg-white/5 rounded-[2.5rem] p-8 animate-pulse">
                  <div className="flex justify-between mb-8">
                     <div className="h-4 w-24 bg-white/10 rounded-full" />
                     <div className="h-4 w-16 bg-white/10 rounded-full" />
                  </div>
                  <div className="grid grid-cols-2 gap-10 mt-12">
                     <div className="flex flex-col items-center gap-4">
                        <div className="w-20 h-20 bg-white/10 rounded-3xl" />
                        <div className="h-4 w-16 bg-white/10 rounded-full" />
                     </div>
                     <div className="flex flex-col items-center gap-4">
                        <div className="w-20 h-20 bg-white/10 rounded-3xl" />
                        <div className="h-4 w-16 bg-white/10 rounded-full" />
                     </div>
                  </div>
              </div>
            ))}
          </motion.div>
        ) : isError ? (
          <motion.div 
            key="error"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="max-w-md mx-auto py-32"
          >
            <ErrorRetry onRetry={() => refetch()} />
          </motion.div>
        ) : !games || games.length === 0 ? (
          <motion.div 
            key="empty"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center justify-center py-48 space-y-8 bg-white/5 rounded-[3rem] border border-dashed border-white/10"
          >
             <div className="p-8 bg-white/5 rounded-full relative">
                <Trophy className="w-24 h-24 text-textMuted opacity-20" />
                <Zap size={32} className="absolute -top-2 -right-2 text-brand-primary animate-pulse" />
             </div>
             <div className="text-center">
                <p className="text-2xl font-black italic uppercase tracking-tighter text-white mb-2 leading-none">Market Neutral</p>
                <p className="text-xs font-bold text-textMuted uppercase tracking-widest italic">No active games in the high-liquidity tracking window.</p>
             </div>
          </motion.div>
        ) : (
          <motion.div 
            key="content"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10"
          >
             {games.map((game: any, i: number) => (
                <ScoreBoard key={game.id} game={game} index={i} />
             ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
