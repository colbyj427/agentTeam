import React from 'react';
import { AgentInfo } from '../types/message';

interface AgentListProps {
  agents: AgentInfo[];
  selectedAgent: string;
  onAgentSelect: (agentName: string) => void;
}

const AgentList: React.FC<AgentListProps> = ({ agents, selectedAgent, onAgentSelect }) => {
  return (
    <div className="w-1/3 bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">Available Agents</h2>
        <p className="text-sm text-gray-600">Select an agent to start a conversation</p>
      </div>

      {/* Agent List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {agents.map((agent) => (
          <div
            key={agent.id}
            onClick={() => onAgentSelect(agent.name)}
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 hover:shadow-md ${
              selectedAgent === agent.name
                ? 'border-blue-500 bg-blue-50 shadow-md'
                : 'border-gray-200 bg-white hover:border-gray-300'
            }`}
          >
            <div className="flex items-start space-x-3">
              {/* Agent Avatar */}
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold ${
                selectedAgent === agent.name ? 'bg-blue-500' : 'bg-gray-400'
              }`}>
                {agent.name.charAt(0)}
              </div>
              
              {/* Agent Info */}
              <div className="flex-1 min-w-0">
                <h3 className={`font-medium ${
                  selectedAgent === agent.name ? 'text-blue-900' : 'text-gray-900'
                }`}>
                  {agent.name}
                </h3>
                <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                  {agent.description}
                </p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {agent.tools.slice(0, 3).map((tool, index) => (
                    <span
                      key={index}
                      className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
                    >
                      {tool}
                    </span>
                  ))}
                  {agent.tools.length > 3 && (
                    <span className="text-xs text-gray-500">
                      +{agent.tools.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="text-xs text-gray-500">
          {agents.length} agent{agents.length !== 1 ? 's' : ''} available
        </div>
      </div>
    </div>
  );
};

export default AgentList;
