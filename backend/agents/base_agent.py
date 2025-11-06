"""
Base agent class for all AI agents in the system.
Provides common functionality for message handling and tool execution.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime

class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, name: str, role: str, description: str, tools: List[str]):
        """
        Initialize base agent.
        
        Args:
            name: Agent name
            role: Agent role (developer, critic, etc.)
            description: Agent description
            tools: List of available tool names
        """
        self.name = name
        self.role = role
        self.description = description
        self.tools = tools
        self.agent_id = str(uuid.uuid4())
        self.curr_session = []

    @abstractmethod
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a message and return a response.
        
        Args:
            message: User message to process
            context: Optional context information
            
        Returns:
            Agent response
        """
        pass

    def can_use_tool(self, tool_name: str) -> bool:
        """Check if agent can use a specific tool."""
        return tool_name in self.tools

    def get_available_tools(self) -> List[str]:
        """Get list of available tools for this agent."""
        return self.tools.copy()

    def log_action(self, tool_name: str, input_data: Dict[str, Any], 
                  output_data: Dict[str, Any], status: str): # -> str
        """
        Log an action to the database.
        
        Args:
            tool_name: Name of tool used
            input_data: Input parameters
            output_data: Output result
            status: Action status (success, error, pending)
            
        Returns:
            Action ID
        """
        # This will be implemented by the specific agent subclasses
        # that have access to the database client
        pass

    async def log_conversation(self):
        """
        Log the current conversation session to the database.
        """
        # This will be implemented by the specific agent subclasses
        # that have access to the database client
        pass

    def get_system_prompt(self) -> str:
        """Get system prompt for this agent."""
        return f"""You are {self.name}, a {self.role} agent in a multi-agent development team.

                Description: {self.description}

                Available tools: {', '.join(self.tools)}

                Use all the tools at your disposal to assist with tasks.
                You will likley use a tool on every response, 
                always check your list to see if there is a tool you should use.
                You **must** call the relevant tool when the user asks a question that requires it.

                You are expected to collaborate with other agents to complete tasks.

                You can help with development tasks, file operations, and code analysis. 
                When you need to use tools, explain what you're doing and show the results.
                Always be helpful and provide clear, actionable responses."""
