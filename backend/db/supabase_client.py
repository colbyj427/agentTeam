"""
Supabase client wrapper for Agent Team application.
Handles database connections and provides utility methods.
"""

import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    """Wrapper for Supabase client with utility methods."""
    
    def __init__(self):
        """Initialize Supabase client with environment variables."""
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not all([self.url, self.anon_key, self.service_key]):
            raise ValueError("Missing required Supabase environment variables")
        
        # Use service key for backend operations
        self.client: Client = create_client(self.url, self.service_key)
    
    def save_message(self, thread_id: str, sender: str, recipient: str, 
                    content: str, role: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save a message to the database."""
        result = self.client.table("messages").insert({
            "thread_id": thread_id,
            "sender": sender,
            "recipient": recipient,
            "content": content,
            "role": role,
            "metadata": metadata or {}
        }).execute()
        
        if result.data:
            return result.data[0]["id"]
        raise Exception("Failed to save message")
    
    def get_messages(self, thread_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve messages, optionally filtered by thread_id."""
        query = self.client.table("messages").select("*")
        
        if thread_id:
            query = query.eq("thread_id", thread_id)
        
        result = query.order("created_at", desc=True).limit(limit).execute()
        return result.data or []
    
    def get_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent configuration by name."""
        result = self.client.table("agents").select("*").eq("name", agent_name).execute()
        return result.data[0] if result.data else None
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Get all available agents."""
        result = self.client.table("agents").select("*").execute()
        return result.data or []
    
    def log_action(self, agent_id: str, tool_name: str, input_data: Dict[str, Any], 
                  output_data: Dict[str, Any], status: str) -> str:
        """Log an agent action to the database."""
        result = self.client.table("actions").insert({
            "agent_id": agent_id,
            "tool_name": tool_name,
            "input": input_data,
            "output": output_data,
            "status": status
        }).execute()
        
        if result.data:
            return result.data[0]["id"]
        raise Exception("Failed to log action")
    
    def get_project(self, project_name: str = "Agent Team Workspace") -> Optional[Dict[str, Any]]:
        """Get project configuration by name."""
        result = self.client.table("projects").select("*").eq("name", project_name).execute()
        return result.data[0] if result.data else None

# Global instance
supabase_client = SupabaseClient()
