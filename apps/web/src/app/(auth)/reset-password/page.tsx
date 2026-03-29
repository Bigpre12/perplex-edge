"use client";
import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Lock, CheckCircle, ShieldAlert, Cpu } from "lucide-react";
import Link from "next/link";
import API from "@/lib/api";

// ── Presentational form component ──────────────────────────────────────────
function ResetPasswordForm({
  token, password, setPassword, confirmPassword, setConfirmPassword,
  loading, success, error, handleSubmit,
}: any) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a0a0f] relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-950/20 via-transparent to-purple-950/20 pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 w-full max-w-md px-6"
      >
        <div className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-xl">
          <div className="flex justify-center mb-6">
            <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20">
              <Cpu className="w-8 h-8 text-blue-400" />
            </div>
          </div>

          <h1 className="text-2xl font-bold text-white text-center mb-1">Set New Password</h1>
          <p className="text-white/40 text-sm text-center mb-6">Secure your neural engine access</p>

          {success ? (
            <div className="flex flex-col items-center gap-3 py-6">
              <CheckCircle className="w-12 h-12 text-green-400" />
              <p className="text-white font-semibold">Password Updated!</p>
              <p className="text-white/40 text-sm">Redirecting to login...</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3"
                >
                  <ShieldAlert className="w-4 h-4 text-red-400 shrink-0" />
                  <p className="text-red-300 text-sm">{error}</p>
                </motion.div>
              )}

              {!token ? (
                <div className="text-center py-4">
                  <Link
                    href="/forgot-password"
                    className="text-blue-400 hover:text-blue-300 transition-colors text-sm"
                  >
                    Request New Link
                  </Link>
                </div>
              ) : (
                <>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                    <input
                      type="password"
                      required
                      minLength={8}
                      className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-6 text-white placeholder:text-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500/50 transition-all font-medium"
                      placeholder="New Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </div>

                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                    <input
                      type="password"
                      required
                      minLength={8}
                      className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-6 text-white placeholder:text-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500/50 transition-all font-medium"
                      placeholder="Confirm Password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-50 text-white font-semibold rounded-2xl py-4 flex items-center justify-center gap-2 transition-all"
                  >
                    {loading ? (
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                      "Update Password"
                    )}
                  </button>
                </>
              )}
            </form>
          )}

          <div className="flex items-center justify-center gap-1.5 mt-6">
            <ShieldAlert className="w-3 h-3 text-white/20" />
            <p className="text-xs text-white/20">Secured by Lucrix Quantum Auth</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

// ── Container component (hooks + logic) ────────────────────────────────────
function ResetPasswordContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) setError("Invalid reset link. Please request a new one.");
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await API.auth.resetPassword({ token: token!, new_password: password });
      setSuccess(true);
      setTimeout(() => router.push("/login"), 3000);
    } catch (err: any) {
      setError(err.message || "Failed to reset password. The link may be expired.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ResetPasswordForm
      token={token}
      password={password}
      setPassword={setPassword}
      confirmPassword={confirmPassword}
      setConfirmPassword={setConfirmPassword}
      loading={loading}
      success={success}
      error={error}
      handleSubmit={handleSubmit}
    />
  );
}

// ── Page export (Suspense required for useSearchParams) ────────────────────
export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-white/20 border-t-blue-400 rounded-full animate-spin" />
      </div>
    }>
      <ResetPasswordContent />
    </Suspense>
  );
}
