import React, { useState, useEffect } from 'react';
import { Message, AgentInfo } from './types/message';
import { messageApi, agentApi } from './services/api';
import AgentList from './components/AgentList';
import ConversationView from './components/ConversationView';
import './App.css';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentThreadId, setCurrentThreadId] = useState<string | undefined>();

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        // Load agents
        const agentsData = await agentApi.getAgents();
        setAgents(agentsData);
        
        // Load recent messages
        const messagesData = await messageApi.getMessages();
        setMessages(messagesData);
        
        // Set thread ID from latest message if available
        if (messagesData.length > 0) {
          const latestMessage = messagesData[0];
          setCurrentThreadId(latestMessage.metadata?.thread_id);
        }
      } catch (error) {
        console.error('Failed to load initial data:', error);
      }
    };

    loadInitialData();
  }, []);

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    setIsLoading(true);
    
    try {
      // Add user message to UI immediately
      const userMessage: Message = {
        id: `temp-${Date.now()}`,
        content: content.trim(),
        sender: 'user',
        recipient: selectedAgent,
        role: 'user',
        created_at: new Date().toISOString(),
        metadata: { thread_id: currentThreadId }
      };
      
      setMessages(prev => [...prev, userMessage]);

      // Send to API
      const response = await messageApi.sendMessage({
        content: content.trim(),
        thread_id: currentThreadId,
        agent_name: selectedAgent
      });

      // Update thread ID if this is a new conversation
      if (!currentThreadId && response.metadata?.thread_id) {
        setCurrentThreadId(response.metadata.thread_id);
      }

      // Add agent response to messages
      setMessages(prev => [...prev, response]);
      
    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove the temporary user message on error
      setMessages(prev => prev.filter(msg => msg.id !== `temp-${Date.now()}`));
    } finally {
      setIsLoading(false);
    }
  };

  const handleAgentSelect = async (agentName: string) => {
    setSelectedAgent(agentName);
    setIsLoading(true);
    
    try {
      // Load message history for this agent
      const messagesData = await messageApi.getMessages();
      
      // Filter messages for this specific agent and sort by timestamp
      const agentMessages = messagesData
        .filter(msg => msg.sender === agentName || msg.recipient === agentName)
        .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      
      setMessages(agentMessages);
      
      // Set thread ID from the most recent message if available
      if (agentMessages.length > 0) {
        const latestMessage = agentMessages[agentMessages.length - 1];
        setCurrentThreadId(latestMessage.metadata?.thread_id);
      } else {
        setCurrentThreadId(undefined);
      }
    } catch (error) {
      console.error('Failed to load agent messages:', error);
      setMessages([]);
      setCurrentThreadId(undefined);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Red Header */}
      <div className="bg-red-600 text-white px-4 py-3 shadow-md">
        <h1 className="text-xl font-bold">AgentTeam</h1>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 min-h-0">
        {/* Left Sidebar - Agent List */}
        <AgentList 
          agents={agents}
          selectedAgent={selectedAgent}
          onAgentSelect={handleAgentSelect}
        />

        {/* Right Side - Conversation */}
        <ConversationView
          messages={messages}
          selectedAgent={selectedAgent}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
        />
      </div>
    </div>
  );
}

export default App;
