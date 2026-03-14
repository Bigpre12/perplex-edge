"use client";
import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Share2, Copy, CheckCircle, Users } from "lucide-react";
import { supabase } from "@/lib/supabaseClient";
import { api, isApiError } from "@/lib/api";

export function ReferralCard() {
    const [userId, setUserId] = useState<string | null>(null);
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        supabase.auth.getUser().then(({ data }) => setUserId(data.user?.id || null));
    }, []);

    const { data } = useQuery({
        queryKey: ["referrals", userId],
        queryFn: async () => {
            const res = await api.referrals(userId as string);
            return isApiError(res) ? { total_referrals: 0 } : res;
        },
        enabled: !!userId
    });

    const refLink = `https://perplexedge.com/?ref=${data?.referral_code || 'BTL_EDGE'}`;

    const handleCopy = () => {
        navigator.clipboard.writeText(refLink);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="bg-gradient-to-br from-blue-900/40 to-indigo-900/40 border border-blue-500/30 rounded-2xl p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10">
                <Users size={120} />
            </div>

            <div className="relative z-10 flex flex-col md:flex-row gap-6 items-start md:items-center justify-between">
                <div className="max-w-md space-y-2">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <Share2 className="text-blue-400" /> Share & Earn Pro
                    </h3>
                    <p className="text-gray-300 text-sm">
                        Invite 3 friends to Perplex Edge and you both get a free month of our Institutional Pro Tier.
                    </p>
                    <div className="flex items-center gap-4 mt-2">
                        <span className="text-sm font-bold text-blue-300 bg-blue-500/10 px-2 py-1 rounded">
                            {data?.total_referrals || 0}/3 Invites
                        </span>
                    </div>
                </div>

                <div className="bg-black/50 border border-gray-700 rounded-xl p-2 flex items-center gap-2 w-full md:w-auto">
                    <code className="text-sm text-gray-300 px-2">{refLink}</code>
                    <button
                        onClick={handleCopy}
                        className="bg-blue-600 hover:bg-blue-500 text-white p-2 text-xs font-bold rounded-lg transition flex items-center gap-2 whitespace-nowrap"
                    >
                        {copied ? <CheckCircle size={16} /> : <Copy size={16} />}
                        {copied ? "Copied" : "Copy"}
                    </button>
                </div>
            </div>
        </div>
    );
}
