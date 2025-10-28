import axios from 'axios';
import { Message, MessageRequest, AgentInfo } from '../types/message';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const messageApi = {
  async getMessages(threadId?: string, limit: number = 50): Promise<Message[]> {
    const response = await api.get('/api/messages', {
      params: { thread_id: threadId, limit }
    });
    return response.data;
  },

  async sendMessage(request: MessageRequest): Promise<Message> {
    const response = await api.post('/api/messages', request);
    return response.data;
  },
};

export const agentApi = {
  async getAgents(): Promise<AgentInfo[]> {
    const response = await api.get('/api/agents');
    return response.data;
  },
};

export const projectApi = {
  async getProject() {
    const response = await api.get('/api/projects');
    return response.data;
  },
};

export default api;
