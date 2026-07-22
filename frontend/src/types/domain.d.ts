export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'manager' | 'agent';
  tenant_id: string;
}

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  plan_tier: string;
  monthly_message_limit: number;
  monthly_messages_used: number;
}

export interface Conversation {
  id: string;
  tenant_id: string;
  whatsapp_account_id: string;
  customer_phone: string;
  customer_name?: string;
  status: 'AI_ACTIVE' | 'AWAITING_CUSTOMER' | 'HUMAN_ESCALATED' | 'CLOSED';
  last_activity_at: string;
  created_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  wamid?: string;
  sender_type: 'CUSTOMER' | 'AI' | 'HUMAN_AGENT' | 'SYSTEM';
  content: string;
  created_at: string;
}

export interface Product {
  id: string;
  sku: string;
  name: string;
  description?: string;
  price: number;
  currency: string;
  is_active: boolean;
  inventory_item?: {
    quantity_available: number;
    quantity_reserved: number;
    version: number;
  };
}

export interface Order {
  id: string;
  conversation_id: string;
  total_amount: number;
  currency: string;
  status: string;
  payment_status: string;
  created_at: string;
}

export interface KnowledgeDocument {
  id: string;
  filename: string;
  mime_type: string;
  chunk_count: number;
  status: string;
  created_at: string;
}
