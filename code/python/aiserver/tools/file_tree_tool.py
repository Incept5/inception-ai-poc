import os
from typing import Optional
from langchain.tools import tool
from utils.debug_utils import debug_print
from utils.file_tree import file_tree

@tool("file_tree")
def file_tree_tool(directory: Optional[str] = None) -> str:
    """Get the file tree structure of a directory, defaulting to /system_src if no directory is provided."""
    if directory is None:
        directory = "/system_src"
    
    debug_print(f"file_tree tool called with directory: {directory}")
    return file_tree(directory)
