'use client';

import React from 'react';
import { useLiveGames, LiveGame } from '@/hooks/useLiveGames';
import { LoadingSkeleton } from '@/components/shared/LoadingSkeleton';
import { ErrorRetry } from '@/components/shared/ErrorRetry';
import { Radio, Clock, Trophy } from 'lucide-react';

export default function LivePage() {
  const { data: games, isLoading, isError, refetch } = useLiveGames();

  const ScoreBoard = ({ game }: { game: LiveGame }) => {
    // Safely extract names/sports to prevent UI crash from broken live data points
    const sportName = (game.sport || 'UNKNOWN').replace('_', ' ').toUpperCase();
    const homeTeamInitial = (game.home_team || 'H').substring(0, 1);
    const awayTeamInitial = (game.away_team || 'A').substring(0, 1);

    return (
    <div className="bg-white/5 border border-white/10 rounded-3xl p-6 transition-all hover:bg-white/10 group">
       <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2 text-[10px] font-black uppercase tracking-widest text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
             <Radio className="w-3 h-3 animate-pulse" />
             <span>Live {sportName}</span>
          </div>
          <div className="flex items-center space-x-1 text-white/30 text-xs font-mono">
             <Clock className="w-3 h-3" />
             <span>{game.period} {game.clock}</span>
          </div>
       </div>

       <div className="grid grid-cols-2 gap-4 items-center mb-6">
          <div className="flex flex-col items-center">
             <div className="w-16 h-16 rounded-2xl bg-white/5 mb-3 flex items-center justify-center text-xl font-bold border border-white/5 group-hover:scale-105 transition-transform">
                {homeTeamInitial}
             </div>
             <span className="text-sm font-bold text-center h-10 overflow-hidden line-clamp-2">{game.home_team || 'Unknown'}</span>
             <span className="text-4xl font-black mt-2 text-white">{game.score_home || 0}</span>
          </div>
          <div className="flex flex-col items-center">
             <div className="w-16 h-16 rounded-2xl bg-white/5 mb-3 flex items-center justify-center text-xl font-bold border border-white/5 group-hover:scale-105 transition-transform">
                {awayTeamInitial}
             </div>
             <span className="text-sm font-bold text-center h-10 overflow-hidden line-clamp-2">{game.away_team || 'Unknown'}</span>
             <span className="text-4xl font-black mt-2 text-white">{game.score_away || 0}</span>
          </div>
       </div>

       <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
          <div className="h-full bg-blue-500 w-1/3 animate-progress" />
       </div>
    </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 pb-24">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex justify-between items-end">
          <div className="space-y-2">
            <h1 className="text-6xl font-black tracking-tighter uppercase leading-[0.8] mb-4">
              <span className="text-blue-500">LIVE</span> ACTION
            </h1>
            <p className="text-white/40 max-w-md">
              Real-time scoring and state updates across all tracked leagues.
              Polling every <span className="text-blue-400 font-mono">15s</span>.
            </p>
          </div>
          
          <div className="hidden md:flex space-x-2">
             <div className="px-4 py-2 rounded-full border border-white/10 bg-white/5 flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-[10px] font-black uppercase tracking-widest text-white/60">Systems Active</span>
             </div>
          </div>
        </div>

        {/* Dynamic Content */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <LoadingSkeleton rows={3} />
          </div>
        ) : isError ? (
          <ErrorRetry onRetry={() => refetch()} />
        ) : !games || games.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 space-y-4 opacity-30">
             <Trophy className="w-16 h-16" />
             <p className="text-xl font-bold uppercase tracking-widest">No Active Games</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
             {games.map((game) => (
                <ScoreBoard key={game.id} game={game} />
             ))}
          </div>
        )}
      </div>
    </div>
  );
}
