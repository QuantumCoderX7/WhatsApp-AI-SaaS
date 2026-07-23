"use client";

import React, { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Conversation, Message } from '@/types/domain';
import {
  Send, UserCheck, Bot, User, AlertCircle, RefreshCw,
  Phone, Clock, MessageSquare, Sparkles, Shield, Loader2
} from 'lucide-react';

export function LiveInbox() {
  const queryClient = useQueryClient();
  const [selectedConvId, setSelectedConvId] = useState<string | null>(null);
  const [inputMessage, setInputMessage] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Fetch Conversations
  const { data: conversations = [], isLoading: isLoadingConvs } = useQuery<Conversation[]>({
    queryKey: ['conversations'],
    queryFn: async () => {
      const res = await apiClient.get('/conversations');
      return res.data;
    },
    refetchInterval: 3000,
  });

  const activeConversation = conversations.find((c) => c.id === selectedConvId) || conversations[0];
  const activeConvId = activeConversation?.id;

  // Fetch Messages
  const { data: messages = [], isLoading: isLoadingMsgs } = useQuery<Message[]>({
    queryKey: ['messages', activeConvId],
    queryFn: async () => {
      if (!activeConvId) return [];
      const res = await apiClient.get(`/conversations/${activeConvId}/messages`);
      return res.data;
    },
    enabled: !!activeConvId,
    refetchInterval: 2000,
  });

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handoff Mutation (Take over / Resume AI)
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

  // Send Human Agent Outbound Message Mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (content: string) => {
      if (!activeConvId || !content.trim()) return;
      await apiClient.post(`/conversations/${activeConvId}/send-message`, { content: content.trim() });
    },
    onSuccess: () => {
      setInputMessage('');
      queryClient.invalidateQueries({ queryKey: ['messages', activeConvId] });
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputMessage.trim() && !sendMessageMutation.isPending) {
      sendMessageMutation.mutate(inputMessage);
    }
  };

  const formatTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="flex h-[calc(100vh-140px)] glass-card overflow-hidden">
      {/* Sidebar - Conversations List */}
      <div className="w-[340px] shrink-0 border-r border-slate-700/40 flex flex-col bg-slate-900/30">
        <div className="p-4 border-b border-slate-700/40">
          <div className="flex justify-between items-center">
            <h2 className="font-bold text-base text-white flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-blue-400" />
              Inbox
            </h2>
            <span className="badge bg-blue-500/15 text-blue-400 border border-blue-500/20">
              {conversations.length} active
            </span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {isLoadingConvs ? (
            <div className="p-6 text-center text-slate-500 flex flex-col items-center gap-2">
              <RefreshCw className="animate-spin w-5 h-5" />
              <span className="text-sm">Loading chats...</span>
            </div>
          ) : conversations.length === 0 ? (
            <div className="p-8 text-center">
              <div className="bg-slate-800/50 p-4 rounded-2xl inline-block mb-3">
                <MessageSquare className="w-8 h-8 text-slate-600" />
              </div>
              <p className="text-sm text-slate-500">No active conversations</p>
              <p className="text-xs text-slate-600 mt-1">
                Messages from customers will automatically appear here
              </p>
            </div>
          ) : (
            <div className="divide-y divide-slate-700/30">
              {conversations.map((conv) => {
                const isSelected = conv.id === activeConvId;
                const isEscalated = conv.status === 'HUMAN_ESCALATED';

                return (
                  <button
                    key={conv.id}
                    onClick={() => setSelectedConvId(conv.id)}
                    className={`w-full text-left p-4 transition-all duration-200 ${
                      isSelected
                        ? 'bg-blue-600/10 border-l-2 border-blue-500'
                        : 'hover:bg-white/3 border-l-2 border-transparent'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-2">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                          isEscalated ? 'bg-amber-600/20 text-amber-400' : 'bg-blue-600/20 text-blue-400'
                        }`}>
                          {(conv.customer_name || conv.customer_phone || '?')[0].toUpperCase()}
                        </div>
                        <div>
                          <span className="font-semibold text-sm text-slate-200 block leading-tight">
                            {conv.customer_name || conv.customer_phone}
                          </span>
                          <span className="text-xs text-slate-500 font-mono flex items-center gap-1">
                            <Phone className="w-3 h-3" />
                            {conv.customer_phone}
                          </span>
                        </div>
                      </div>
                      <span
                        className={`badge ${
                          isEscalated
                            ? 'bg-amber-500/15 text-amber-400 border border-amber-500/20'
                            : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
                        }`}
                      >
                        {isEscalated ? 'Human' : 'AI'}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Main Workspace - Chat Area */}
      <div className="flex-1 flex flex-col bg-[#0a0e1a]/60">
        {activeConversation ? (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b border-slate-700/40 flex justify-between items-center bg-slate-900/30 backdrop-blur-sm">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold ${
                  activeConversation.status === 'HUMAN_ESCALATED'
                    ? 'bg-amber-600/20 text-amber-400'
                    : 'bg-blue-600/20 text-blue-400'
                }`}>
                  {(activeConversation.customer_name || activeConversation.customer_phone || '?')[0].toUpperCase()}
                </div>
                <div>
                  <h3 className="font-semibold text-white text-sm">
                    {activeConversation.customer_name || activeConversation.customer_phone}
                  </h3>
                  <span className="text-xs text-slate-400 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {activeConversation.status === 'HUMAN_ESCALATED' ? 'Human agent active' : 'AI agent handling'}
                  </span>
                </div>
              </div>

              {/* Handoff Toggle Button */}
              {activeConversation.status === 'HUMAN_ESCALATED' ? (
                <button
                  onClick={() => handoffMutation.mutate('resume_ai')}
                  disabled={handoffMutation.isPending}
                  className="flex items-center gap-2 px-4 py-2 bg-emerald-600/15 hover:bg-emerald-600/25 text-emerald-400 border border-emerald-500/30 rounded-xl text-xs font-semibold transition-all duration-200"
                >
                  <Sparkles className="w-3.5 h-3.5" /> Resume AI
                </button>
              ) : (
                <button
                  onClick={() => handoffMutation.mutate('takeover')}
                  disabled={handoffMutation.isPending}
                  className="flex items-center gap-2 px-4 py-2 bg-amber-600/15 hover:bg-amber-600/25 text-amber-400 border border-amber-500/30 rounded-xl text-xs font-semibold transition-all duration-200"
                >
                  <Shield className="w-3.5 h-3.5" /> Take Over (Pause AI)
                </button>
              )}
            </div>

            {/* Chat Messages Stream */}
            <div className="flex-1 overflow-y-auto p-6 space-y-3">
              {isLoadingMsgs ? (
                <div className="flex justify-center items-center h-32">
                  <RefreshCw className="animate-spin w-5 h-5 text-slate-500" />
                </div>
              ) : messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-slate-500">
                  <MessageSquare className="w-10 h-10 mb-2 text-slate-700" />
                  <p className="text-sm">No messages yet</p>
                </div>
              ) : (
                messages.map((msg) => {
                  const isCustomer = msg.sender_type === 'CUSTOMER';
                  const isAI = msg.sender_type === 'AI';
                  const isSystem = msg.sender_type === 'SYSTEM';

                  if (isSystem) {
                    return (
                      <div key={msg.id} className="flex justify-center my-2">
                        <span className="text-[11px] bg-slate-800/60 text-slate-400 border border-slate-700/40 px-4 py-1.5 rounded-full">
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
                        className={`max-w-[70%] p-3.5 rounded-2xl text-sm leading-relaxed ${
                          isCustomer
                            ? 'bg-slate-800/80 text-slate-100 rounded-bl-md border border-slate-700/40'
                            : isAI
                            ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-br-md shadow-lg shadow-blue-600/10'
                            : 'bg-gradient-to-br from-amber-600 to-amber-700 text-white rounded-br-md shadow-lg shadow-amber-600/10'
                        }`}
                      >
                        <div className="flex items-center gap-1.5 mb-1 opacity-70">
                          {isCustomer ? <User className="w-3 h-3" /> : <Bot className="w-3 h-3" />}
                          <span className="text-[10px] font-semibold uppercase tracking-wider">
                            {isCustomer ? 'Customer' : isAI ? 'AI Agent' : 'Human Agent'}
                          </span>
                        </div>
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                        <div className="text-[10px] text-right opacity-50 mt-1.5">
                          {formatTime(msg.created_at)}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Bottom Message Input / Composer Section */}
            <div className="p-4 border-t border-slate-700/40 bg-slate-900/40 backdrop-blur-sm">
              {activeConversation.status === 'HUMAN_ESCALATED' ? (
                <form onSubmit={handleSendMessage} className="flex items-center gap-3">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder={`Type your reply to ${activeConversation.customer_name || 'customer'}...`}
                    className="flex-1 px-4 py-3 bg-slate-950/80 border border-amber-500/30 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/40 transition"
                  />
                  <button
                    type="submit"
                    disabled={!inputMessage.trim() || sendMessageMutation.isPending}
                    className="px-5 py-3 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white font-semibold rounded-xl text-xs flex items-center gap-2 shadow-lg transition"
                  >
                    {sendMessageMutation.isPending ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <Send className="w-4 h-4" /> Send WhatsApp Message
                      </>
                    )}
                  </button>
                </form>
              ) : (
                <div className="flex items-center justify-between p-3 bg-blue-950/30 border border-blue-800/40 rounded-xl text-xs text-slate-300">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-blue-400 shrink-0" />
                    <span>
                      Gemini AI is actively responding to customer inquiries in real-time.
                    </span>
                  </div>
                  <button
                    onClick={() => handoffMutation.mutate('takeover')}
                    disabled={handoffMutation.isPending}
                    className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white font-bold rounded-lg transition shrink-0 ml-2"
                  >
                    Take Over (Pause AI)
                  </button>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col justify-center items-center text-slate-500">
            <div className="bg-slate-800/30 p-6 rounded-2xl mb-4">
              <Bot className="w-12 h-12 text-slate-700" />
            </div>
            <h3 className="font-semibold text-slate-400 mb-1">No conversation selected</h3>
            <p className="text-sm text-slate-600 max-w-xs text-center">
              Select a conversation from the sidebar to monitor the AI agent in real-time
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
