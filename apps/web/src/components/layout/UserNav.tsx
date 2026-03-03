"use client";

import { useState, useEffect, useRef } from "react";
import { User, LogOut, Settings, Shield, ChevronDown } from "lucide-react";
import { useRouter } from "next/navigation";

export function UserNav() {
    const [isOpen, setIsOpen] = useState(false);
    const [userEmail, setUserEmail] = useState<string | null>(null);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const router = useRouter();

    useEffect(() => {
        // Simple JWT decode to get email for display
        const getCookie = (name: string) => {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop()?.split(';').shift();
            return null;
        };

        const token = getCookie('sb-access-token') || getCookie('perplex-auth');
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                setUserEmail(payload.email || payload.sub);
            } catch (e) {
                console.error("Failed to decode token", e);
            }
        }

        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleLogout = () => {
        // Clear cookies
        document.cookie = "sb-access-token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;";
        document.cookie = "perplex-auth=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;";
        router.push("/login");
    };

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 p-1 rounded-full hover:bg-[#1E1E35] transition-colors border border-transparent hover:border-[#F5C518]/20"
            >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#F5C518] to-[#C49A12] flex items-center justify-center text-black font-bold text-xs shadow-lg shadow-[#F5C518]/10">
                    {userEmail ? userEmail[0].toUpperCase() : <User size={16} />}
                </div>
                <ChevronDown size={14} className={`text-[#6B7280] transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-[#0F0F1A] border border-[#1E1E35] rounded-2xl shadow-2xl overflow-hidden glass-morphism z-[100] animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="px-4 py-3 border-b border-[#1E1E35]">
                        <p className="text-xs text-[#6B7280] font-medium uppercase tracking-wider mb-1">Signed in as</p>
                        <p className="text-sm font-semibold text-white truncate">{userEmail || "User"}</p>
                    </div>

                    <div className="p-2">
                        <button className="flex w-full items-center gap-2 px-3 py-2 text-sm text-[#94a3b8] hover:text-white hover:bg-[#1E1E35] rounded-xl transition-colors group">
                            <Shield size={16} className="group-hover:text-[#F5C518]" />
                            Subscription
                        </button>
                        <button className="flex w-full items-center gap-2 px-3 py-2 text-sm text-[#94a3b8] hover:text-white hover:bg-[#1E1E35] rounded-xl transition-colors group">
                            <Settings size={16} className="group-hover:text-[#F5C518]" />
                            Settings
                        </button>
                    </div>

                    <div className="p-2 border-t border-[#1E1E35]">
                        <button
                            onClick={handleLogout}
                            className="flex w-full items-center gap-2 px-3 py-2 text-sm text-[#EF4444] hover:bg-[#EF4444]/10 rounded-xl transition-colors"
                        >
                            <LogOut size={16} />
                            Log out
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
