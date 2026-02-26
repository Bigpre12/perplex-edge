/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect } from 'react';
import { Share2, MessageSquare, ThumbsUp, TrendingUp, Users, Crown, ShieldCheck } from 'lucide-react';
import { useBrainData } from '../hooks/useBrainData';

export default function SharedIntel() {
    const [activeSport] = useState('basketball_nba');
    const { marketIntel, loading } = useBrainData(activeSport);

    const [leaderboard, setLeaderboard] = useState([
        { name: "Marcus Sharp", profit: 114 },
        { name: "QuantEdge", profit: 92 },
        { name: "ParlayKing", profit: 87 },
        { name: "KellyCriterion", profit: 64 }
    ]);

    useEffect(() => {
        const interval = setInterval(() => {
            setLeaderboard(prev => prev.map(u => ({ ...u, profit: u.profit + Math.floor(Math.random() * 3) })));
        }, 10000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex gap-8">
            {/* Feed Area */}
            <div className="flex-1 space-y-6 min-w-0">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-primary/10 text-primary">
                                <Users size={24} />
                            </div>
                            Intelligence Feed
                        </h1>
                        <p className="text-sm text-secondary mt-1">Real-time collaboration across the Perplex network.</p>
                    </div>
                    <div className="flex items-center gap-2">
                        <button className="flex items-center gap-2 px-4 py-2 bg-primary text-background-dark font-bold rounded-lg text-sm hover:bg-primary/90 transition-all shadow-lg shadow-primary/20">
                            <Share2 size={18} /> <span>Share Intel</span>
                        </button>
                    </div>
                </div>

                <div className="glass-panel p-4 rounded-xl flex gap-4 bg-surface/30">
                    <div className="size-10 rounded-full bg-slate-800 shrink-0 border border-slate-700 flex items-center justify-center">
                        <span className="material-symbols-outlined text-slate-500">person</span>
                    </div>
                    <div className="flex-1">
                        <textarea
                            className="w-full bg-transparent border-none focus:ring-0 p-2 text-white placeholder-slate-600 resize-none h-12"
                            placeholder="What market trends are you seeing?"
                        ></textarea>
                        <div className="flex justify-between items-center mt-2 pt-2 border-t border-slate-800">
                            <div className="flex gap-4">
                                <button className="text-slate-500 hover:text-primary transition-colors flex items-center gap-1.5 text-xs font-bold">
                                    <span className="material-symbols-outlined text-lg">image</span> Photo
                                </button>
                                <button className="text-slate-500 hover:text-primary transition-colors flex items-center gap-1.5 text-xs font-bold">
                                    <span className="material-symbols-outlined text-lg">equalizer</span> Poll
                                </button>
                            </div>
                            <button className="px-4 py-1.5 bg-slate-800 text-slate-400 rounded-lg text-xs font-bold hover:text-white transition-colors">Post</button>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    {loading ? (
                        <div className="text-center py-10 text-slate-500 text-sm font-bold flex flex-col items-center gap-4">
                            <div className="size-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                            Synchronizing AI Intel...
                        </div>
                    ) : marketIntel && marketIntel.length > 0 ? (
                        marketIntel.map((intel, idx) => (
                            <Post
                                key={idx}
                                user="Perplex Brain"
                                role={`AI Agent • ${intel.type.toUpperCase()}`}
                                time={new Date(intel.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                content={intel.content}
                                comments={10 + (idx * 3 % 8)}
                                likes={10 + (idx * 7 % 40)}
                                isBot
                            />
                        ))
                    ) : (
                        <>
                            <Post
                                user="Marcus Sharp"
                                role="Elite Sharp • +114% YTD"
                                time="14m ago"
                                content="Just spotted heavy line movement at Circa. Bills ML moving from -135 to -150 in the last 5 minutes. The model and the money are finally aligning."
                                hasPick={{ player: 'Bills ML', odds: '-135', book: 'Circa' }}
                                comments={12}
                                likes={42}
                                image="https://lh3.googleusercontent.com/aida-public/AB6AXuD-sN1m0r_WnF_r3zG0M1J6Yq7N6J2-l-Z-9-1-P-H-Y-E-l-D-J-K-3-M-h-I-y-0-X-1-N-O-m-0-z-j-D-O-8-z-Y-2-z-S-x-x-0-M-p-c-_-y-y-G-W-x-L-q-T-n-y-4-9-l-g-K-b-U-q-u-a-r-K-6-m-w-i-W-P-n-H-E-6-R-j-O-j-0-8-m-X-5-h_D-7-e-K-t-x-L-h-R-Q-H-N-H-y-h-S-t-J-0-N-E-f-w-P-g-m-H-a-y-W-k-g-Z-K-t-M-y-4-0-x-e-z-_-U-p-5-b-Y-V-h-g-d-t-b-Q-C-1-8-W-N-2-h-p-9-J-W-j-g-F-a-q-0-T-L-N-p-H-n-e-V-u-t-n-E-l-7-w-V-0-v-A-Y-M-G-v-n-i-k-g-k-Y-x-k-e-b-O-H-M-6-L-u-m-m-y-8-B-Z-S-6_d-x-G-3-c-S-X-N-N-n-p-V-1-M-8-I-n-p-h-A"
                            />
                            <Post
                                user="System Bot"
                                role="Brain Notification"
                                time="45m ago"
                                content="Automated Intel: 85% of high-volume bets in the last hour have been on the UNDER for Lakers @ Warriors. Line holding steady at 224.5. Potential value on the OVER if line drops further."
                                comments={4}
                                likes={15}
                                isBot
                            />
                        </>
                    )}
                </div>
            </div>

            {/* Leaderboard Area */}
            <aside className="hidden xl:flex flex-col w-80 shrink-0 space-y-6">
                <div className="glass-panel p-5 rounded-xl border border-primary/20 bg-primary/5">
                    <div className="flex items-center gap-2 text-primary font-bold text-sm mb-4">
                        <TrendingUp size={18} /> Global Sentiment
                    </div>
                    <div className="space-y-4">
                        <SentimentBar label="NFL Over / Under" value={72} label2="OVER" />
                        <SentimentBar label="NBA Home Teams" value={38} label2="HOME" />
                        <SentimentBar label="MLB Underdogs" value={61} label2="DOGS" />
                    </div>
                </div>

                <div className="glass-panel p-5 rounded-xl">
                    <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-6">
                        <Crown size={16} className="text-amber-400" /> Top Sharers
                    </h3>
                    <div className="space-y-4">
                        {[...leaderboard].sort((a, b) => b.profit - a.profit).map((user, idx) => (
                            <LeaderboardItem key={user.name} rank={idx + 1} name={user.name} profit={`+${user.profit}%`} />
                        ))}
                    </div>
                    <button className="w-full mt-6 py-2 text-xs font-bold text-slate-500 hover:text-white transition-colors border-t border-slate-800 pt-4">View All Members</button>
                </div>
            </aside>
        </div>
    );
}

function Post({ user, role, time, content, hasPick, comments, likes, image, isBot }: any) {
    return (
        <div className="glass-panel p-6 rounded-xl space-y-4 hover:border-slate-700 transition-all border border-slate-800/40">
            <div className="flex justify-between items-start">
                <div className="flex items-center gap-3">
                    {isBot ? (
                        <div className="size-10 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                            <ShieldCheck size={20} />
                        </div>
                    ) : (
                        <img src={image} className="size-10 rounded-full border border-slate-700" alt="" />
                    )}
                    <div>
                        <div className="flex items-center gap-1.5">
                            <h4 className="text-sm font-bold text-white">{user}</h4>
                            {isBot && <span className="bg-primary/20 text-primary text-[8px] font-black uppercase tracking-widest px-1 rounded">System Verified</span>}
                        </div>
                        <p className="text-[10px] text-slate-500 font-medium uppercase tracking-wider">{role} • {time}</p>
                    </div>
                </div>
                <button className="text-slate-600 hover:text-white transition-colors">
                    <span className="material-symbols-outlined">more_horiz</span>
                </button>
            </div>

            <p className="text-sm text-slate-300 leading-relaxed">{content}</p>

            {hasPick && (
                <div className="bg-[#121e16] border border-emerald-primary/20 rounded-xl p-4 flex items-center justify-between group cursor-pointer hover:border-emerald-primary/40 transition-all">
                    <div>
                        <p className="text-[10px] font-bold text-emerald-primary uppercase tracking-widest mb-0.5">Recommended Pick</p>
                        <p className="text-base font-bold text-white group-hover:text-emerald-primary transition-colors">{hasPick.player} @ {hasPick.odds}</p>
                    </div>
                    <div className="text-right">
                        <span className="text-[10px] text-slate-500 font-bold uppercase block">{hasPick.book}</span>
                        <span className="text-primary font-bold text-sm">View Analytics</span>
                    </div>
                </div>
            )}

            <div className="flex gap-6 pt-2">
                <button className="flex items-center gap-2 text-slate-500 hover:text-primary transition-colors text-xs font-bold">
                    <ThumbsUp size={16} /> {likes}
                </button>
                <button className="flex items-center gap-2 text-slate-500 hover:text-primary transition-colors text-xs font-bold">
                    <MessageSquare size={16} /> {comments}
                </button>
                <button className="flex items-center gap-2 text-slate-500 hover:text-primary transition-colors text-xs font-bold ml-auto">
                    <Share2 size={16} />
                </button>
            </div>
        </div>
    );
}

function SentimentBar({ label, value, label2 }: any) {
    return (
        <div className="space-y-2">
            <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-widest text-slate-400">
                <span>{label}</span>
                <span className="text-primary">{value}% {label2}</span>
            </div>
            <div className="w-full bg-slate-800/50 h-1 rounded-full overflow-hidden">
                <div className="h-full bg-primary" style={{ width: `${value}%` }}></div>
            </div>
        </div>
    );
}

function LeaderboardItem({ rank, name, profit }: any) {
    return (
        <div className="flex items-center justify-between group cursor-pointer">
            <div className="flex items-center gap-3">
                <span className={`text-xs font-black italic w-4 ${rank === 1 ? 'text-amber-400' : rank === 2 ? 'text-slate-300' : rank === 3 ? 'text-orange-400' : 'text-slate-600'}`}>{rank}</span>
                <div className="size-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[10px] font-bold text-slate-500">
                    {name.charAt(0)}
                </div>
                <span className="text-xs font-bold text-slate-300 group-hover:text-white transition-colors">{name}</span>
            </div>
            <span className="text-xs font-bold text-emerald-primary">{profit}</span>
        </div>
    );
}
