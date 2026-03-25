'use client';

import React, { useState } from 'react';
import { useEV, EVRecord } from '@/hooks/useEV';
import { DataTable } from '@/components/shared/DataTable';
import { LoadingSkeleton } from '@/components/shared/LoadingSkeleton';
import { ErrorRetry } from '@/components/shared/ErrorRetry';
import { SportFilter } from '@/components/shared/SportFilter';
import { TrendingUp, Percent, Info } from 'lucide-react';

export default function EVPage() {
  const [sport, setSport] = useState('all');
  const { data: evSignals, isLoading, isError, refetch } = useEV(sport);

  const getEVColor = (val: number) => {
    if (val >= 5) return 'text-green-400';
    if (val >= 2) return 'text-yellow-400';
    return 'text-red-400';
  };

  const columns = [
    { 
      header: 'Player / Market', 
      accessor: (p: EVRecord) => (
        <div className="flex flex-col">
          <span className="font-bold text-white">{p.player_name || 'Matchup'}</span>
          <span className="text-xs text-white/40 uppercase font-mono">{p.market_key}</span>
        </div>
      ) 
    },
    { header: 'Line', accessor: (p: EVRecord) => <span className="font-mono">{p.line}</span> },
    { 
      header: 'EV Score', 
      accessor: (p: EVRecord) => (
        <span className={`font-black ${getEVColor(p.ev_percentage)}`}>
          {p.ev_percentage.toFixed(2)}%
        </span>
      )
    },
    { 
      header: 'Edge', 
      accessor: (p: EVRecord) => (
        <span className="text-white/60 font-mono">
          {(p.edge_percent * 100).toFixed(1)}%
        </span>
      )
    },
    { header: 'Bookmaker', accessor: 'bookmaker', className: 'uppercase text-xs font-medium' },
    { 
      header: 'Recommendation', 
      accessor: (p: EVRecord) => (
        <span className="px-3 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-md text-xs font-bold uppercase tracking-widest">
          {p.recommendation || 'Watch'}
        </span>
      )
    },
  ];

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 pb-24">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Hero Section */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-900/20 via-black to-black border border-white/10 p-8 md:p-12">
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-8">
            <div className="max-w-2xl space-y-4">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold uppercase tracking-widest leading-none">
                <TrendingUp className="w-3 h-3" />
                <span>Positive Expectation Engine</span>
              </div>
              <h1 className="text-4xl md:text-6xl font-black tracking-tighter leading-none">
                EV+ <span className="text-blue-500">SIGNALS</span>
              </h1>
              <p className="text-white/50 text-lg leading-relaxed">
                Our quant engine identifies mathematical edges where sportsbook odds misprice real-world probabilities.
              </p>
            </div>
            
            <div className="flex gap-4">
               <div className="px-6 py-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                 <div className="text-white/30 text-xs font-bold uppercase mb-1">Total Edges</div>
                 <div className="text-3xl font-black">{evSignals?.length || 0}</div>
               </div>
               <div className="px-6 py-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                 <div className="text-white/30 text-xs font-bold uppercase mb-1">Max Edge</div>
                 <div className="text-3xl font-black text-green-400">
                    {Math.max(...(evSignals?.map(s => s.ev_percentage) || [0])).toFixed(1)}%
                 </div>
               </div>
            </div>
          </div>
          
          <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/10 blur-[100px] -mr-48 -mt-48 rounded-full" />
        </div>

        <SportFilter activeSport={sport} onSportChange={setSport} />

        {/* Content */}
        {isLoading ? (
          <LoadingSkeleton rows={10} />
        ) : isError ? (
          <ErrorRetry onRetry={() => refetch()} />
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between text-xs text-white/30 px-2">
              <div className="flex items-center space-x-4">
                 <span className="flex items-center space-x-1">
                   <div className="w-2 h-2 rounded-full bg-green-400" />
                   <span>High ({'>'}5%)</span>
                 </span>
                 <span className="flex items-center space-x-1">
                   <div className="w-2 h-2 rounded-full bg-yellow-400" />
                   <span>Mid (2-5%)</span>
                 </span>
                 <span className="flex items-center space-x-1">
                   <div className="w-2 h-2 rounded-full bg-red-400" />
                   <span>Low ({'<'}2%)</span>
                 </span>
              </div>
              <span className="flex items-center space-x-1">
                <Info className="w-3 h-3" />
                <span>Computed against Sharp Consensus</span>
              </span>
            </div>
            
            <DataTable 
              columns={columns} 
              data={evSignals as any} 
              onRowClick={(p) => console.log('Clicked signal:', p)}
            />
          </div>
        )}
      </div>
    </div>
  );
}
