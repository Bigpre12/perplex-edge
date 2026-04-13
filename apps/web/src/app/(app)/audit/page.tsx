'use client';

import React, { useState } from 'react';
import { useAudit } from '@/hooks/useAudit';
import { DataTable } from '@/components/shared/DataTable';
import { GradeBadge } from '@/components/shared/GradeBadge';
import { LoadingSkeleton } from '@/components/shared/LoadingSkeleton';
import { ErrorRetry } from '@/components/shared/ErrorRetry';
import { SportFilter } from '@/components/shared/SportFilter';
import { Download, ChevronLeft, ChevronRight, FileSpreadsheet } from 'lucide-react';
import { format } from 'date-fns';

export default function AuditPage() {
  const [page, setPage] = useState(0);
  const [sport, setSport] = useState('all');
  const limit = 50;

  const { data: auditData, isLoading, isError, refetch } = useAudit(page, limit);

  const exportToCSV = () => {
    if (!auditData?.rows) return;
    const headers = ['Player', 'Market', 'Line', 'Result', 'Grade', 'Confidence', 'Book', 'Sport', 'Commence', 'Graded At'];
    const csvContent = [
      headers.join(','),
      ...auditData.rows.map((r: any) => [
        r.player_name,
        r.market_key,
        r.line,
        r.result || 'N/A',
        r.grade,
        r.confidence,
        r.book,
        r.sport,
        r.commence_time,
        r.graded_at
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `audit_export_${format(new Date(), 'yyyyMMdd')}.csv`;
    link.click();
  };

  const columns = [
    { 
      header: 'Player', 
      accessor: (r: any) => (
        <div className="flex flex-col">
          <span className="font-bold text-white">{r.player_name}</span>
          <span className="text-[10px] text-white/30 uppercase">{r.sport}</span>
        </div>
      )
    },
    { header: 'Market', accessor: 'market_key', className: 'text-xs uppercase font-mono' },
    { header: 'Line', accessor: (r: any) => <span className="font-mono">{r.line}</span> },
    { 
      header: 'Result', 
      accessor: (r: any) => (
        <span className={`font-black ${r.result > r.line ? 'text-green-400' : 'text-red-400'}`}>
          {r.result || '--'}
        </span>
      )
    },
    { 
      header: 'Grade', 
      accessor: (r: any) => <GradeBadge grade={r.grade} /> 
    },
    { 
      header: 'Edge', 
      accessor: (r: any) => {
        const barStyle = { width: `${(r.confidence || 0) * 100}%` } as React.CSSProperties;
        return (
          <div className="w-16 h-1 bg-white/5 rounded-full overflow-hidden">
            {React.createElement('div', { className: 'bg-blue-500 h-full', style: barStyle })}
          </div>
        );
      }
    },
    { header: 'Book', accessor: 'book', className: 'text-[10px] uppercase text-white/40' },
    { 
      header: 'Commence', 
      accessor: (r: any) => (
        <span className="text-[10px] text-white/30 font-mono">
          {format(new Date(r.commence_time), 'MM/dd HH:mm')}
        </span>
      )
    },
    { 
      header: 'Graded', 
      accessor: (r: any) => (
        <span className="text-[10px] text-white/30 font-mono">
          {r.graded_at ? format(new Date(r.graded_at), 'MM/dd HH:mm') : '--'}
        </span>
      )
    },
  ];

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 pb-24">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div className="space-y-2">
             <h1 className="text-5xl font-black tracking-tighter uppercase leading-none italic">
                PERFORMANCE <span className="text-blue-500 not-italic">AUDIT</span>
             </h1>
             <p className="text-white/40 max-w-xl text-sm leading-relaxed">
               Full transparency into historical performance. Every pick, every grade, and every result verified 
               against official scoring.
             </p>
          </div>

          <button 
             onClick={exportToCSV}
             className="flex items-center space-x-2 px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl transition-all text-sm font-bold shadow-lg active:scale-95"
          >
             <FileSpreadsheet className="w-4 h-4 text-green-400" />
             <span>Export History (CSV)</span>
          </button>
        </div>

        <SportFilter activeSport={sport} onSportChange={setSport} />

        {/* Content Table */}
        <div className="space-y-6">
           <div className="flex items-center justify-between px-2">
              <span className="text-[10px] font-black uppercase tracking-widest text-white/30">
                 Database Transcript: {auditData?.total || 0} Graded Entries
              </span>

              {/* Pagination Controls */}
              <div className="flex items-center space-x-4">
                 <button 
                    disabled={page === 0}
                    onClick={() => setPage(page - 1)}
                    className="p-1 hover:bg-white/5 rounded disabled:opacity-20"
                    title="Previous Page"
                    aria-label="Previous Page"
                 >
                    <ChevronLeft className="w-5 h-5" />
                 </button>
                 <span className="text-xs font-mono text-white/50">Page {page + 1}</span>
                 <button 
                    disabled={(page + 1) * limit >= (auditData?.total || 0)}
                    onClick={() => setPage(page + 1)}
                    className="p-1 hover:bg-white/5 rounded disabled:opacity-20"
                    title="Next Page"
                    aria-label="Next Page"
                 >
                    <ChevronRight className="w-5 h-5" />
                 </button>
              </div>
           </div>

           {isLoading ? (
             <LoadingSkeleton rows={20} />
           ) : isError ? (
             <ErrorRetry onRetry={() => refetch()} />
           ) : (
             <DataTable 
               columns={columns} 
               data={auditData?.rows || []} 
               onRowClick={(r) => console.log('Audit entry:', r)}
             />
           )}
        </div>
      </div>
    </div>
  );
}
