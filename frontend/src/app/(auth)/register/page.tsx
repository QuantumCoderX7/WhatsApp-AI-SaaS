"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { Bot, UserPlus, AlertCircle, Loader2, Building2 } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const [tenantName, setTenantName] = useState('');
  const [tenantSlug, setTenantSlug] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSlugAutoFill = (val: string) => {
    setTenantName(val);
    setTenantSlug(val.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, ''));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await apiClient.post('/auth/register', {
        tenant_name: tenantName,
        tenant_slug: tenantSlug,
        full_name: fullName,
        email,
        password,
      });

      if (res.data.access_token) {
        localStorage.setItem('access_token', res.data.access_token);
        router.push('/conversations');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please check your inputs.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0e1a] flex flex-col justify-center items-center p-6 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-20 right-1/4 w-[500px] h-[500px] bg-purple-600/6 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-20 left-1/4 w-[400px] h-[400px] bg-blue-600/8 rounded-full blur-[100px] pointer-events-none" />

      <div className="w-full max-w-lg relative z-10">
        {/* Logo & Brand */}
        <div className="flex flex-col items-center mb-8">
          <div className="relative mb-4">
            <div className="bg-gradient-to-br from-purple-600 to-blue-600 p-4 rounded-2xl text-white shadow-2xl shadow-purple-600/30">
              <Building2 className="w-8 h-8" />
            </div>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Create your workspace
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Set up your WhatsApp AI automation in minutes
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

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">
                  Business Name
                </label>
                <input
                  id="register-business-name"
                  type="text"
                  required
                  value={tenantName}
                  onChange={(e) => handleSlugAutoFill(e.target.value)}
                  placeholder="Acme Electronics"
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">
                  Tenant Slug
                </label>
                <input
                  id="register-tenant-slug"
                  type="text"
                  required
                  value={tenantSlug}
                  onChange={(e) => setTenantSlug(e.target.value)}
                  placeholder="acme-electronics"
                  className="input-field font-mono text-xs"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">
                Admin Full Name
              </label>
              <input
                id="register-full-name"
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="John Doe"
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">
                Admin Email
              </label>
              <input
                id="register-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="john@acme.com"
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">
                Password
              </label>
              <input
                id="register-password"
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimum 8 characters"
                className="input-field"
              />
            </div>

            <button
              id="register-submit"
              type="submit"
              disabled={loading}
              className="w-full btn-primary py-3.5 flex justify-center items-center gap-2 disabled:opacity-50 mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Creating workspace...
                </>
              ) : (
                <>
                  <UserPlus className="w-4 h-4" /> Create Workspace
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-slate-700/50 text-center">
            <p className="text-sm text-slate-400">
              Already have an account?{' '}
              <Link href="/login" className="text-blue-400 hover:text-blue-300 font-semibold transition-colors">
                Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
