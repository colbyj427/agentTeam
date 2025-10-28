export interface Message {
  id: string;
  content: string;
  sender: string;
  recipient: string;
  role: 'user' | 'assistant' | 'manager' | 'critic' | 'rag';
  created_at: string;
  metadata?: Record<string, any>;
}

export interface MessageRequest {
  content: string;
  thread_id?: string;
  agent_name: string;
}

export interface AgentInfo {
  id: string;
  name: string;
  role: string;
  description: string;
  tools: string[];
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}
