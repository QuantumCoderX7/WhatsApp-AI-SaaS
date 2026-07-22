"use client";

import React from 'react';
import Link from 'next/link';
import { Bot, MessageSquare, Package, BookOpen, ShoppingBag, Settings, LogOut } from 'lucide-react';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Sidebar Navigation */}
      <aside className="w-64 border-r border-slate-800 bg-slate-900 flex flex-col justify-between">
        <div>
          {/* Logo Header */}
          <div className="p-6 border-b border-slate-800 flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-xl text-white">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-bold text-sm text-slate-100">WhatsApp AI SaaS</h1>
              <span className="text-[10px] text-blue-400 font-mono">Enterprise Tenant</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1">
            <Link
              href="/conversations"
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition"
            >
              <MessageSquare className="w-4 h-4 text-blue-400" /> Conversations Inbox
            </Link>
            <Link
              href="/inventory"
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition"
            >
              <Package className="w-4 h-4 text-emerald-400" /> Catalog & Stock
            </Link>
            <Link
              href="/knowledge-base"
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition"
            >
              <BookOpen className="w-4 h-4 text-purple-400" /> RAG Knowledge Base
            </Link>
            <Link
              href="/orders"
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition"
            >
              <ShoppingBag className="w-4 h-4 text-amber-400" /> Orders & Checkout
            </Link>
          </nav>
        </div>

        {/* Footer Logout */}
        <div className="p-4 border-t border-slate-800">
          <button
            onClick={() => {
              if (typeof window !== 'undefined') {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
              }
            }}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-slate-800 hover:bg-red-950 hover:text-red-400 text-slate-300 rounded-xl text-xs font-semibold transition"
          >
            <LogOut className="w-4 h-4" /> Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content View */}
      <main className="flex-1 p-8 overflow-y-auto">{children}</main>
    </div>
  );
}
