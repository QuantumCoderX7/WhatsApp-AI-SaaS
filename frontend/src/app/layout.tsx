"use client";

import './globals.css';
import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 1000 * 10,
            retry: 1,
          },
        },
      })
  );

  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <title>WhatsApp AI SaaS — Intelligent Automation Platform</title>
        <meta name="description" content="Enterprise WhatsApp AI customer support and sales automation dashboard. Powered by Gemini AI." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="bg-[#0a0e1a] text-slate-100 min-h-screen antialiased">
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </body>
    </html>
  );
}
