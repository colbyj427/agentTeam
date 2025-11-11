def sayHello() -> str:
    """Say hello the proper way."""
    return "Hello, world!"

async def message_agent(agent_name: str, message: str, thread_id: str, sender_agent: str) -> str:
    """
    Send a message to another agent and get their response.
    This enables agents to collaborate and work together on tasks.
    Inter-agent messages are saved to a team thread separate from individual agent threads.
    
    Args:
        agent_name: Name of the agent to message (e.g., "Critic", "Developer")
        message: The message content to send to the agent
        thread_id: The conversation thread ID (individual agent thread)
        sender_agent: Name of the agent sending this message
        
    Returns:
        The response from the recipient agent
    """
    import uuid
    from db.supabase_client import supabase_client
    from agents.agent_registry import agent_registry
    
    # Get agent from registry
    recipient_agent = agent_registry.get_agent(agent_name)
    
    if not recipient_agent:
        available = agent_registry.get_all_agent_names()
        return f"Error: Unknown agent '{agent_name}'. Available agents: {', '.join(available)}"
    
    try:
        # Use a team thread for inter-agent messages
        # Find existing team thread or create a new one
        # Team threads are identified by metadata flag "is_team_thread"
        all_messages = supabase_client.get_messages(thread_id=None, limit=1000)
        team_threads = set()
        
        # Find all team threads (threads with is_team_thread flag or inter-agent messages)
        for msg in all_messages:
            metadata = msg.get("metadata") or {}
            if isinstance(metadata, str):
                import json
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            
            # Check if this is a team thread
            if metadata.get("is_team_thread") == True:
                tid = msg.get("thread_id")
                if tid:
                    team_threads.add(tid)
            # Also check for threads with inter-agent messages (these are team threads)
            elif msg.get("sender") not in ["user"] and msg.get("recipient") not in ["user"]:
                tid = msg.get("thread_id")
                if tid:
                    team_threads.add(tid)
        
        # Use the most recent team thread, or create a new one
        if team_threads:
            # For simplicity, use the first team thread found
            # In a production system, you'd want to track the "active" team thread
            team_thread_id = list(team_threads)[0]
        else:
            team_thread_id = str(uuid.uuid4())
        
        # Save the inter-agent message to the team thread with team flag
        supabase_client.save_message(
            thread_id=team_thread_id,
            sender=sender_agent,
            recipient=agent_name,
            content=message,
            role="assistant",
            metadata={"is_team_thread": True, "thread_id": team_thread_id}
        )
        
        # Process the message with the recipient agent (pass team thread_id in context)
        context = {"thread_id": team_thread_id}
        response = await recipient_agent.process_message(message, context=context)
        
        # Save the recipient agent's response to the team thread with team flag
        supabase_client.save_message(
            thread_id=team_thread_id,
            sender=agent_name,
            recipient=sender_agent,
            content=response,
            role="assistant",
            metadata={"is_team_thread": True, "thread_id": team_thread_id}
        )
        
        return f"Response from {agent_name}: {response}"
        
    except Exception as e:
        return f"Error messaging {agent_name}: {str(e)}"