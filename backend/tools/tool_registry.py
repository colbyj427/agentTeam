import inspect
from pathlib import Path
from types import UnionType
from typing import Any, Callable, Dict, List, get_type_hints, Literal, get_origin, get_args, Union
import tools.file_tools
import tools.general_tools

# from openai.types.responses import FunctionToolParam

# from config import Agent

_tools: dict[str, Callable] = {}


def _is_optional(annotation) -> bool:
    origin = get_origin(annotation)
    args = get_args(annotation)
    return (origin is UnionType or origin is Union) and type(None) in args


def _get_strict_json_schema_type(annotation) -> dict:
    origin = get_origin(annotation)
    args = get_args(annotation)

    if _is_optional(annotation):
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            return _get_strict_json_schema_type(non_none_args[0])
        raise TypeError(f"Unsupported Union with multiple non-None values: {annotation}")

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
    }

    if annotation in type_map:
        return {"type": type_map[annotation]}

    if origin in type_map:
        return {"type": type_map[origin]}

    if origin is Literal:
        values = args
        if all(isinstance(v, (str, int, bool)) for v in values):
            return {"type": "string" if all(isinstance(v, str) for v in values) else "number", "enum": list(values)}
        raise TypeError("Unsupported Literal values in annotation")

    raise TypeError(f"Unsupported parameter type: {annotation}")


def generate_function_schema(func: Callable[..., Any]) -> dict[str, Any]:
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)

    params = {}
    required = []

    for name, param in sig.parameters.items():
        if name in {"self", "ctx"}:
            continue

        ann = type_hints.get(name, param.annotation)
        if ann is inspect._empty:
            raise TypeError(f"Missing type annotation for parameter: {name}")

        schema_entry = _get_strict_json_schema_type(ann)

        required.append(name)
        params[name] = schema_entry

    return {
        "type": "function",
        "name": func.__name__,
        "description": func.__doc__ or "",
        "parameters": {
            "type": "object",
            "properties": params,
            "required": required,
            "additionalProperties": False
        },
        # "strict": True
    }

# === Tool Registry ===
class ToolRegistry:
    """Global registry for all tools with schema and category metadata."""
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, dict] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, func: Callable, categories: List[str]):
        """Register a callable as a tool with schema and metadata."""
        self._tools[name] = func
        self._schemas[name] = generate_function_schema(func)
        self._metadata[name] = {"categories": categories or []}

    def get_tool(self, name: str) -> Callable:
        return self._tools[name]

    def get_tools_by_category(self, category: str) -> Dict[str, Callable]:
        return {
            name: func for name, func in self._tools.items()
            if category in self._metadata[name]["categories"]
        }

    def get_schemas_by_category(self, category: str) -> List[dict]:
        """Return JSON schemas for a given category — used by agents for OpenAI function calls."""
        return [
            self._schemas[name]
            for name, meta in self._metadata.items()
            if category in meta["categories"]
        ]

    def get_all_schemas(self) -> List[dict]:
        return list(self._schemas.values())


# Singleton instance (import this anywhere)
registry = ToolRegistry()

def register_tool(name: str, func: Callable, categories: List[str]):
    registry.register(name, func, categories)

# Register all the tools here.
register_tool("read_file", tools.file_tools.read_file, ["file"])
register_tool("write_file", tools.file_tools.write_file, ["file"])
register_tool("sayHello", tools.general_tools.sayHello, ["general"])

# class ToolBox:
#     _tools: list[dict[str, Any]]

#     def __init__(self):
#         self._funcs = {}
#         self._tools = []

#     def tool(self, func):
#         self._tools.append(generate_function_schema(func))

#         if inspect.iscoroutinefunction(func):
#             async def _safe_func_async(*args, **kwargs):
#                 try:
#                     return await func(*args, **kwargs)
#                 except Exception:
#                     return traceback.format_exc()
#             safe_func = _safe_func_async
#         else:
#             def _safe_func_sync(*args, **kwargs):
#                 try:
#                     return func(*args, **kwargs)
#                 except Exception:
#                     return traceback.format_exc()
#             safe_func = _safe_func_sync

#         self._funcs[func.__name__] = safe_func
#         return func

#     def get_tools(self):
#         result = []
#         for tool in self._tools:
#             result.append(tool["name"])
#         return result

#     def get_tool(self, tool_name: str):
#         try:
#             return _tools[tool_name]
#         except:
#             return f"Tool: {tool_name} is not in the toolbox."

#     async def run_tool(self, tool_name: str, **kwargs):
#         tool = self._funcs.get(tool_name)
#         if tool is None:
#             return f"Tool: {tool_name} is not in the toolbox."
#         result = tool(**kwargs)
#         if inspect.iscoroutine(result):
#             return await result
#         else:
#             return result
        