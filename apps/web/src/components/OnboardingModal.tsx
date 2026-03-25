"use client";
import { useState, useEffect } from "react";
import { ChevronRight, Check } from "lucide-react";
import { supabase } from "@/lib/supabase";

const SPORTS = [
    { key: "basketball_nba", label: "🏀 NBA" },
    { key: "americanfootball_nfl", label: "🏈 NFL" },
    { key: "baseball_mlb", label: "⚾ MLB" },
    { key: "icehockey_nhl", label: "🏒 NHL" },
    { key: "basketball_ncaab", label: "🏀 NCAAB" },
    { key: "tennis_atp", label: "🎾 ATP" },
    { key: "mma_mixed_martial_arts", label: "🥊 UFC" },
];

const BOOKS = ["DraftKings", "FanDuel", "BetMGM", "Caesars", "BetRivers", "PrizePicks", "Underdog"];
const STAKES = ["0.5u", "1u", "2u", "5u", "10u+"];

export function OnboardingModal({ onComplete }: { onComplete?: () => void } = {}) {
    const [isVisible, setIsVisible] = useState(false);
    const [user, setUser] = useState<any>(null);
    const [step, setStep] = useState(0);

    useEffect(() => {
        supabase.auth.getUser().then(({ data }) => {
            if (data.user) {
                setUser(data.user);
                if (!data.user.user_metadata?.onboarded) setIsVisible(true);
            }
        });
    }, []);
    const [sports, setSports] = useState<string[]>([]);
    const [book, setBook] = useState("");
    const [stake, setStake] = useState("1u");

    const toggleSport = (key: string) =>
        setSports(p => p.includes(key) ? p.filter(s => s !== key) : [...p, key]);

    const finish = async () => {
        if (user) {
            await supabase.auth.updateUser({
                data: { onboarded: true, sports, preferredBook: book, defaultStake: stake }
            });
        }
        setIsVisible(false);
        if (onComplete) onComplete();
    };

    if (!isVisible) return null;

    const steps = [
        {
            title: "Welcome to Lucrix 👋",
            subtitle: "The sharpest sports betting intelligence platform. Let's set you up.",
            content: (
                <div className="text-center space-y-4 py-4">
                    <div className="w-20 h-20 bg-indigo-600 rounded-3xl mx-auto flex items-center justify-center text-4xl">⚡</div>
                    <p className="text-gray-400 text-sm leading-relaxed">
                        Real-time props, hit rates, line movement, DvP matchups, and a bet tracker — all in one place.
                    </p>
                </div>
            ),
        },
        {
            title: "Pick your sports",
            subtitle: "We'll show you relevant props and alerts.",
            content: (
                <div className="grid grid-cols-2 gap-2 py-2">
                    {SPORTS.map(s => (
                        <button
                            key={s.key}
                            onClick={() => toggleSport(s.key)}
                            className={`flex items-center gap-2 px-4 py-3 rounded-xl border text-sm font-medium transition ${sports.includes(s.key)
                                ? "bg-indigo-600 border-indigo-500 text-white"
                                : "bg-gray-800 border-gray-700 text-gray-300 hover:border-gray-500"
                                }`}
                        >
                            {sports.includes(s.key) && <Check size={12} />}
                            {s.label}
                        </button>
                    ))}
                </div>
            ),
        },
        {
            title: "Your sportsbook",
            subtitle: "We'll show you the best prices on your book first.",
            content: (
                <div className="grid grid-cols-2 gap-2 py-2">
                    {BOOKS.map(b => (
                        <button
                            key={b}
                            onClick={() => setBook(b)}
                            className={`px-4 py-3 rounded-xl border text-sm font-medium transition ${book === b
                                ? "bg-indigo-600 border-indigo-500 text-white"
                                : "bg-gray-800 border-gray-700 text-gray-300 hover:border-gray-500"
                                }`}
                        >
                            {b}
                        </button>
                    ))}
                </div>
            ),
        },
        {
            title: "Default stake size",
            subtitle: "Used in your bet tracker and Kelly sizing.",
            content: (
                <div className="flex gap-2 flex-wrap py-4 justify-center">
                    {STAKES.map(s => (
                        <button
                            key={s}
                            onClick={() => setStake(s)}
                            className={`px-6 py-3 rounded-xl border text-sm font-bold transition ${stake === s
                                ? "bg-indigo-600 border-indigo-500 text-white"
                                : "bg-gray-800 border-gray-700 text-gray-300 hover:border-gray-500"
                                }`}
                        >
                            {s}
                        </button>
                    ))}
                </div>
            ),
        },
    ];

    const current = steps[step];
    const isLast = step === steps.length - 1;

    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 border border-gray-700 rounded-3xl p-6 w-full max-w-md space-y-5">
                {/* Progress */}
                <div className="flex gap-1.5">
                    {steps.map((_, i) => (
                        <div key={i} className={`h-1 flex-1 rounded-full transition-all ${i <= step ? "bg-indigo-500" : "bg-gray-700"}`} />
                    ))}
                </div>

                <div>
                    <h2 className="text-white font-black text-xl">{current.title}</h2>
                    <p className="text-gray-400 text-sm mt-1">{current.subtitle}</p>
                </div>

                {current.content}

                <button
                    onClick={() => isLast ? finish() : setStep(s => s + 1)}
                    disabled={step === 1 && sports.length === 0}
                    className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition"
                >
                    {isLast ? "Let's Go ⚡" : "Continue"} {!isLast && <ChevronRight size={16} />}
                </button>

                {step > 0 && (
                    <button onClick={() => setStep(s => s - 1)} className="w-full text-gray-500 text-sm hover:text-gray-400 transition">
                        Back
                    </button>
                )}
            </div>
        </div>
    );
}
