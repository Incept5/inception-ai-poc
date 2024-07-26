import os
from typing import Optional
from langchain.tools import tool
from utils.debug_utils import debug_print
from utils.file_tree import file_tree

@tool("file_content")
def file_content(file_path: Optional[str] = None) -> str:
    """Get the content of a file, handling paths that may or may not start with the system source directory or a forward slash."""
    debug_print(f"file_content tool called with file_path: {file_path}")

    system_src = os.environ.get("SYSTEM_SOURCE_PATH", "/system_src")

    if file_path is None:
        debug_print("Error: No file path provided.")
        return "Error: No file path provided."

    debug_print(f"System source directory: {system_src}")

    # Remove leading slash if present
    file_path = file_path.lstrip('/')

    if file_path.startswith(system_src.lstrip('/')):
        full_path = os.path.join('/', file_path)
    else:
        full_path = os.path.join(system_src, file_path)

    debug_print(f"Full path: {full_path}")

    if os.path.exists(full_path):
        debug_print(f"File exists: {full_path}")
        if os.path.isfile(full_path):
            debug_print(f"Is a file: {full_path}")
            try:
                with open(full_path, 'r') as file:
                    content = file.read()
                debug_print(f"File content read successfully: {full_path}")
                return content
            except Exception as e:
                debug_print(f"Error reading file: {full_path}. Error: {str(e)}")
                return f"Error reading file: {file_path}. Error: {str(e)}"
        else:
            debug_print(f"Path is not a file: {full_path}")
            return f"Error: {file_path} is not a file."
    else:
        debug_print(f"File not found: {full_path}")
        return f"Error: File {file_path} not found."

@tool("file_tree")
def file_tree_tool(directory: Optional[str] = None) -> str:
    """Get the file tree structure of a directory, defaulting to SYSTEM_SOURCE_PATH if no directory is provided."""
    if directory is None:
        directory = os.environ.get("SYSTEM_SOURCE_PATH", "/system_src")
    
    debug_print(f"file_tree tool called with directory: {directory}")
    return file_tree(directory)
