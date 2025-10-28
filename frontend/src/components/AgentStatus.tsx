import React from 'react';
import { AgentInfo } from '../types/message';

interface AgentStatusProps {
  agents: AgentInfo[];
  selectedAgent: string;
  onAgentSelect: (agentName: string) => void;
}

const AgentStatus: React.FC<AgentStatusProps> = ({ agents, selectedAgent, onAgentSelect }) => {
  return (
    <div className="bg-gray-50 border-b p-4">
      <h3 className="text-sm font-medium text-gray-700 mb-2">Available Agents</h3>
      <div className="flex flex-wrap gap-2">
        {agents.map((agent) => (
          <button
            key={agent.id}
            onClick={() => onAgentSelect(agent.name)}
            className={`px-3 py-1 rounded-full text-sm transition-colors ${
              selectedAgent === agent.name
                ? 'bg-blue-500 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            {agent.name}
          </button>
        ))}
      </div>
      {selectedAgent && (
        <div className="mt-2 text-xs text-gray-600">
          Selected: {selectedAgent}
        </div>
      )}
    </div>
  );
};

export default AgentStatus;
