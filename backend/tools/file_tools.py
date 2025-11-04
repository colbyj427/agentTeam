import os

"""
File manipulation tools for agents.
Provides safe file operations within the workspace.
"""

def read_file(path: str) -> str:
    """Read the contents of a file."""
    path = f"./workspace/{path}"
    with open(path, "r") as f:
        return f.read()

def write_file(path: str, content: str) -> str:
    """Write content to a file. The path is appended to the path of the workspace."""
    path = f"./workspace/{path}"
    with open(path, "w") as f:
        f.write(content)
    return "File written successfully."

def make_directory(path: str) -> str:
    """Create a directory at the given path."""
    full_path = f"./workspace/{path}"
    os.makedirs(full_path, exist_ok=True)
    return "Directory created successfully."

def list_directory(path: str) -> list[str]:
    """List files and directories in the given path."""
    full_path = f"./workspace/{path}"
    return os.listdir(full_path)

