"""
Developer Agent - handles coding tasks and file operations.
"""

import json
import os
from typing import Dict, Any, Optional
from xxlimited import Str
from openai import OpenAI
from agents.base_agent import BaseAgent
from tools.tool_box import ToolBox
from db.supabase_client import supabase_client

tool_box = ToolBox(["file", "general"])

class DeveloperAgent(BaseAgent):
    """Agent specialized in development tasks and file operations."""

    def __init__(self):
        """Initialize Developer Agent with OpenAI client and file tools."""
        super().__init__(
            name="Developer",
            role="software developer",
            description="""A coding agent that can write, read, and modify files.
                        Specializes in software development tasks.""",
            tools=tool_box.get_tool_names()
        )
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Initialize file tools
        self.workspace_path = os.getenv("WORKSPACE_PATH", "./workspace")

        # Get agent ID from database
        agent_data = supabase_client.get_agent("Developer")
        if agent_data:
            self.agent_id = agent_data["id"]

        self.curr_session = []
        self.initialize_context()

        return None

    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        try:
            self.curr_session.append({"role": "user", "content": message})
            messages = self.curr_session

            while True:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=messages,  # type: ignore[arg-type]
                    temperature=0.7,
                    # max_tokens=2000
                    functions=tool_box.get_openai_schemas(),
                    function_call="auto"
                )

                choice = response.choices[0].message
                fn_call = getattr(choice, "function_call", None)
                print(f">>> Assistant response: {choice}")
                print(f"Tools: {tool_box.get_tool_names()}")
                if fn_call:
                    func_name = fn_call.name
                    try:
                        args = json.loads(fn_call.arguments or "{}")
                    except Exception:
                        return "Sorry, there was an error parsing the function call."

                    print(f">>> Calling {func_name}({args})")

                    if func := tool_box.get_tool(func_name):
                        result = await tool_box.run_tool(func_name, **args)
                    else:
                        result = {"error": f"Unknown tool: {func_name}"}

                    # Add the function call and result back to conversation
                    messages.append({"role": "assistant", "function_call": fn_call})
                    messages.append({
                        "role": "function",
                        "name": func_name,
                        "content": json.dumps(result)
                    })
                    self.curr_session = messages  # Update current session
                    continue

            # Otherwise, final assistant message
                self.curr_session.append({"role": "assistant", "content": choice.content or ""})
                return choice.content or ""

        except Exception as e:
            print(f"[Error] process_message failed: {e}")
            return f"Sorry, I encountered an error: {e}"
        
    async def summarize_session(self):
        """Summarize the current conversation session before logging."""
        # Simple summarization logic (could be improved with LLM)
        summary = await self.process_message(
        "Summarize our conversation so far in brief points. Exclude your system prompt," \
        "and this summary command. Focus on key actions taken and decisions made." \
        "Write it so that it can be used to recall context later."
                                       )
        print(f">>> Summary: {summary}")
        return summary

    def log_action(self, tool_name: str, input_data: Dict[str, Any],
                  output_data: Dict[str, Any], status: str):
        """Log action to database."""
        supabase_client.log_action(
            self.agent_id, tool_name, input_data, output_data, status
        )

    async def log_conversation(self):
        """Log the current conversation session to the database."""
        print(">>> Logging conversation...")
        if len(self.curr_session) == 1:
            print(">>> No conversation to log.")
            return
        summary = await self.summarize_session()
        supabase_client.log_conversation(self.agent_id, summary)
        self.initialize_context()

    def initialize_context(self):
        """Reset current session with system prompt."""
        self.curr_session = [{"role": "system", "content": self.get_system_prompt()}]
        # grab the 5 most recent summaries from db
        # add them to the curr_session as context (as assistant messages)
        print(f"agent id in initialize_context: {self.agent_id}")
        recent_summaries = supabase_client.get_recent_summaries(self.agent_id, limit=5)
        for summary in recent_summaries:
            self.curr_session.append({"role": "assistant", "content": summary})