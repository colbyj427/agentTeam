"""
Agent Registry - manages agent instances for inter-agent communication.
"""

from typing import Dict, Optional
from agents.base_agent import BaseAgent

class AgentRegistry:
    """Global registry for agent instances."""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
    
    def register(self, name: str, agent: BaseAgent):
        """Register an agent instance."""
        self._agents[name] = agent
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent instance by name."""
        return self._agents.get(name)
    
    def get_all_agent_names(self) -> list[str]:
        """Get list of all registered agent names."""
        return list(self._agents.keys())


# Global singleton instance
agent_registry = AgentRegistry()

