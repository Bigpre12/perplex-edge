"use client";

export function PropSkeleton() {
    return (
        <div className="bg-[#141424] border border-[#1E1E35] rounded-2xl p-4 
                    animate-pulse">
            <div className="flex items-center gap-2 mb-4">
                <div className="w-9 h-9 rounded-full bg-[#1E1E35]" />
                <div className="space-y-2">
                    <div className="h-3 w-28 bg-[#1E1E35] rounded" />
                    <div className="h-2.5 w-20 bg-[#1E1E35] rounded" />
                </div>
            </div>
            <div className="h-20 bg-[#0F0F1A] rounded-xl mb-4" />
            <div className="grid grid-cols-3 gap-2 mb-4">
                {[0, 1, 2].map(i => (
                    <div key={i} className="h-12 bg-[#0F0F1A] rounded-lg" />
                ))}
            </div>
            <div className="h-10 bg-[#1E1E35] rounded-xl" />
        </div>
    )
}
