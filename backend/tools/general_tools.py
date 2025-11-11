from backend.main import MessageRequest, MessageResponse, send_message

def sayHello() -> str:
    """Say hello the proper way."""
    return "Hello, world!"

async def sendAgentMessage(agent_name: str, message: str) -> str:
    """Send a message to a specific agent and get the response."""
    request = MessageRequest(agent_name=agent_name, content=message)
    response = await send_message(request)
    return response.content

# a tool to get line numbers so critic and agent can communicate better?