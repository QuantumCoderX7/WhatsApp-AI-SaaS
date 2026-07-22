"use client";

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Conversation, Message } from '@/types/domain';
import { Send, UserCheck, Bot, User, AlertCircle, RefreshCw } from 'lucide-react';

export function LiveInbox() {
  const queryClient = useQueryClient();
  const [selectedConvId, setSelectedConvId] = useState<string | null>(null);
  const [inputMessage, setInputMessage] = useState('');

  // 1. Fetch Tenant Conversations List
  const { data: conversations = [], isLoading: isLoadingConvs } = useQuery<Conversation[]>({
    queryKey: ['conversations'],
    queryFn: async () => {
      const res = await apiClient.get('/conversations');
      return res.data;
    },
    refetchInterval: 3000, // Poll every 3 seconds
  });

  // Automatically select first conversation if none selected
  const activeConversation = conversations.find((c) => c.id === selectedConvId) || conversations[0];
  const activeConvId = activeConversation?.id;

  // 2. Fetch Chat History Messages for Active Conversation
  const { data: messages = [], isLoading: isLoadingMsgs } = useQuery<Message[]>({
    queryKey: ['messages', activeConvId],
    queryFn: async () => {
      if (!activeConvId) return [];
      const res = await apiClient.get(`/conversations/${activeConvId}/messages`);
      return res.data;
    },
    enabled: !!activeConvId,
    refetchInterval: 2000, // Poll active chat every 2s
  });

  // 3. Toggle Human Handoff Takeover Mutation
  const handoffMutation = useMutation({
    mutationFn: async (action: 'takeover' | 'resume_ai') => {
      if (!activeConvId) return;
      await apiClient.post(`/conversations/${activeConvId}/handoff`, { action });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      queryClient.invalidateQueries({ queryKey: ['messages', activeConvId] });
    },
  });

  return (
    <div className="flex h-[calc(100vh-100px)] border border-gray-800 rounded-xl overflow-hidden bg-slate-950 text-slate-100 shadow-2xl">
      {/* Sidebar - Conversations List */}
      <div className="w-1/3 border-r border-gray-800 flex flex-col bg-slate-900">
        <div className="p-4 border-b border-gray-800 flex justify-between items-center">
          <h2 className="font-bold text-lg text-slate-100 flex items-center gap-2">
            <Bot className="w-5 h-5 text-blue-400" /> WhatsApp Inbox
          </h2>
          <span className="text-xs bg-blue-900/50 text-blue-300 px-2 py-1 rounded-full border border-blue-700">
            {conversations.length} Active
          </span>
        </div>

        <div className="flex-1 overflow-y-auto divide-y divide-gray-800/50">
          {isLoadingConvs ? (
            <div className="p-8 text-center text-slate-500 flex justify-center items-center gap-2">
              <RefreshCw className="animate-spin w-4 h-4" /> Loading conversations...
            </div>
          ) : conversations.length === 0 ? (
            <div className="p-8 text-center text-slate-500">No active customer chats found.</div>
          ) : (
            conversations.map((conv) => {
              const isSelected = conv.id === activeConvId;
              const isEscalated = conv.status === 'HUMAN_ESCALATED';

              return (
                <button
                  key={conv.id}
                  onClick={() => setSelectedConvId(conv.id)}
                  className={`w-full text-left p-4 transition-all duration-150 flex flex-col gap-1 ${
                    isSelected ? 'bg-slate-800 border-l-4 border-blue-500' : 'hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-sm text-slate-200">
                      {conv.customer_name || conv.customer_phone}
                    </span>
                    <span
                      className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full font-bold ${
                        isEscalated
                          ? 'bg-amber-950 text-amber-400 border border-amber-800'
                          : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                      }`}
                    >
                      {isEscalated ? 'Human Mode' : 'AI Active'}
                    </span>
                  </div>
                  <span className="text-xs text-slate-400 font-mono">{conv.customer_phone}</span>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Main Workspace - Chat Area */}
      <div className="flex-1 flex flex-col bg-slate-950">
        {activeConversation ? (
          <>
            {/* Header */}
            <div className="p-4 border-b border-gray-800 flex justify-between items-center bg-slate-900">
              <div>
                <h3 className="font-bold text-slate-100 flex items-center gap-2">
                  {activeConversation.customer_name || activeConversation.customer_phone}
                </h3>
                <span className="text-xs text-slate-400 font-mono">
                  Phone: {activeConversation.customer_phone}
                </span>
              </div>

              {/* Handoff Toggle Button */}
              {activeConversation.status === 'HUMAN_ESCALATED' ? (
                <button
                  onClick={() => handoffMutation.mutate('resume_ai')}
                  disabled={handoffMutation.isPending}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 shadow-lg"
                >
                  <Bot className="w-4 h-4" /> Resume AI Automation
                </button>
              ) : (
                <button
                  onClick={() => handoffMutation.mutate('takeover')}
                  disabled={handoffMutation.isPending}
                  className="bg-amber-600 hover:bg-amber-500 text-white px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 shadow-lg"
                >
                  <UserCheck className="w-4 h-4" /> Take Over (Pause AI)
                </button>
              )}
            </div>

            {/* Chat Messages Log */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-950">
              {isLoadingMsgs ? (
                <div className="text-center text-slate-500">Loading chat history...</div>
              ) : (
                messages.map((msg) => {
                  const isCustomer = msg.sender_type === 'CUSTOMER';
                  const isAI = msg.sender_type === 'AI';
                  const isSystem = msg.sender_type === 'SYSTEM';

                  if (isSystem) {
                    return (
                      <div key={msg.id} className="text-center my-2">
                        <span className="text-[11px] bg-slate-900 text-slate-400 border border-slate-800 px-3 py-1 rounded-full italic">
                          {msg.content}
                        </span>
                      </div>
                    );
                  }

                  return (
                    <div
                      key={msg.id}
                      className={`flex ${isCustomer ? 'justify-start' : 'justify-end'}`}
                    >
                      <div
                        className={`max-w-md p-4 rounded-2xl text-sm shadow-md ${
                          isCustomer
                            ? 'bg-slate-800 text-slate-100 rounded-tl-none border border-slate-700'
                            : isAI
                            ? 'bg-blue-600 text-white rounded-tr-none'
                            : 'bg-amber-600 text-white rounded-tr-none'
                        }`}
                      >
                        <div className="text-[10px] font-bold opacity-75 mb-1 flex items-center gap-1">
                          {isCustomer ? <User className="w-3 h-3" /> : <Bot className="w-3 h-3" />}
                          {msg.sender_type}
                        </div>
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                        <div className="text-[9px] text-right opacity-60 mt-1">
                          {new Date(msg.created_at).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col justify-center items-center text-slate-500">
            <AlertCircle className="w-12 h-12 mb-2 text-slate-700" />
            <p>Select a conversation from the sidebar to start live agent monitoring.</p>
          </div>
        )}
      </div>
    </div>
  );
}
