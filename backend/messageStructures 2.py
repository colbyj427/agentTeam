from typing import Any, Dict, Optional
from pydantic import BaseModel

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
