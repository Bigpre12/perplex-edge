"use client";

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { EmptyState } from "@/components/ui/EmptyState";
import { SPORTS } from '@/utils/sportUtils';

function CombosPageContent() {
    const searchParams = useSearchParams();
    const activeSport = searchParams.get('sport') || 'basketball_nba';
    const sportName = SPORTS.find(s => s.id === activeSport)?.name || 'Sport';

    return (
        <div className="px-4 py-8 max-w-7xl mx-auto">
            <h1 className="text-2xl font-black tracking-tight text-white mb-6 uppercase italic">Prop Combos</h1>

            <EmptyState
                title={`${sportName} Combos Engine Idle`}
                description={`We're currently recalibrating the correlated prop combo engine for ${sportName}. Check back shortly for high-EV player bundles.`}
            />
        </div>
    )
}

export default function CombosPage() {
    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center py-20">
                <div className="animate-bounce text-[#F5C518] text-2xl mb-4">🌀</div>
                <p className="text-[#6B7280] text-sm italic font-black uppercase tracking-widest">Loading Combo Matrix...</p>
            </div>
        }>
            <CombosPageContent />
        </Suspense>
    );
}
