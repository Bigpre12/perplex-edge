"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Users,
    MessageSquare,
    Heart,
    Share2,
    Search,
    Brain,
    ShieldCheck,
    Loader2,
    TrendingUp,
    Plus
} from "lucide-react";
import { getAuthToken, getUser } from "@/lib/auth";
import { API_BASE_URL } from "@/lib/apiConfig";

export default function SharedIntelPage() {
    const [posts, setPosts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [currentUser, setCurrentUser] = useState<any>(null);
    const [showPostModal, setShowPostModal] = useState(false);
    const [newPost, setNewPost] = useState({ title: "", content: "" });
    const [isPosting, setIsPosting] = useState(false);

    useEffect(() => {
        setCurrentUser(getUser());
        fetchFeed();
    }, []);

    const fetchFeed = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/social/feed`);
            if (res.ok) setPosts(await res.json());
        } catch (err) {
            console.error("Failed to fetch community feed:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleLike = async (postId: number) => {
        const token = getAuthToken();
        if (!token) return alert("Please login to interact with posts.");

        try {
            const res = await fetch(`${API_BASE_URL}/social/like/${postId}`, {
                method: "POST",
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (res.ok) {
                setPosts(posts.map(p => p.id === postId ? { ...p, likes_count: p.likes_count + 1 } : p));
            }
        } catch (err) {
            console.error(err);
        }
    };

    const handlePost = async () => {
        if (!newPost.title) return;
        const token = getAuthToken();
        if (!token) return;

        setIsPosting(true);
        try {
            const res = await fetch(`${API_BASE_URL}/social/share`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(newPost)
            });

            if (res.ok) {
                setShowPostModal(false);
                setNewPost({ title: "", content: "" });
                fetchFeed();
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsPosting(false);
        }
    };

    return (
        <div className="flex gap-8">
            {/* Left Feed */}
            <div className="flex-1 space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
                            <Users className="text-primary" /> Community Intelligence
                        </h1>
                        <p className="text-secondary text-sm mt-1">Shared sharp insights and crowdsourced analytics from the Lucrix community.</p>
                    </div>
                    <button
                        onClick={() => setShowPostModal(true)}
                        className="flex items-center gap-2 px-6 py-3 bg-primary text-background-dark font-black rounded-xl text-sm hover:scale-[1.02] active:scale-[0.98] transition-all shadow-lg shadow-primary/20"
                    >
                        <Plus size={18} /> POST INSIGHT
                    </button>
                </div>

                {/* Global Feed */}
                <div className="space-y-4">
                    {loading ? (
                        <div className="h-64 flex items-center justify-center">
                            <Loader2 className="animate-spin text-primary" size={32} />
                        </div>
                    ) : posts.length > 0 ? (
                        posts.map((post, i) => (
                            <motion.div
                                key={post.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.05 }}
                                className="glass-panel p-6 rounded-2xl border-white/[0.05] hover:border-white/10 transition-all group"
                            >
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-center gap-3">
                                        <img
                                            src={`https://ui-avatars.com/api/?name=${encodeURIComponent(post.username)}&background=0df233&color=101f19`}
                                            className="size-10 rounded-full border border-slate-700"
                                            alt=""
                                        />
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <span className="text-sm font-bold text-white hover:text-primary cursor-pointer transition-colors">{post.username}</span>
                                                <ShieldCheck size={14} className="text-primary opacity-60" />
                                            </div>
                                            <p className="text-[10px] text-secondary font-medium">{new Date(post.created_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
                                        </div>
                                    </div>
                                    {post.slip_id && (
                                        <div className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
                                            <span className="text-[10px] font-black text-emerald-500 uppercase flex items-center gap-1.5">
                                                <Share2 size={10} /> SHARED SLIP
                                            </span>
                                        </div>
                                    )}
                                </div>

                                <div className="space-y-3">
                                    <h3 className="text-lg font-black text-white group-hover:text-primary transition-colors leading-tight">
                                        {post.title}
                                    </h3>
                                    <p className="text-sm text-slate-300 leading-relaxed">
                                        {post.content}
                                    </p>
                                </div>

                                <div className="flex items-center gap-6 mt-6 pt-4 border-t border-white/[0.03]">
                                    <button
                                        onClick={() => handleLike(post.id)}
                                        className="flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-red-500 transition-colors"
                                    >
                                        <Heart size={16} className={post.likes_count > 0 ? "fill-red-500 text-red-500" : ""} /> {post.likes_count}
                                    </button>
                                    <button className="flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-primary transition-colors">
                                        <MessageSquare size={16} /> {post.comments_count}
                                    </button>
                                    <button className="flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-white transition-colors ml-auto">
                                        <Share2 size={16} />
                                    </button>
                                </div>
                            </motion.div>
                        ))
                    ) : (
                        <div className="text-center py-20 bg-white/[0.02] rounded-3xl border border-dashed border-slate-700">
                            <p className="text-slate-500 italic">The community is quiet. Be the first to post a sharp insight.</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Right Sidebar */}
            <div className="hidden xl:flex flex-col w-80 shrink-0 space-y-6">
                <div className="glass-panel p-6 rounded-2xl border-white/[0.05]">
                    <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                        <TrendingUp size={16} className="text-primary" /> Trending Intel
                    </h3>
                    <div className="space-y-4">
                        <TrendingTopic title="NBA Player Props" volume="1.2k shared" />
                        <TrendingTopic title="Super Bowl LVIII" volume="4.5k shared" />
                        <TrendingTopic title="UFC 298 Steam Move" volume="842 shared" />
                    </div>
                </div>

                <div className="glass-panel p-6 rounded-2xl border-white/[0.05] bg-gradient-to-br from-[#0c1416] to-[#0a0a0a]">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-primary/20 rounded-lg text-primary">
                            <Brain size={20} />
                        </div>
                        <h3 className="text-sm font-bold text-white uppercase tracking-tight">Wisdom of Crowds</h3>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed italic">
                        "68% of verified analysts are moving towards the OVER on LeBron James points tonight. Crowdsourced efficiency is currently high."
                    </p>
                </div>
            </div>

            {/* Post Modal */}
            <AnimatePresence>
                {showPostModal && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setShowPostModal(false)}
                            className="absolute inset-0 bg-background-dark/80 backdrop-blur-sm"
                        ></motion.div>
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className="relative w-full max-w-lg glass-premium p-8 rounded-3xl border-white/[0.08] shadow-2xl"
                        >
                            <h2 className="text-2xl font-black text-white mb-6">Share Community Intel</h2>
                            <div className="space-y-4">
                                <input
                                    type="text"
                                    placeholder="Catchy Headline (e.g. Sharp move detected on Laker props)"
                                    value={newPost.title}
                                    onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                                    className="w-full bg-white/[0.03] border border-white/[0.08] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-primary/50 transition-colors"
                                />
                                <textarea
                                    placeholder="Share your technical analysis or reasoning..."
                                    rows={6}
                                    value={newPost.content}
                                    onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                                    className="w-full bg-white/[0.03] border border-white/[0.08] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-primary/50 transition-colors resize-none"
                                />
                                <button
                                    onClick={handlePost}
                                    disabled={isPosting}
                                    className="w-full py-4 bg-primary text-background-dark font-black rounded-xl hover:bg-primary/90 transition-all disabled:opacity-50"
                                >
                                    {isPosting ? <Loader2 className="animate-spin mx-auto" /> : "PUBLISH INTELLIGENCE"}
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}

function TrendingTopic({ title, volume }: any) {
    return (
        <div className="p-3 rounded-xl bg-white/[0.02] border border-transparent hover:border-white/5 cursor-pointer transition-all">
            <p className="text-xs font-bold text-slate-200">{title}</p>
            <p className="text-[10px] text-slate-500 font-medium uppercase mt-1">Status: {volume}</p>
        </div>
    );
}
