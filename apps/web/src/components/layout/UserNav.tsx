"use client";
import { useAuth } from "@/hooks/useAuth";
import { useSubscription } from "@/hooks/useSubscription";
import Link from "next/link";

export function UserNav() {
    const { user, signOut, loading: authLoading } = useAuth();
    const { tier, loading: subLoading } = useSubscription();

    const loading = authLoading || subLoading;
    const isActuallySignedIn = tier !== "free" || !!user;

    if (loading) return <div className="w-8 h-8 rounded-full bg-white/5 animate-pulse" />;

    return (
        <div className="flex items-center gap-3">
            {!isActuallySignedIn ? (
                <>
                    <Link href="/login">
                        <button className="text-xs font-bold text-[#6B7280] hover:text-white transition-colors uppercase tracking-wider">
                            Log In
                        </button>
                    </Link>
                    <Link href="/signup">
                        <button className="px-4 py-1.5 bg-[#F5C518] hover:bg-[#C49A12] text-black text-xs font-black rounded-full transition-all shadow-lg shadow-[#F5C518]/10 uppercase tracking-tight">
                            Join Lucrix
                        </button>
                    </Link>
                </>
            ) : (
                <div className="flex items-center gap-3">
                    <button
                        onClick={signOut}
                        className="text-[10px] font-bold text-white/40 hover:text-white transition-colors uppercase tracking-widest"
                    >
                        Sign Out
                    </button>
                    <Link href="/settings">
                        <div className="w-8 h-8 rounded-full border border-[#F5C518]/20 bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-[10px] font-black text-white hover:opacity-80 transition-opacity cursor-pointer">
                            {user?.email?.[0].toUpperCase() ?? "U"}
                        </div>
                    </Link>
                </div>
            )}
        </div>
    );
}
