"use client";
import { Calendar, ChevronRight, Clock } from "lucide-react";
import { ErrorBoundary } from "@/components/ErrorBoundary";

export default function Schedule() {
    const sports = [
        { name: "NBA Basketball", status: "Active", gamesToday: 8, color: "text-orange-400", bg: "bg-orange-400/10 border-orange-400/20" },
        { name: "NFL Football", status: "Active Phase", gamesToday: 0, color: "text-blue-400", bg: "bg-blue-400/10 border-blue-400/20" },
        { name: "NHL Hockey", status: "Active", gamesToday: 4, color: "text-cyan-400", bg: "bg-cyan-400/10 border-cyan-400/20" },
        { name: "MLB Baseball", status: "Offseason", gamesToday: 0, color: "text-red-400", bg: "bg-red-400/10 border-red-400/20" },
    ];

    return (
        <ErrorBoundary label="Failed to load schedule">
            <div className="space-y-6 p-4">
                <div className="flex items-center justify-between">
                    <h1 className="text-2xl font-black text-white flex items-center gap-2">
                        <Calendar className="text-blue-500" /> Schedule Grid
                    </h1>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {sports.map(s => (
                        <div key={s.name} className={`rounded-2xl border p-4 ${s.bg} flex items-center justify-between`}>
                            <div>
                                <h2 className={`font-black text-lg ${s.color}`}>{s.name}</h2>
                                <p className="text-gray-400 text-sm flex items-center gap-1 mt-1">
                                    <Clock size={12} /> {s.status}
                                </p>
                            </div>
                            <div className="text-right">
                                {s.gamesToday > 0 ? (
                                    <span className="font-bold text-white bg-white/10 px-2 py-1 rounded text-sm">
                                        {s.gamesToday} Games Today
                                    </span>
                                ) : (
                                    <span className="text-gray-500 text-sm">No Action</span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-center mt-8">
                    <h3 className="text-white font-bold mb-2">Upcoming Events & Tournaments</h3>
                    <p className="text-gray-500 text-sm mb-4">Coverage for major PGA, Tennis, and MMA events will appear here.</p>
                    <button className="bg-gray-800 text-white px-4 py-2 rounded-lg text-sm font-semibold inline-flex items-center gap-2 hover:bg-gray-700 transition">
                        View Full Calendar <ChevronRight size={16} />
                    </button>
                </div>
            </div>
        </ErrorBoundary>
    );
}
