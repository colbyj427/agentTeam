import React from 'react';
import { Message } from '../types/message';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

interface ConversationViewProps {
  messages: Message[];
  selectedAgent: string;
  isLoading: boolean;
  onSendMessage: (content: string) => void;
}

const ConversationView: React.FC<ConversationViewProps> = ({
  messages,
  selectedAgent,
  isLoading,
  onSendMessage
}) => {
  // Show welcome screen when no agent is selected
  if (!selectedAgent) {
    return (
      <div className="w-2/3 flex flex-col h-full bg-gray-50">
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Welcome to AgentTeam</h2>
            <p className="text-gray-600 mb-4">Select an agent from the left to start a conversation</p>
            <div className="text-sm text-gray-500">
              Choose from available agents to begin your development session
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-2/3 flex flex-col h-full bg-gray-50">
      {/* Conversation Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
            {selectedAgent.charAt(0)}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-800">{selectedAgent}</h2>
            <p className="text-sm text-gray-600">
              {messages.length > 0 ? `${messages.length} messages` : 'Start a conversation'}
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 flex flex-col min-h-0">
        <MessageList messages={messages} isLoading={isLoading} />
      </div>

      {/* Message Input */}
      <MessageInput 
        onSendMessage={onSendMessage}
        disabled={isLoading}
      />
    </div>
  );
};

export default ConversationView;
