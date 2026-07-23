"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { Bot, LogIn, AlertCircle, Loader2, Sparkles } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await apiClient.post('/auth/login', { email, password });
      if (res.data.access_token) {
        localStorage.setItem('access_token', res.data.access_token);
        router.push('/conversations');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0e1a] flex flex-col justify-center items-center p-6 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-blue-600/8 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-purple-600/6 rounded-full blur-[100px] pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        {/* Logo & Brand */}
        <div className="flex flex-col items-center mb-8">
          <div className="relative mb-4">
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 p-4 rounded-2xl text-white shadow-2xl shadow-blue-600/30">
              <Bot className="w-8 h-8" />
            </div>
            <div className="absolute -top-1 -right-1 bg-emerald-500 p-1 rounded-full">
              <Sparkles className="w-3 h-3 text-white" />
            </div>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Welcome back
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Sign in to your WhatsApp AI workspace
          </p>
        </div>

        {/* Card */}
        <div className="glass-card p-8">
          {/* Error Alert */}
          {error && (
            <div className="mb-6 p-4 bg-red-950/40 border border-red-800/60 text-red-300 text-sm rounded-xl flex items-start gap-3">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">
                Email Address
              </label>
              <input
                id="login-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@business.com"
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">
                Password
              </label>
              <input
                id="login-password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="input-field"
              />
            </div>

            <button
              id="login-submit"
              type="submit"
              disabled={loading}
              className="w-full btn-primary py-3.5 flex justify-center items-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Authenticating...
                </>
              ) : (
                <>
                  <LogIn className="w-4 h-4" /> Sign In to Dashboard
                </>
              )}
            </button>
          </form>

          {/* Divider & Footer */}
          <div className="mt-8 pt-6 border-t border-slate-700/50 text-center">
            <p className="text-sm text-slate-400">
              Don&apos;t have an account?{' '}
              <Link href="/register" className="text-blue-400 hover:text-blue-300 font-semibold transition-colors">
                Register Business
              </Link>
            </p>
          </div>
        </div>

        {/* Bottom tag */}
        <p className="text-center text-xs text-slate-600 mt-6">
          Powered by Gemini AI &middot; Enterprise WhatsApp Automation
        </p>
      </div>
    </div>
  );
}
