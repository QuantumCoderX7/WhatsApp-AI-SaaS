"use client";

import React from 'react';
import { LiveInbox } from '@/components/chat/LiveInbox';
import { MessageSquare } from 'lucide-react';

export default function ConversationsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="bg-gradient-to-br from-blue-600 to-cyan-600 p-2 rounded-lg">
          <MessageSquare className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Live Agent Workspace</h1>
          <p className="text-sm text-slate-400">
            Monitor Gemini AI conversations and take over in real-time
          </p>
        </div>
      </div>
      <LiveInbox />
    </div>
  );
}
