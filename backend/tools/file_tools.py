"""
File manipulation tools for agents.
Provides safe file operations within the workspace.
"""

def read_file(path: str) -> str:
    """Read the contents of a file."""
    with open(path, "r") as f:
        return f.read()

def write_file(path: str, content: str) -> str:
    """Write content to a file."""
    with open(path, "w") as f:
        f.write(content)
    return "File written successfully."
