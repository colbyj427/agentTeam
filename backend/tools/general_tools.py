from typing import Optional
import os
import httpx
from messageStructures import MessageRequest, MessageResponse


def sayHello() -> str:
    """Say hello the proper way."""
    return "Hello, world!"


async def sendAgentMessage(agent_name: str, message: str, thread_id: Optional[str] = None) -> str:
    """
    Send a message to a specific agent and return the agent's response content.

    Important: to avoid circular imports with `main.py` we make an HTTP request to the
    local backend message endpoint instead of importing and calling the endpoint
    function directly. This requires the server to be reachable at the configured
    host/port (defaults to http://localhost:8000).

    Args:
        agent_name: target agent name (e.g., 'Developer', 'Critic')
        message: message content to send
        thread_id: optional thread id to continue an existing conversation

    Returns:
        The assistant response content as a string.
    """
    base = os.getenv("API_BASE_URL") or f"http://{os.getenv('HOST','localhost')}:{os.getenv('PORT','8000')}"

    req = MessageRequest(content=message, thread_id=thread_id, agent_name=agent_name)

    url = f"{base.rstrip('/')}/api/messages"

    async with httpx.AsyncClient() as client:
        # call backend API which will route to the requested agent
        resp = await client.post(url, json=req.model_dump())
        resp.raise_for_status()
        data = resp.json()

    # Expect the API to return our MessageResponse shape
    if isinstance(data, dict):
        return data.get("content", "")
    return str(data)




# a tool to get line numbers so critic and agent can communicate better?