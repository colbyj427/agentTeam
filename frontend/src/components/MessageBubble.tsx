import React from 'react';
import { Message } from '../types/message';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isAgent = message.role === 'assistant';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
        isUser 
          ? 'bg-teal-500 text-white' 
          : isAgent 
            ? 'bg-teal-100 text-teal-800' 
            : 'bg-gray-100 text-gray-700'
      }`}>
        <div className="text-sm font-medium mb-1">
          {isUser ? 'You' : message.sender}
        </div>
        <div className="whitespace-pre-wrap break-words">
          {message.content}
        </div>
        <div className="text-xs opacity-70 mt-1">
          {(() => {
            const date = new Date(message.created_at);
            if (isNaN(date.getTime())) {
              // If date is invalid, show current time
              const now = new Date();
              return `${now.toLocaleDateString('en-US', { 
                weekday: 'short', 
                month: 'short', 
                day: 'numeric' 
              })} at ${now.toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
              })}`;
            }
            return `${date.toLocaleDateString('en-US', { 
              weekday: 'short', 
              month: 'short', 
              day: 'numeric' 
            })} at ${date.toLocaleTimeString('en-US', {
              hour: 'numeric',
              minute: '2-digit',
              hour12: true
            })}`;
          })()}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
