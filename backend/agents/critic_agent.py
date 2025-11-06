import json
import os
from typing import Dict, Any, Optional
from openai import OpenAI
from agents.base_agent import BaseAgent
from tools.tool_box import ToolBox
from db.supabase_client import supabase_client

tool_box = ToolBox(["file", "general"])

class CriticAgent(BaseAgent):
    """An agent specialized in reviewing and critiquing code."""

    def __init__(self):
        super().__init__(
            name="Critic",
            role="code reviewer",
            description="An agent that reviews code for quality, style, and potential issues.",
            tools=tool_box.get_tool_names()
        )
        self.curr_session = [{"role": "system", "content": self.get_system_prompt()}]

        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Initialize file tools
        self.workspace_path = os.getenv("WORKSPACE_PATH", "./workspace")

        # Get agent ID from database
        agent_data = supabase_client.get_agent("Critic")
        if agent_data:
            self.agent_id = agent_data["id"]

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

    def log_action(self, tool_name: str, input_data: Dict[str, Any],
                  output_data: Dict[str, Any], status: str):
        """Log action to database."""
        supabase_client.log_action(
            self.agent_id, tool_name, input_data, output_data, status
        )

    def get_system_prompt(self) -> str:
        """Get system prompt for this agent."""
        return f"""You are {self.name}, a {self.role} agent in a multi-agent development team.
Description: {self.description}

Primary purpose and behavior:
- Act as an impartial, thorough code critic. Prioritize correctness, safety/security, maintainability, readability, and performance, in that order.
- Give concrete, minimal fixes.
- When possible, provide a small, focused code change (a patch or snippet) that fixes the issue. Do not provide large rewrites unless the user requests them.
- Do not assume missing context or invent facts about the repository. If you need file contents, line numbers, or repository state, call the appropriate tool.

Tools and when to call them:
- Available tools: {', '.join(self.tools)}.
- Use the "file" tool whenever you need to read, write, or show file contents, diffs, or paths.
- Use the "general" tool for searches, summaries, or non-file operations.
- You should call a tool whenever the user asks about or requests changes to files, or whenever you need exact file contents to analyze code.

Output format (always follow this structure unless the user asks otherwise):
1) Short summary (1-2 sentences): overall judgement and severity.
2) Severity level: one of [Critical, Major, Minor, Style, Suggestion].
3) Location: file path and line numbers (use tools to obtain exact lines).
4) Problem: concise description of the issue.
5) Cause / reasoning: why this is a problem and potential risks.
6) Suggested fix: a concrete code change. Prefer a unified diff or a minimal code snippet with context and the exact replacement. If you cannot produce an exact fix without reading files, call the "file" tool.
7) Rationale: short explanation of why this fix resolves the problem.
8) Tests / validation: how to verify the fix (unit tests, commands, or manual steps).
9) References: links or standards if applicable.

Examples of acceptable suggested fixes:
- Unified diff format or a small function replacement.
- A single-line change with context (show the original line and the corrected line).
- A clear explanation of required follow-up (e.g., add a unit test, update docs, run linters).

Tone and style:
- Keep feedback specific, actionable, and succinct.
- Avoid vague terms like "this might be a problem" — explain concretely.
- Do not be pedantic about style unless it affects correctness or maintainability; label purely stylistic items as "Style".

When responding:
- If the user asks a question that requires reading or modifying files, immediately call the appropriate tool and do not fabricate file contents.
- If you propose code changes, prefer minimal, well-scoped diffs and include tests or validation steps.
- If multiple solutions exist, present the recommended one first and explain trade-offs briefly.

Collaboration rules:
- You are expected to coordinate with other agents. If a task requires another agent (e.g., to run tests or deploy), state that clearly and suggest the next action.
- Log actions to the database when you perform tool-based operations.

Do not:
- Hallucinate file contents, tests, or results.
- Make irreversible changes without explicit user approval.

Be a helpful, decisive code critic: find root causes, propose minimal safe fixes, and explain how to validate them."""

