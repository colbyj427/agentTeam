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
      // For Team chat, we need special handling
      if (selectedAgent === "Team") {
        const userMessage: Message = {
          id: `temp-${Date.now()}`,
          content: content.trim(),
          sender: 'user',
          recipient: 'Team',
          role: 'user',
          created_at: new Date().toISOString(),
          metadata: { thread_id: currentThreadId }
        };
        
        setMessages(prev => [...prev, userMessage]);

        // Send to API with Team as agent_name
        const response = await messageApi.sendMessage({
          content: content.trim(),
          thread_id: currentThreadId,
          agent_name: "Team"
        });

        // Update thread ID if this is a new conversation
        if (!currentThreadId && response.metadata?.thread_id) {
          setCurrentThreadId(response.metadata.thread_id);
        }

        // Add agent response to messages
        setMessages(prev => [...prev, response]);
        
        // Refresh messages to get all team messages including inter-agent conversations
        if (currentThreadId || response.metadata?.thread_id) {
          const threadId = currentThreadId || response.metadata?.thread_id;
          const threadMessages = await messageApi.getMessages(threadId);
          const sortedMessages = threadMessages.sort(
            (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
          );
          setMessages(sortedMessages);
        }
      } else {
        // Individual agent chat - normal flow
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
        
        // Refresh messages to get any inter-agent messages that may have been created
        if (currentThreadId || response.metadata?.thread_id) {
          const threadId = currentThreadId || response.metadata?.thread_id;
          const threadMessages = await messageApi.getMessages(threadId);
          const sortedMessages = threadMessages.sort(
            (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
          );
          setMessages(sortedMessages);
        }
      }
      
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
      // For individual agent chats, only show messages between user and that agent
      // For Team chat, show all messages from all agents in team thread
      if (agentName === "Team") {
        // Load all messages and find team threads
        const messagesData = await messageApi.getMessages();
        
        // Find team threads (threads with is_team_thread flag or inter-agent messages)
        let teamThreadId: string | undefined = undefined;
        
        for (const msg of messagesData) {
          const metadata = msg.metadata || {};
          // Check if this is a team thread
          if (metadata.is_team_thread === true) {
            const tid = metadata.thread_id;
            if (tid) {
              teamThreadId = tid;
              break;
            }
          }
          // Also check for threads with inter-agent messages (these are team threads)
          if (msg.sender !== "user" && msg.recipient !== "user") {
            const tid = metadata.thread_id;
            if (tid) {
              teamThreadId = tid;
              break;
            }
          }
        }
        
        if (teamThreadId) {
          // Load all messages from the team thread
          const allTeamMessages = await messageApi.getMessages(teamThreadId);
          const sortedMessages = allTeamMessages.sort(
            (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
          );
          setMessages(sortedMessages);
          setCurrentThreadId(teamThreadId);
        } else {
          setMessages([]);
          setCurrentThreadId(undefined);
        }
      } else {
        // Individual agent chat - only show messages between user and this agent
        const messagesData = await messageApi.getMessages();
        
        // Filter messages for this specific agent and sort by timestamp
        const agentMessages = messagesData
          .filter(msg => 
            (msg.sender === agentName && msg.recipient === "user") ||
            (msg.sender === "user" && msg.recipient === agentName)
          )
          .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        
        setMessages(agentMessages);
        
        // Set thread ID from the most recent message if available
        if (agentMessages.length > 0) {
          const latestMessage = agentMessages[agentMessages.length - 1];
          setCurrentThreadId(latestMessage.metadata?.thread_id);
        } else {
          setCurrentThreadId(undefined);
        }
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
