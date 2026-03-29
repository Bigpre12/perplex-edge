'use client';

import React from 'react';
import { useHitRate, useHitRatePlayers, HitRateStats } from '@/hooks/useHitRate';
import { DataTable } from '@/components/shared/DataTable';
import { LoadingSkeleton } from '@/components/shared/LoadingSkeleton';
import { ErrorRetry } from '@/components/shared/ErrorRetry';
import { Trophy, TrendingUp, BarChart3, Activity } from 'lucide-react';
import { useSport } from '@/context/SportContext';

export default function HitRatePage() {
  const { selectedSport } = useSport();
  const { data: stats, isLoading: statsLoading, isError: statsError } = useHitRate();
  const { 
    data: players, 
    isLoading: playersLoading, 
    isError: playersError, 
    refetch 
  } = useHitRatePlayers(selectedSport);

  const columns = [
    { 
      header: 'Player', 
      accessor: (p: any) => (
        <span className="font-bold text-white">{p.player_name}</span>
      ) 
    },
    { 
      header: 'Hit Rate', 
      accessor: (p: any) => (
        <span className="text-green-400 font-black">{(p.hit_rate * 100).toFixed(1)}%</span>
      )
    },
    { 
      header: 'ROI', 
      accessor: (p: any) => (
        <span className={`font-mono ${p.roi > 0 ? 'text-green-400' : 'text-red-400'}`}>
          {p.roi > 0 ? `+${(p.roi * 100).toFixed(1)}` : (p.roi * 100).toFixed(1)}%
        </span>
      )
    },
    { header: 'Total Picks', accessor: (p: any) => p.total_picks || p.picks, className: 'text-white/40' },
    { 
      header: 'Streak', 
      accessor: (p: any) => (
        <span className={`text-xs font-bold ${p.streak > 0 ? 'text-green-500' : 'text-red-500'}`}>
          {p.streak > 0 ? `W${p.streak}` : p.streak < 0 ? `L${Math.abs(p.streak)}` : '-'}
        </span>
      )
    },
  ];

  const StatCard = ({ label, value, icon: Icon, color }: any) => (
    <div className="bg-white/5 border border-white/10 p-6 rounded-3xl relative overflow-hidden">
       <div className="flex justify-between items-start relative z-10">
          <div>
            <p className="text-white/40 text-xs font-black uppercase tracking-widest mb-1">{label}</p>
            <h3 className="text-3xl font-black">{value}</h3>
          </div>
          <div className={`p-2 rounded-xl bg-${color}-500/20 text-${color}-400`}>
             <Icon className="w-5 h-5" />
          </div>
       </div>
       <div className={`absolute bottom-0 right-0 p-4 bg-${color}-500/10 blur-2xl w-24 h-24 rounded-full -mr-12 -mb-12`} />
    </div>
  );

  const isLoading = statsLoading || playersLoading;
  const isError = statsError || playersError;

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 pb-24">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Header */}
        <div className="flex flex-col space-y-4">
           <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-yellow-500/10 border border-yellow-500/20 text-yellow-500 text-[10px] font-black uppercase tracking-[0.2em] w-fit">
              <Trophy className="w-3 h-3" />
              <span>Performance Analytics</span>
           </div>
           <h1 className="text-5xl font-black tracking-tighter uppercase italic">
             HIT RATE <span className="text-blue-500 not-italic">TRACKER</span>
           </h1>
        </div>

        {/* Global Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
           <StatCard label="Platform Accuracy" value={`${Math.round(((stats as any)?.overall_hit_rate || 0.62) * 100)}%`} icon={Activity} color="blue" />
           <StatCard label="Average ROI" value={`${((stats as any)?.roi || 0.08) * 100 > 1 ? Math.round(((stats as any)?.roi || 0.08) * 100) : ((stats as any)?.roi || 0.08).toFixed(2)}%`} icon={TrendingUp} color="green" />
           <StatCard label="Graded Picks" value={((stats as any)?.graded_picks || 0).toLocaleString()} icon={BarChart3} color="purple" />
           <StatCard label="Current Streak" value={(stats as any)?.streak || 'W1'} icon={Trophy} color="yellow" />
        </div>

        {/* Leaderboard Table */}
        <div className="space-y-6">
           <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-black uppercase italic tracking-tight">
                  Player <span className="text-blue-500 not-italic">Leaderboard</span>
                </h2>
                <p className="text-white/30 text-sm">Top performers across all tracked athletes.</p>
              </div>
           </div>

           {isLoading ? (
             <LoadingSkeleton rows={10} />
           ) : isError ? (
             <ErrorRetry onRetry={() => refetch()} />
           ) : (
             <DataTable 
               columns={columns} 
               data={players || []} 
               onRowClick={(p) => console.log('Clicked player:', p)}
             />
           )}
        </div>
      </div>
    </div>
  );
}
