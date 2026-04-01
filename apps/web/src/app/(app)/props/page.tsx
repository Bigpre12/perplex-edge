'use client';

import React, { useState } from 'react';
import { useProps, PropRecord } from '@/hooks/useProps';
import { DataTable } from '@/components/shared/DataTable';
import { GradeBadge } from '@/components/shared/GradeBadge';
import { LoadingSkeleton } from '@/components/shared/LoadingSkeleton';
import { ErrorRetry } from '@/components/shared/ErrorRetry';
import { SportFilter } from '@/components/shared/SportFilter';
import { Check, Plus } from 'lucide-react';
import { useLucrixStore } from '@/store';

export default function PropsPage() {
  const [sport, setSport] = useState('basketball_nba');
  const [gradeFilter, setGradeFilter] = useState('all');
  
  const { data: props, isLoading, isError, refetch } = useProps(sport);

  const filteredProps = (props || []).filter(p => {
    if (gradeFilter !== 'all' && p.grade !== gradeFilter) return false;
    return true;
  });

  const columns = [
    { 
      header: 'Player', 
      accessor: (p: PropRecord) => (
        <div className="flex flex-col">
          <span className="font-bold text-white">{p.player_name}</span>
          <span className="text-xs text-white/40">{p.sport.replace('_', ' ').toUpperCase()}</span>
        </div>
      ) 
    },
    { header: 'Market', accessor: (p: any) => p.market_key, className: 'capitalize' },
    { header: 'Line', accessor: (p: PropRecord) => <span className="font-mono">{p.line}</span> },
    { 
      header: 'Odds', 
      accessor: (p: PropRecord) => (
        <div className="flex space-x-2 text-xs font-mono">
          <span className="text-green-400">O: {p.odds_over > 0 ? `+${p.odds_over}` : p.odds_over}</span>
          <span className="text-red-400">U: {p.odds_under > 0 ? `+${p.odds_under}` : p.odds_under}</span>
        </div>
      )
    },
    { 
      header: 'Confidence', 
      accessor: (p: PropRecord) => {
        const barStyle = { width: `${(p.confidence || 0) * 100}%` } as React.CSSProperties;
        return (
          <div className="w-24 bg-white/5 h-1.5 rounded-full overflow-hidden">
            {React.createElement('div', { className: 'bg-blue-500 h-full', style: barStyle })}
          </div>
        );
      }
    },
    { 
      header: 'Grade', 
      accessor: (p: PropRecord) => <GradeBadge grade={p.grade} /> 
    },
    { header: 'Bookmaker', accessor: (p: any) => p.book, className: 'text-xs text-white/50 uppercase' },
    {
      header: 'Action',
      accessor: (p: PropRecord) => {
        const { addLeg, parlayLegs } = useLucrixStore();
        const isInParlay = parlayLegs.some((l: any) => l.id === p.id);
        
        return (
          <button
            onClick={(e) => {
              e.stopPropagation();
              addLeg(p);
            }}
            disabled={isInParlay}
            className={`flex items-center space-x-1 px-3 py-1 rounded-md text-[10px] font-black uppercase tracking-widest transition-all ${
              isInParlay 
                ? 'bg-green-500/10 text-green-500 border border-green-500/20' 
                : 'bg-blue-500/10 text-blue-400 border border-blue-500/20 hover:bg-blue-500 hover:text-white'
            }`}
          >
            {isInParlay ? <Check className="w-3 h-3" /> : <Plus className="w-3 h-3" />}
            <span>{isInParlay ? 'Added' : 'Parlay'}</span>
          </button>
        );
      }
    }
  ];

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 pb-24">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-black tracking-tight text-white mb-1">
              PROPS <span className="text-blue-500">BOARD</span>
            </h1>
            <p className="text-white/40 text-sm">Real-time player prop analytics and grading.</p>
          </div>
          
          <div className="flex items-center space-x-4">
             <select 
               value={gradeFilter} 
               onChange={(e) => setGradeFilter(e.target.value)}
               title="Grade Filter"
               aria-label="Grade Filter"
               className="bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
             >
               <option value="all">All Grades</option>
               <option value="A">Grade A</option>
               <option value="B">Grade B</option>
               <option value="C">Grade C</option>
             </select>
          </div>
        </div>

        <SportFilter activeSport={sport} onSportChange={setSport} />

        {/* Content */}
        {isLoading ? (
          <LoadingSkeleton rows={10} />
        ) : isError ? (
          <ErrorRetry onRetry={() => refetch()} />
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs text-white/30 px-2">
              <span>Showing {filteredProps.length} active props</span>
              <span>Sorted by Confidence</span>
            </div>
            <DataTable 
              columns={columns} 
              data={filteredProps as any} 
              onRowClick={(p) => console.log('Clicked prop:', p)}
            />
          </div>
        )}
      </div>
    </div>
  );
}
