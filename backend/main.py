"""
FastAPI backend for Agent Team Multi-Agent Coding Environment.
Provides REST API endpoints for messaging and agent interaction.
"""

import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from db.supabase_client import supabase_client
from agents.developer_agent import DeveloperAgent

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Agent Team API",
    description="Multi-Agent Coding Environment API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
developer_agent = DeveloperAgent()

# Pydantic models
class MessageRequest(BaseModel):
    content: str
    thread_id: Optional[str] = None
    agent_name: str = "Developer"

class MessageResponse(BaseModel):
    id: str
    content: str
    sender: str
    recipient: str
    role: str
    created_at: str
    metadata: Optional[Dict[str, Any]] = None

class AgentInfo(BaseModel):
    id: str
    name: str
    role: str
    description: str
    tools: List[str]

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Agent Team API",
        "version": "1.0.0",
        "endpoints": {
            "messages": "/api/messages",
            "agents": "/api/agents",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "agent-team-api"}

@app.get("/api/agents", response_model=List[AgentInfo])
async def get_agents():
    """Get all available agents."""
    try:
        agents_data = supabase_client.get_agents()
        return [
            AgentInfo(
                id=agent["id"],
                name=agent["name"],
                role=agent["role"],
                description=agent["description"],
                tools=agent["tools"] or []
            )
            for agent in agents_data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")

@app.get("/api/messages", response_model=List[MessageResponse])
async def get_messages(thread_id: Optional[str] = None, limit: int = 50):
    """Get message history."""
    try:
        messages_data = supabase_client.get_messages(thread_id, limit)
        return [
            MessageResponse(
                id=msg["id"],
                content=msg["content"],
                sender=msg["sender"],
                recipient=msg["recipient"],
                role=msg["role"],
                created_at=msg["created_at"],
                metadata=msg.get("metadata")
            )
            for msg in messages_data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

@app.post("/api/messages", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    """Send a message to an agent and get response."""
    try:
        # Generate thread ID if not provided
        thread_id = request.thread_id or str(uuid.uuid4())

        # Save user message
        user_message_id = supabase_client.save_message(
            thread_id=thread_id,
            sender="user",
            recipient=request.agent_name,
            content=request.content,
            role="user"
        )

        # Get agent response
        if request.agent_name == "Developer":
            agent_response = await developer_agent.process_message(request.content)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent: {request.agent_name}")

        # Save agent response
        agent_message_id = supabase_client.save_message(
            thread_id=thread_id,
            sender=request.agent_name,
            recipient="user",
            content=agent_response,
            role="assistant"
        )

        # Return agent response
        return MessageResponse(
            id=agent_message_id,
            content=agent_response,
            sender=request.agent_name,
            recipient="user",
            role="assistant",
            created_at=datetime.now().isoformat(),  # Set current timestamp
            metadata={"thread_id": thread_id}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@app.get("/api/projects")
async def get_projects():
    """Get project information."""
    try:
        project = supabase_client.get_project()
        if project:
            return {
                "id": project["id"],
                "name": project["name"],
                "repo_url": project.get("repo_url"),
                "branch": project.get("branch", "main"),
                "settings": project.get("settings", {})
            }
        return {"message": "No project found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )
