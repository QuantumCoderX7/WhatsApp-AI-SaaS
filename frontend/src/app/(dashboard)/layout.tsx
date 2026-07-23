"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Bot, MessageSquare, Package, BookOpen, ShoppingBag, LogOut,
  LayoutDashboard, Sparkles
} from 'lucide-react';

const navItems = [
  { href: '/',              label: 'Dashboard',       icon: LayoutDashboard, color: 'text-sky-400' },
  { href: '/conversations', label: 'Conversations',   icon: MessageSquare,   color: 'text-blue-400' },
  { href: '/inventory',     label: 'Catalog & Stock', icon: Package,         color: 'text-emerald-400' },
  { href: '/knowledge-base',label: 'Knowledge Base',  icon: BookOpen,        color: 'text-purple-400' },
  { href: '/orders',        label: 'Orders',          icon: ShoppingBag,     color: 'text-amber-400' },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen bg-[#0a0e1a] text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-[260px] shrink-0 bg-slate-900/50 backdrop-blur-xl border-r border-slate-700/40 flex flex-col">
        {/* Brand */}
        <div className="p-5 border-b border-slate-700/40">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="bg-gradient-to-br from-blue-600 to-blue-700 p-2.5 rounded-xl text-white shadow-lg shadow-blue-600/20">
                <Bot className="w-5 h-5" />
              </div>
              <div className="absolute -top-0.5 -right-0.5 bg-emerald-500 w-2.5 h-2.5 rounded-full border-2 border-slate-900" />
            </div>
            <div>
              <h1 className="font-bold text-sm text-white leading-tight">WhatsApp AI</h1>
              <div className="flex items-center gap-1 mt-0.5">
                <Sparkles className="w-3 h-3 text-amber-400" />
                <span className="text-[10px] text-slate-400 font-medium">Enterprise Platform</span>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          <p className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold px-4 py-2">
            Navigation
          </p>
          {navItems.map((item) => {
            const isActive = pathname === item.href || 
              (item.href !== '/' && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20 shadow-sm'
                    : 'text-slate-400 hover:bg-white/5 hover:text-white'
                }`}
              >
                <item.icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : item.color}`} />
                {item.label}
                {isActive && (
                  <div className="ml-auto w-1.5 h-1.5 bg-blue-400 rounded-full glow-pulse" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-3 border-t border-slate-700/40">
          <button
            id="sign-out-btn"
            onClick={() => {
              if (typeof window !== 'undefined') {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
              }
            }}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-800/50 hover:bg-red-950/50 hover:text-red-400 hover:border-red-800/40 text-slate-400 rounded-xl text-xs font-semibold transition-all duration-300 border border-slate-700/40"
          >
            <LogOut className="w-4 h-4" /> Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
