"use client";

export function PropSkeleton() {
    return (
        <div className="bg-lucrix-surface border border-lucrix-border rounded-xl p-4 
                    animate-pulse shadow-card">
            <div className="flex items-center gap-2 mb-4">
                <div className="w-9 h-9 rounded-full bg-lucrix-dark" />
                <div className="space-y-2">
                    <div className="h-3 w-28 bg-lucrix-dark rounded" />
                    <div className="h-2.5 w-20 bg-lucrix-dark rounded" />
                </div>
            </div>
            <div className="h-20 bg-lucrix-dark/80 rounded-lg mb-4" />
            <div className="grid grid-cols-3 gap-2 mb-4">
                {[0, 1, 2].map(i => (
                    <div key={i} className="h-12 bg-lucrix-dark/80 rounded-md" />
                ))}
            </div>
            <div className="h-10 bg-lucrix-dark rounded-lg" />
        </div>
    )
}
