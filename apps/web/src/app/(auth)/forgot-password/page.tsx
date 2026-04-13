"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Mail, ArrowLeft, ShieldCheck, Send } from "lucide-react";
import Link from "next/link";
import API from "@/lib/api";

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        setMessage("");

        try {
            await API.auth.forgotPassword({ email });
            setMessage("Check your inbox — if that email exists, we've sent a reset link.");
        } catch (err: any) {
            setError(err.message || "Something went wrong. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4 relative overflow-hidden">
            {/* Dynamic Background */}
            <div className="absolute top-0 left-0 w-full h-full">
                <div className="absolute top-[10%] left-[20%] w-64 h-64 bg-blue-500/10 blur-[100px] rounded-full" />
                <div className="absolute bottom-[20%] right-[10%] w-96 h-96 bg-indigo-500/5 blur-[120px] rounded-full" />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md z-10"
            >
                <div className="bg-[#0c0c0c]/80 backdrop-blur-3xl border border-white/10 rounded-[32px] p-10 shadow-2xl relative">
                    
                    <div className="mb-10 text-center">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 mb-6 shadow-xl shadow-blue-600/20">
                            <ShieldCheck className="w-8 h-8 text-white" />
                        </div>
                        <h1 className="text-3xl font-black text-white tracking-tight">Recover Access</h1>
                        <p className="text-white/40 mt-3 font-medium">We'll send a reset link to your email</p>
                    </div>

                    {message ? (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="bg-blue-500/10 border border-blue-500/20 rounded-2xl p-6 text-center"
                        >
                            <Send className="w-10 h-10 text-blue-500 mx-auto mb-4" />
                            <p className="text-white font-semibold text-lg">{message}</p>
                            <Link 
                                href="/login" 
                                className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors mt-6 font-bold"
                            >
                                <ArrowLeft className="w-4 h-4" /> Back to Login
                            </Link>
                        </motion.div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            {error && (
                                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-400 text-sm text-center font-medium">
                                    {error}
                                </div>
                            )}

                            <div className="relative group">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/20 group-focus-within:text-blue-500 transition-colors" />
                                <input
                                    type="email"
                                    required
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-6 text-white placeholder:text-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500/50 transition-all font-medium"
                                    placeholder="Enter your email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-4 rounded-2xl shadow-xl shadow-blue-500/30 flex items-center justify-center gap-3 transition-all active:scale-[0.98] disabled:opacity-50"
                            >
                                {loading ? (
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                ) : (
                                    <>
                                        Send Reset Link
                                        <Send className="w-5 h-5" />
                                    </>
                                )}
                            </button>

                            <div className="text-center">
                                <Link 
                                    href="/login" 
                                    className="inline-flex items-center gap-2 text-white/30 hover:text-white/60 transition-colors text-sm font-bold"
                                >
                                    <ArrowLeft className="w-4 h-4" /> Wait, I remember it!
                                </Link>
                            </div>
                        </form>
                    )}
                </div>

                <div className="mt-8 text-center">
                    <p className="text-white/10 text-[10px] uppercase tracking-[4px] font-black">
                        Secured by Lucrix Quantum Auth
                    </p>
                </div>
            </motion.div>
        </div>
    );
}
