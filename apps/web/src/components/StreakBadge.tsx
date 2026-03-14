import { Flame, Snowflake } from "lucide-react";

export function StreakBadge({ streak, isHot }: { streak: string, isHot: boolean }) {
    if (!streak || streak === "0L0") return null;

    // Parse streak e.g. "7L10" -> 7 hits out of last 10
    const [hits, total] = streak.split("L").map(Number);
    const hitRate = hits / total;

    if (hitRate >= 0.7 || isHot) {
        return (
            <div className="flex items-center gap-1 bg-orange-500/20 text-orange-400 px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider">
                <Flame size={12} /> {streak} (HOT)
            </div>
        );
    } else if (hitRate <= 0.3 && total >= 5) {
        return (
            <div className="flex items-center gap-1 bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider">
                <Snowflake size={12} /> {streak} (COLD)
            </div>
        );
    }

    return (
        <div className="flex items-center gap-1 bg-gray-800 text-gray-400 px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider">
            {streak}
        </div>
    );
}
