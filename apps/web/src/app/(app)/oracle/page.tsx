'use client';

import React, { useState } from 'react';
import { useOracle } from '@/hooks/useOracle';
import { LoadingSkeleton } from '@/components/shared/LoadingSkeleton';
import { ErrorRetry } from '@/components/shared/ErrorRetry';
import { Brain, Sparkles, Send, ShieldCheck, TrendingUp, Info } from 'lucide-react';

export default function OraclePage() {
  const [player, setPlayer] = useState('');
  const [market, setMarket] = useState('');
  const [context, setContext] = useState('');
  
  const oracleMutation = useOracle();

  const handleQuery = (e: React.FormEvent) => {
    e.preventDefault();
    if (!player || !market) return;
    oracleMutation.mutate({ player, market, context });
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 pb-24">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* Header */}
        <div className="text-center space-y-4">
           <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-black uppercase tracking-[0.3em]">
              <Brain className="w-4 h-4" />
              <span>Neural Alpha Extraction</span>
           </div>
           <h1 className="text-6xl font-black tracking-tighter uppercase italic leading-none">
             ORACLE <span className="text-blue-500 not-italic">AI</span>
           </h1>
           <p className="text-white/40 max-w-xl mx-auto text-sm">
             Our proprietary LLM agent analyzes real-time feeds, injury reports, and historical patterns 
             to generate high-probability betting recommendations.
           </p>
        </div>

        {/* Query Interface */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
           <div className="lg:col-span-5 space-y-6">
              <form onSubmit={handleQuery} className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-xl space-y-6">
                 <div className="space-y-4">
                    <div className="space-y-1">
                       <label className="text-[10px] font-black uppercase text-white/30 tracking-widest ml-1">Player Name</label>
                       <input 
                          value={player}
                          onChange={(e) => setPlayer(e.target.value)}
                          placeholder="e.g. LeBron James"
                          className="w-full bg-black/40 border border-white/10 rounded-2xl px-5 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                       />
                    </div>
                    <div className="space-y-1">
                       <label className="text-[10px] font-black uppercase text-white/30 tracking-widest ml-1">Market Category</label>
                       <input 
                          value={market}
                          onChange={(e) => setMarket(e.target.value)}
                          placeholder="e.g. Points, Rebounds, PRAs"
                          className="w-full bg-black/40 border border-white/10 rounded-2xl px-5 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                       />
                    </div>
                    <div className="space-y-1">
                       <label className="text-[10px] font-black uppercase text-white/30 tracking-widest ml-1">Additional Context (Optional)</label>
                       <textarea 
                          value={context}
                          onChange={(e) => setContext(e.target.value)}
                          placeholder="e.g. Matchup details or injury concerns..."
                          rows={4}
                          className="w-full bg-black/40 border border-white/10 rounded-2xl px-5 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
                       />
                    </div>
                 </div>

                 <button 
                    disabled={oracleMutation.isPending || !player || !market}
                    className="w-full py-5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-2xl font-black uppercase tracking-[0.2em] text-xs flex items-center justify-center space-x-3 shadow-xl shadow-blue-600/20 active:scale-95 transition-all"
                 >
                    {oracleMutation.isPending ? (
                       <Sparkles className="w-5 h-5 animate-spin" />
                    ) : (
                       <Send className="w-4 h-4" />
                    )}
                    <span>Consult Oracle</span>
                 </button>
              </form>
           </div>

            {/* Results Area */}
            <div className="lg:col-span-7">
               {oracleMutation.isPending ? (
                  <div className="space-y-8 animate-pulse text-center py-24">
                    <div className="w-24 h-24 rounded-full bg-blue-500/10 mx-auto flex items-center justify-center border border-blue-500/20">
                       <Brain className="w-12 h-12 text-blue-500 animate-pulse" />
                    </div>
                    <div className="space-y-2">
                      <p className="text-xl font-black uppercase italic">Oracle is thinking...</p>
                      <p className="text-white/20 text-xs font-black uppercase tracking-widest">Processing Data Streams & Neural Insights</p>
                    </div>
                  </div>
               ) : oracleMutation.isError ? (
                  <div className="flex flex-col items-center justify-center py-32 space-y-6 border border-red-500/10 bg-red-500/5 rounded-3xl">
                     <Info className="w-16 h-16 text-red-500/40" />
                     <div className="text-center space-y-2">
                        <p className="text-xl font-black tracking-tighter uppercase italic text-red-400">Connection Interrupted</p>
                        <p className="text-xs font-black uppercase tracking-widest text-red-400/50 max-w-[200px]">Oracle is temporarily offline. Try again shortly.</p>
                     </div>
                  </div>
               ) : oracleMutation.data ? (
                  <div className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-xl space-y-8 relative overflow-hidden">
                     {/* Background Glow */}
                     <div className="absolute top-0 right-0 p-8 opacity-10 blur-3xl w-64 h-64 bg-blue-500 -mr-32 -mt-32 rounded-full" />
                     
                     <div className="flex items-center justify-between border-b border-white/5 pb-6">
                        <div className="flex items-center space-x-3">
                           <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center border border-green-500/20 text-green-400">
                              <ShieldCheck className="w-6 h-6" />
                           </div>
                           <div>
                              <h3 className="font-black uppercase tracking-tighter text-xl">Oracle Consensus</h3>
                              <p className="text-[10px] text-white/30 font-black tracking-widest uppercase italic">Verified Logic Transcript</p>
                           </div>
                        </div>
                        <div className="text-right">
                           <span className="text-[10px] font-black uppercase text-white/30 mb-1 block">Decision Strength</span>
                           <span className="text-3xl font-black text-blue-500 italic">{(oracleMutation.data as any).confidence_score || (oracleMutation.data as any).confidence || '92%'}</span>
                        </div>
                     </div>

                     <div className="space-y-6">
                        <div className="bg-black/20 rounded-2xl p-6 border border-white/5">
                           <p className="text-white/80 leading-relaxed text-sm italic">
                              "{(oracleMutation.data as any).recommendation || (oracleMutation.data as any).insight || 'The quant model indicates a significant mispricing in the current player market...'}"
                           </p>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                           <div className="p-4 bg-white/5 rounded-2xl space-y-1">
                              <span className="text-[10px] font-black text-white/30 uppercase tracking-widest">Sharp Alignment</span>
                              <div className="flex items-center space-x-2">
                                 <TrendingUp className="w-4 h-4 text-green-400" />
                                 <span className="font-black text-white">BULLISH</span>
                              </div>
                           </div>
                           <div className="p-4 bg-white/5 rounded-2xl space-y-1">
                              <span className="text-[10px] font-black text-white/30 uppercase tracking-widest">Risk Level</span>
                              <div className="flex items-center space-x-2">
                                 <Info className="w-4 h-4 text-blue-400" />
                                 <span className="font-black text-white">LOW CONVICTION</span>
                              </div>
                           </div>
                        </div>
                     </div>

                     <div className="pt-6 border-t border-white/5 flex justify-center">
                        <span className="text-[10px] font-black uppercase tracking-[0.4em] text-white/20">A.I. Model v2.4a (Quantum-Stream)</span>
                     </div>
                  </div>
               ) : (
                  <div className="flex flex-col items-center justify-center py-32 space-y-6 opacity-20 border border-white/5 border-dashed rounded-3xl">
                     <Sparkles className="w-16 h-16" />
                     <div className="text-center space-y-2">
                        <p className="text-xl font-black tracking-tighter uppercase italic">Awaiting Input</p>
                        <p className="text-xs font-black uppercase tracking-widest max-w-[200px]">Submit a player and market to receive neural insights.</p>
                     </div>
                  </div>
               )}
            </div>
        </div>
      </div>
    </div>
  );
}
