import inspect

# from tools.tool_registry import tool_registry
from tools.tool_registry import registry


class ToolBox:
    """Scoped tool access per agent."""
    def __init__(self, categories: list[str]):
        self.categories = categories
        self.tools = {}
        for cat in categories:
            self.tools.update(registry.get_tools_by_category(cat))

    def get_tool(self, name: str):
        return self.tools[name] if name in self.tools else None
    
    def get_tool_names(self):
        return list(self.tools.keys())

    def get_openai_schemas(self):
        schemas = []
        for cat in self.categories:
            schemas.extend(registry.get_schemas_by_category(cat))
        return schemas

    async def run_tool(self, name: str, **kwargs):
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Unknown tool: {name}"}
        try:
            result = tool(**kwargs)
            if inspect.iscoroutine(result):
                result = await result
            return result
        except Exception as e:
            return {"error": str(e)}
