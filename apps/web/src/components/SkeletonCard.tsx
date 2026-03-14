"use client";
import React from 'react';

export function SkeletonPropCard() {
    return (
        <div className="relative overflow-hidden bg-[#0a0a0f]/80 backdrop-blur-xl border border-white/5 rounded-2xl p-4 min-h-[160px] animate-pulse">
            {/* Shimmer Effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full animate-[shimmer_2s_infinite]" />

            <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-white/5 rounded-full" />
                    <div className="space-y-2">
                        <div className="h-4 w-32 bg-white/10 rounded" />
                        <div className="h-3 w-20 bg-white/5 rounded" />
                    </div>
                </div>
                <div className="h-8 w-14 bg-white/10 rounded-lg" />
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="h-10 bg-white/5 rounded-xl border border-white/5" />
                <div className="h-10 bg-white/5 rounded-xl border border-white/5" />
            </div>

            <div className="flex justify-between items-center pt-3 border-t border-white/5">
                <div className="flex gap-2">
                    <div className="h-5 w-16 bg-white/5 rounded-full" />
                    <div className="h-5 w-16 bg-white/5 rounded-full" />
                </div>
                <div className="h-6 w-24 bg-white/10 rounded-md" />
            </div>
        </div>
    );
}

export function SkeletonGrid({ count = 6 }: { count?: number }) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: count }).map((_, i) => (
                <SkeletonPropCard key={i} />
            ))}
        </div>
    );
}
