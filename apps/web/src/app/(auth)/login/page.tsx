"use client";

import React, { useState, useRef } from "react";
import { motion } from "framer-motion";
import { User, Lock, ArrowRight, ShieldCheck, Cpu } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { authStorage } from "@/lib/auth";
import API from "@/lib/api";

export default function LoginPage() {
    const router = useRouter();
    const emailRef = useRef<HTMLInputElement>(null);
    const passwordRef = useRef<HTMLInputElement>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        // Read directly from DOM elements to capture browser autofill values
        const email = emailRef.current?.value || "";
        const password = passwordRef.current?.value || "";

        if (!email || !password) {
            setError("Please enter your email and password");
            setLoading(false);
            return;
        }

        try {
            const data: any = await API.auth.login({
                email,
                password
            });
            // Backend may return accessToken (simple) or access_token (legacy)
            const token = data?.accessToken || data?.access_token;
            if (data?.error || !token) {
                throw new Error(data?.error || data?.detail || "Login failed — check your credentials");
            }
            // Save token for both authStorage AND apiFetch
            authStorage.saveToken(token);
            localStorage.setItem("accessToken", token); // apiFetch reads this key
            if (data.user) authStorage.saveUser(data.user);
            // Hard redirect to dashboard
            window.location.href = "/dashboard";
        } catch (err: any) {
            // Don't redirect on login errors - just show the error
            const msg = err?.response?.data?.detail || err?.message || "Cannot connect to server — make sure backend is running";
            setError(msg);
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
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-md z-10"
            >
                <div className="bg-[#0c0c0c]/80 backdrop-blur-3xl border border-white/10 rounded-[32px] p-10 shadow-2xl relative">
                    <div className="mb-10 text-center">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 mb-6 shadow-xl shadow-blue-600/20">
                            <ShieldCheck className="w-8 h-8 text-white" />
                        </div>
                        <h1 className="text-4xl font-black text-white tracking-tight">Welcome Back</h1>
                        <p className="text-white/40 mt-3 font-medium">Access your personalized edge engine</p>
                    </div>
                    {error && (
                        <motion.div
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="mb-8 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-400 text-sm text-center font-medium"
                        >
                            {error}
                        </motion.div>
                    )}
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-3">
                            <div className="relative group">
                                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/20 group-focus-within:text-blue-500 transition-colors" />
                                <input
                                    ref={emailRef}
                                    type="email"
                                    name="email"
                                    autoComplete="email"
                                    required
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-6 text-white placeholder:text-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500/50 transition-all font-medium"
                                    placeholder="Email Address"
                                />
                            </div>
                        </div>
                        <div className="space-y-3">
                            <div className="relative group">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/20 group-focus-within:text-blue-500 transition-colors" />
                                <input
                                    ref={passwordRef}
                                    type="password"
                                    name="password"
                                    autoComplete="current-password"
                                    required
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-6 text-white placeholder:text-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500/50 transition-all font-medium"
                                    placeholder="Password"
                                />
                            </div>
                            <div className="flex justify-end">
                                <Link
                                    href="/forgot-password"
                                    className="text-xs font-semibold text-blue-500/60 hover:text-blue-500 transition-colors"
                                >
                                    Forgot Credentials?
                                </Link>
                            </div>
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-4 rounded-2xl shadow-xl shadow-blue-500/30 flex items-center justify-center gap-3 group transition-all active:scale-[0.98] disabled:opacity-50"
                        >
                            {loading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <>
                                    <Cpu className="w-5 h-5" />
                                    Start Neural Engine
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>
                    <div className="mt-10 pt-8 border-t border-white/5 text-center">
                        <p className="text-white/30 text-sm font-medium">
                            New to the platform?{" "}
                            <Link href="/signup" className="text-blue-400 hover:text-blue-300 transition-colors ml-1 font-bold">
                                Create Account
                            </Link>
                        </p>
                    </div>
                </div>
                {/* Footnote */}
                <div className="mt-8 text-center">
                    <p className="text-white/10 text-[10px] uppercase tracking-[4px] font-black">
                        Secured by Lucrix Quantum Auth
                    </p>
                </div>
            </motion.div>
        </div>
    );
}
