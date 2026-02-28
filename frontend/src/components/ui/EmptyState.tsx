"use client";

interface EmptyStateProps {
    onReset?: () => void;
    title?: string;
    description?: string;
}

export function EmptyState({ onReset, title = 'No picks right now', description = 'The Lucrix engine is filtering for real edge. Check back before tip-off or lower your filters.' }: EmptyStateProps) {
    return (
        <div className="flex flex-col items-center justify-center py-20 px-8 text-center bg-[#080810]">
            <div className="text-6xl mb-6 animate-bounce">🎯</div>
            <h3 className="text-white font-bold text-xl mb-3">
                {title}
            </h3>
            <p className="text-[#6B7280] text-sm mb-8 max-w-xs leading-relaxed">
                {description}
            </p>
            <button onClick={onReset}
                className="bg-[#F5C518] text-black font-bold text-sm 
                   px-8 py-3 rounded-full hover:bg-[#C49A12] 
                   transition-all transform hover:scale-105 active:scale-95
                   shadow-[0_0_20px_rgba(245,197,24,0.2)]">
                Show All Picks
            </button>
        </div>
    )
}
