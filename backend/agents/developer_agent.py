"""
Developer Agent - handles coding tasks and file operations.
"""

import json
import os
import re
from typing import Dict, Any, Optional
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

    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        try:
            system_prompt = self.get_system_prompt()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]

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

                    continue

            # Otherwise, final assistant message
                return choice.content or ""

        except Exception as e:
            print(f"[Error] process_message failed: {e}")
            return f"Sorry, I encountered an error: {e}"

    # def _should_use_tools(self, response: str, original_message: str) -> bool:
    #     """Determine if agent should use tools based on response and message."""
    #     tool_indicators = [
    #         "read", "write", "file", "directory", "folder", "create", "edit",
    #         "show me", "list", "open", "save", "modify", "update"
    #     ]

    #     message_lower = original_message.lower()
    #     response_lower = response.lower()

    #     return any(indicator in message_lower or indicator in response_lower
    #               for indicator in tool_indicators)

    # def _execute_tool(self, tools: list[str], tool_call):
    #     """
    #     Extract tool calls from the response and call each one, returning the results.

    #     tools: the list of tools available to the agent.
    #     tool_call: the tool call the agent would like to make.

    #     Returns:
    #         The result of the tool call.
    #     """
    #     if tool_call in tools:
    #         return tools[tool_call](tool_call) # TODO: get the right arguments passed in here.
    #     else:
    #         return f"Tool call to {tool_call} failed."

    # def _execute_tools_and_respond(self, original_message: str, initial_response: str) -> str:
    #     """
    #     Execute appropriate tools and generate final response.
        
    #     Args:
    #         original_message: Original user message
    #         initial_response: Initial agent response
            
    #     Returns:
    #         Final response with tool results
    #     """
    #     tool_results = []
    #     message_lower = original_message.lower()

    #     # Determine which tools to use
    #     if any(word in message_lower for word in ["read", "show", "open", "view"]):
    #         # Try to read a file
    #         file_path = self._extract_file_path(original_message)
    #         if file_path:
    #             result = self.file_tools.read_file(file_path)
    #             tool_results.append(self.format_tool_result("read_file", result))
    #             self.log_action("read_file", {"file_path": file_path}, result,
    #                            "success" if result["success"] else "error")

    #     if any(word in message_lower for word in ["write", "create", "save", "edit", "modify"]):
    #         # Try to write a file
    #         file_path = self._extract_file_path(original_message)
    #         if file_path:
    #             content = self._extract_file_content(original_message)
    #             if content:
    #                 result = self.file_tools.write_file(file_path, content)
    #                 tool_results.append(self.format_tool_result("write_file", result))
    #                 self.log_action("write_file", {"file_path": file_path, "content": content},
    #                                 result, "success" if result["success"] else "error")

    #     if any(word in message_lower for word in ["list", "directory", "folder", "show files"]):
    #         # List directory contents
    #         dir_path = self._extract_directory_path(original_message)
    #         result = self.file_tools.list_directory(dir_path)
    #         tool_results.append(self.format_tool_result("list_directory", result))
    #         self.log_action("list_directory", {"dir_path": dir_path}, result,
    #                        "success" if result["success"] else "error")

    #     # Combine initial response with tool results
    #     if tool_results:
    #         return f"{initial_response}\n\n**Tool Results:**\n" + "\n\n".join(tool_results)
    #     else:
    #         return initial_response

    # def _extract_file_path(self, message: str) -> Optional[str]:
    #     """Extract file path from message."""
    #     # Simple extraction - look for common file patterns
    #     # Look for file extensions
    #     file_patterns = [
    #         r'(\w+\.\w+)',  # filename.ext
    #         r'([\w/]+\.\w+)',  # path/filename.ext
    #         r'["\']([^"\']+\.\w+)["\']',  # quoted filenames
    #     ]

    #     for pattern in file_patterns:
    #         matches = re.findall(pattern, message)
    #         if matches:
    #             return matches[0]

    #     return None

    # def _extract_file_content(self, message: str) -> Optional[str]:
    #     """Extract file content from message."""
    #     # Look for code blocks or specific content indicators
    #     # Look for code blocks
    #     code_blocks = re.findall(r'```[\s\S]*?```', message)
    #     if code_blocks:
    #         # Remove markdown formatting
    #         content = code_blocks[0].replace('```', '').strip()
    #         return content

    #     # Look for content after "create" or "write"
    #     content_patterns = [
    #         r'create.*?["\']([^"\']+)["\']',
    #         r'write.*?["\']([^"\']+)["\']',
    #     ]

    #     for pattern in content_patterns:
    #         matches = re.findall(pattern, message, re.IGNORECASE)
    #         if matches:
    #             return matches[0]

    #     return None

    # def _extract_directory_path(self, message: str) -> str:
    #     """Extract directory path from message."""
    #     # Default to current directory
    #     # Look for directory indicators
    #     dir_patterns = [
    #         r'in\s+([\w/]+)',
    #         r'of\s+([\w/]+)',
    #         r'from\s+([\w/]+)',
    #     ]

    #     for pattern in dir_patterns:
    #         matches = re.findall(pattern, message, re.IGNORECASE)
    #         if matches:
    #             return matches[0]

    #     return "."

    def log_action(self, tool_name: str, input_data: Dict[str, Any],
                  output_data: Dict[str, Any], status: str):
        """Log action to database."""
        supabase_client.log_action(
            self.agent_id, tool_name, input_data, output_data, status
        )
