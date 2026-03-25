'use client';

import React, { useState } from 'react';
import { useParlay } from '@/hooks/useParlay';
import { DataTable } from '@/components/shared/DataTable';
import { GradeBadge } from '@/components/shared/GradeBadge';
import { LoadingSkeleton } from '@/components/shared/LoadingSkeleton';
import { ErrorRetry } from '@/components/shared/ErrorRetry';
import { Zap, Target, Trash2, Plus, Calculator } from 'lucide-react';

interface ParlayLeg {
  id: string;
  player_name: string;
  market_key: string;
  line: number;
  odds: number;
  sport: string;
}

export default function ParlayPage() {
  const { data: props, isLoading, isError, refetch } = useParlay();
  const [selectedLegs, setSelectedLegs] = useState<ParlayLeg[]>([]);

  const toggleLeg = (leg: ParlayLeg) => {
    if (selectedLegs.find(l => l.id === leg.id)) {
      setSelectedLegs(selectedLegs.filter(l => l.id !== leg.id));
    } else {
      if (selectedLegs.length >= 6) return;
      setSelectedLegs([...selectedLegs, leg]);
    }
  };

  const calculateTotalOdds = () => {
    if (selectedLegs.length === 0) return 0;
    const multiplier = selectedLegs.reduce((acc, leg) => {
        const mult = leg.odds > 0 ? (leg.odds / 100) + 1 : (100 / Math.abs(leg.odds)) + 1;
        return acc * mult;
    }, 1);
    
    if (multiplier >= 2) return Math.round((multiplier - 1) * 100);
    return Math.round(-100 / (multiplier - 1));
  };

  const totalOdds = calculateTotalOdds();

  const columns = [
    { header: 'Player', accessor: 'player_name', className: 'font-bold' },
    { header: 'Market', accessor: 'market_key', className: 'text-xs uppercase' },
    { header: 'Line', accessor: (p: any) => <span className="font-mono">{p.line}</span> },
    { header: 'Odds', accessor: (p: any) => <span className="text-green-400 font-mono">{p.over_odds || -110}</span> },
    { 
      header: 'Action', 
      accessor: (p: any) => {
        const isSelected = selectedLegs.find(l => l.id === p.id);
        return (
          <button
            onClick={() => toggleLeg({ ...p, odds: p.over_odds || -110 })}
            className={`px-3 py-1 rounded-md text-[10px] font-black uppercase transition-all ${
              isSelected 
                ? 'bg-red-500/10 text-red-500 border border-red-500/20' 
                : 'bg-blue-500 text-white hover:bg-blue-600'
            }`}
          >
            {isSelected ? 'Remove' : 'Add Leg'}
          </button>
        );
      }
    },
  ];

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 pb-24">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12">
        {/* Selection Area */}
        <div className="lg:col-span-8 space-y-8">
           <div className="space-y-2">
              <h1 className="text-5xl font-black italic tracking-tighter uppercase font-display leading-none">
                PARLAY <span className="text-blue-500 not-italic">BUILDER</span>
              </h1>
              <p className="text-white/40 text-sm">Select top-graded props to build your mathematical edge.</p>
           </div>

           <div className="space-y-4">
              <h2 className="text-xs font-black uppercase tracking-[0.2em] text-white/30 flex items-center gap-2">
                 <Plus className="w-3 h-3" /> Recommended Legs
              </h2>
              {isLoading ? (
                <LoadingSkeleton rows={5} />
              ) : isError ? (
                <ErrorRetry onRetry={() => refetch()} />
              ) : (
                <DataTable 
                  columns={columns} 
                  data={props || []} 
                />
              )}
           </div>
        </div>

        {/* Builder Sidebar */}
        <div className="lg:col-span-4">
           <div className="sticky top-24 bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-xl space-y-8">
              <div className="flex items-center justify-between border-b border-white/5 pb-6">
                 <h2 className="text-xl font-bold flex items-center space-x-2">
                    <Zap className="w-5 h-5 text-blue-500 fill-blue-500" />
                    <span>Your Slip</span>
                 </h2>
                 <span className="text-[10px] font-black uppercase text-white/30">{selectedLegs.length}/6 Legs</span>
              </div>

              <div className="space-y-4 max-h-[400px] overflow-y-auto overflow-x-hidden pr-2">
                 {selectedLegs.length === 0 ? (
                    <div className="py-20 text-center space-y-4 opacity-20">
                       <Target className="w-12 h-12 mx-auto" />
                       <p className="text-xs font-black uppercase tracking-widest">Slip is Empty</p>
                    </div>
                 ) : (
                    selectedLegs.map((leg) => (
                       <div key={leg.id} className="p-4 bg-white/5 border border-white/10 rounded-2xl flex items-center justify-between group">
                          <div>
                             <p className="text-sm font-bold">{leg.player_name}</p>
                             <p className="text-[10px] text-white/40 uppercase">{leg.market_key} {leg.line}</p>
                          </div>
                          <div className="flex items-center space-x-4">
                             <span className="font-mono text-green-400 text-sm">{leg.odds > 0 ? `+${leg.odds}` : leg.odds}</span>
                             <button onClick={() => toggleLeg(leg)} className="text-white/20 hover:text-red-500 transition-colors">
                                <Trash2 className="w-4 h-4" />
                             </button>
                          </div>
                       </div>
                    ))
                 )}
              </div>

              <div className="space-y-6 pt-6 border-t border-white/5">
                 <div className="flex justify-between items-end">
                    <div>
                       <span className="text-[10px] font-black uppercase text-white/30 mb-1 block">Total Odds</span>
                       <span className="text-4xl font-black italic text-blue-500">{selectedLegs.length > 0 ? (totalOdds > 0 ? `+${totalOdds}` : totalOdds) : '---'}</span>
                    </div>
                    <div className="text-right">
                       <span className="text-[10px] font-black uppercase text-white/30 mb-1 block">Proj. ROI</span>
                       <span className="text-xl font-black text-green-400">+{selectedLegs.length * 12}%</span>
                    </div>
                 </div>

                 <button 
                   disabled={selectedLegs.length < 2}
                   className={`w-full py-4 rounded-2xl font-black uppercase tracking-widest text-xs transition-all flex items-center justify-center space-x-2 ${
                     selectedLegs.length >= 2 
                       ? 'bg-blue-600 text-white shadow-xl shadow-blue-600/20 hover:scale-[1.02] active:scale-95' 
                       : 'bg-white/5 text-white/20 cursor-not-allowed border border-white/5'
                   }`}
                 >
                    <Calculator className="w-4 h-4" />
                    <span>Analyze Correlation</span>
                 </button>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
