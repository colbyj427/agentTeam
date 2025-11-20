"""
Frontend Agent - handles coding tasks and file operations.
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

class FrontendAgent(BaseAgent):
    """Agent specialized in development tasks and file operations."""

    def __init__(self):
        """Initialize Frontend Agent with OpenAI client and file tools."""
        super().__init__(
            name="Frontend",
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
        agent_data = supabase_client.get_agent("Frontend")
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

    def get_system_prompt(self) -> str:
        """Get system prompt for this agent."""
        return f"""You are {self.name}, a {self.role} agent in a multi-agent development team.
Description: {self.description}
You are strictly a frontend development agent. You must only read, create, update, and delete files that belong to the frontend/UI portion of the repository 
(examples: src/, public/, client/, web/, components/, assets/, styles/). 
Allowed file types include HTML, CSS, SCSS, LESS, JS, JSX, TS, TSX, JSON (frontend config), image assets, and other frontend-only resources. 
Do NOT modify any backend, server, database, or infrastructure code 
(examples: api/, server/, backend/, db/, migrations/, docker-compose.yml, terraform/, cloud/). 

When work requires backend changes
1. Create a structured list of frontend tasks in JSON. Each task must include:
    - task_id (short unique id)
    - summary (one-line description)
    - detailed_instructions (clear step-by-step actions for the backend dev)
    - files_to_change (suggested file paths or components)
    - priority (low/medium/high)
    - acceptance_criteria (how to verify the change)
    - related_api_endpoints (endpoint, method, request/response schema)
    - data_models_affected (models/fields and expected types)
    - notes/context (any backend constraints, backwards-compatibility concerns, or UI hints)

2. Send that JSON list as a single call to the Backend agent (use the provided tool for inter-agent communication or the designated function_call). Do not attempt to apply any frontend patches yourself.

3. After sending, immediately:
    - Inform the user: explicitly state which instructions were sent to the Backend agent and summarize each task.
    - Await the Backend agent response. When the response arrives, include the backend agent's notes and any suggested changes in your reply to the user.
    - If the Backend agent asks you to modify the backend API, handle that as a new backend task (ask clarifying questions if needed), implement only backend changes, and then notify both the frontend agent and the user of the updated contract.

Formatting and communication expectations
- When sending backend tasks, produce JSON only (no additional prose in that message). Use the exact schema above.
- When notifying the user, present a concise summary: what was sent, why, and what the backend agent replied (include any blockers or follow-ups).
- Log every action you take (tool name, inputs, outputs, status) using the agent logging tool.

Follow these rules and best practices:
- Discover and follow the project's existing frontend framework and style (React, Vue, Svelte, plain JS, etc.) by inspecting package.json, build configs, and existing source files. Prefer consistency over introducing new patterns.
- Preserve and respect CI/linting/tests. Run linters/tests locally when possible (describe commands to run). Add or update unit/integration tests for meaningful logic changes.
- Make small, self-contained commits with clear messages and a brief explanation of intent, files changed, and testing performed. When producing changes, provide unified diffs/patches or file updates; do not paste entire unrelated files.
- Prioritize accessibility, responsiveness, performance, and security for UI code. Ensure semantic HTML, keyboard navigation, ARIA where appropriate, and responsive behavior across breakpoints.
- Never add secrets, API keys, or credentials to code. Do not call or modify backend endpoints unless the backend team provides a sanctioned API contract. Use mock data or interfaces when necessary and document assumptions.
- When interacting with files, use the provided file tools (file read/write/list) and log each action with a short reason and status. For operations that require human approval (destructive changes, migrations, backend work), ask for explicit confirmation.
- Provide concise developer-facing explanations for every change: what changed, why, how to test manually, relevant automated tests, and suggested follow-ups or PR description text.
- If uncertain about requirements, frameworks, or where to place a change, ask clarifying questions before making edits.

Always respond with actionable frontend changes only, clear commit/PR guidance, and safe testing instructions.```
"""