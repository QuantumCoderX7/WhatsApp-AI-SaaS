"use client";

import React from 'react';
import { MessageSquare, Bot, Package, ShoppingBag, ArrowUpRight } from 'lucide-react';
import Link from 'next/link';

export default function DashboardOverview() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-100">Tenant Analytics Overview</h1>
        <p className="text-sm text-slate-400">
          Real-time performance metrics for WhatsApp AI Customer Support & Sales Automation.
        </p>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
          <div className="flex justify-between items-center mb-4">
            <span className="text-xs font-semibold text-slate-400">Total WhatsApp Messages</span>
            <MessageSquare className="w-5 h-5 text-blue-400" />
          </div>
          <div className="text-3xl font-extrabold text-slate-100">1,248</div>
          <span className="text-[11px] text-emerald-400 flex items-center gap-1 mt-2">
            <ArrowUpRight className="w-3 h-3" /> +18.4% this month
          </span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
          <div className="flex justify-between items-center mb-4">
            <span className="text-xs font-semibold text-slate-400">AI Resolution Rate</span>
            <Bot className="w-5 h-5 text-purple-400" />
          </div>
          <div className="text-3xl font-extrabold text-slate-100">94.2%</div>
          <span className="text-[11px] text-emerald-400 flex items-center gap-1 mt-2">
            <ArrowUpRight className="w-3 h-3" /> 5.8% escalated to human
          </span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
          <div className="flex justify-between items-center mb-4">
            <span className="text-xs font-semibold text-slate-400">Active SKUs Listed</span>
            <Package className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-slate-100">42</div>
          <span className="text-[11px] text-slate-400 mt-2 block">Zero stock collisions</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
          <div className="flex justify-between items-center mb-4">
            <span className="text-xs font-semibold text-slate-400">Orders Processed</span>
            <ShoppingBag className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-slate-100">$8,450.00</div>
          <span className="text-[11px] text-emerald-400 flex items-center gap-1 mt-2">
            <ArrowUpRight className="w-3 h-3" /> 14 orders automated
          </span>
        </div>
      </div>

      {/* Action Shortcut Banner */}
      <div className="bg-gradient-to-r from-blue-900/40 to-slate-900 border border-blue-800/50 p-8 rounded-2xl flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Open Live Agent Workspace</h2>
          <p className="text-xs text-slate-400 mt-1">
            Monitor active customer WhatsApp chats in real-time or take over manually.
          </p>
        </div>
        <Link
          href="/conversations"
          className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-bold text-xs transition shadow-lg flex items-center gap-2"
        >
          Go to Inbox <ArrowUpRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
