'use client';

import React from 'react';
import { useSharpMoney, SharpAlert } from '@/hooks/useSharpMoney';
import { DataTable } from '@/components/shared/DataTable';
import { LoadingSkeleton } from '@/components/shared/LoadingSkeleton';
import { ErrorRetry } from '@/components/shared/ErrorRetry';
import { Flame, Anchor, TrendingUp, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function SharpPage() {
  const { data: alerts, isLoading, isError, refetch } = useSharpMoney();

  const columns = [
    { 
      header: 'Event', 
      accessor: (a: SharpAlert) => (
        <div className="flex flex-col">
          <span className="font-bold text-white">{a.player_name || 'Matchup'}</span>
          <span className="text-xs text-white/40 uppercase">{a.market_key}</span>
        </div>
      ) 
    },
    { 
      header: 'Signal', 
      accessor: (a: SharpAlert) => (
        <div className="flex items-center space-x-2">
          {a.is_steam && (
            <div className="flex items-center space-x-1 px-2 py-0.5 rounded bg-orange-500/10 border border-orange-500/20 text-orange-400 text-[10px] font-black uppercase">
              <Flame className="w-3 h-3" />
              <span>Steam</span>
            </div>
          )}
          {a.is_whale && (
            <div className="flex items-center space-x-1 px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-black uppercase">
              <Anchor className="w-3 h-3" />
              <span>Whale</span>
            </div>
          )}
          {!a.is_steam && !a.is_whale && (
            <div className="flex items-center space-x-1 px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/20 text-purple-400 text-[10px] font-black uppercase">
              <TrendingUp className="w-3 h-3" />
              <span>Sharp Move</span>
            </div>
          )}
        </div>
      )
    },
    { 
      header: 'Side', 
      accessor: (a: SharpAlert) => (
        <span className={`font-black uppercase tracking-widest ${a.sharp_side.toLowerCase().includes('over') || a.sharp_side.toLowerCase().includes('home') ? 'text-green-400' : 'text-red-400'}`}>
          {a.sharp_side}
        </span>
      )
    },
    { 
      header: 'Movement', 
      accessor: (a: SharpAlert) => (
        <span className="font-mono text-white/80">
          {a.line_movement > 0 ? `+${a.line_movement}` : a.line_movement} ticks
        </span>
      )
    },
    { 
      header: 'Time', 
      accessor: (a: SharpAlert) => (
        <div className="flex items-center space-x-1 text-white/40 text-xs">
          <Clock className="w-3 h-3" />
          <span>{formatDistanceToNow(new Date(a.created_at))} ago</span>
        </div>
      )
    },
  ];

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 pb-24">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Page Title */}
        <div className="flex flex-col space-y-2">
           <h1 className="text-4xl font-black tracking-tighter uppercase italic">
             Sharp <span className="text-blue-500 not-italic">Money</span>
           </h1>
           <p className="text-white/40 max-w-xl">
             We track professional volume and institutional line movement in real-time. 
             Follow the money, find the value.
           </p>
        </div>

        {/* Featured Whale Move */}
        {alerts && alerts.filter(a => a.is_whale).length > 0 && (
           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
             {alerts.filter(a => a.is_whale).slice(0, 3).map((whale) => (
                <div key={whale.id} className="relative group overflow-hidden rounded-3xl bg-blue-600/5 border border-blue-500/20 p-6 transition-all hover:bg-blue-600/10">
                   <div className="flex items-center justify-between mb-4">
                      <div className="p-3 rounded-2xl bg-blue-500/20 text-blue-400">
                        <Anchor className="w-6 h-6" />
                      </div>
                      <span className="text-[10px] font-black uppercase text-blue-400/50 tracking-widest">Premium Signal</span>
                   </div>
                   <h3 className="text-xl font-bold mb-1">{whale.player_name || 'Matchup'}</h3>
                   <div className="flex items-center space-x-2 mb-4">
                      <span className="text-xs text-white/40 uppercase">{whale.market_key}</span>
                      <span className="w-1 h-1 rounded-full bg-white/20" />
                      <span className="text-xs font-black text-green-400 uppercase">{whale.sharp_side}</span>
                   </div>
                   <div className="absolute bottom-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                      <Anchor className="w-24 h-24" />
                   </div>
                </div>
             ))}
           </div>
        )}

        {/* Grid / Table */}
        <div className="space-y-4">
           <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-blue-500" />
                <span>Live Signal Feed</span>
              </h2>
           </div>
           
           {isLoading ? (
             <LoadingSkeleton rows={10} />
           ) : isError ? (
             <ErrorRetry onRetry={() => refetch()} />
           ) : (
             <DataTable 
               columns={columns} 
               data={alerts as any} 
               onRowClick={(p) => console.log('Clicked alert:', p)}
             />
           )}
        </div>
      </div>
    </div>
  );
}
