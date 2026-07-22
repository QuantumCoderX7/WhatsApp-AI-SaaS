"use client";

import React from 'react';
import { LiveInbox } from '@/components/chat/LiveInbox';

export default function ConversationsPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Live Agent Workspace</h1>
        <p className="text-xs text-slate-400">
          Monitor automated Gemini AI customer interactions and toggle human agent takeover in real-time.
        </p>
      </div>

      <LiveInbox />
    </div>
  );
}
