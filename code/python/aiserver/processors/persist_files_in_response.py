import re
import random
import string
import os
from processors.persist_file import persist_file
from utils.debug_utils import debug_print

def persist_files_in_response(thread_id: str, response: str) -> str:
    lines = response.split('\n')
    current_file = None
    file_content = []
    file_type = None
    file_path = None

    for line in lines:
        if line.startswith('```') and current_file is None:
            # Start of a new file block
            file_type, file_path = extract_file_info(line)
            current_file = True
            debug_print(f"Starting new file block: type={file_type}, path={file_path}")
        elif line.startswith('```') and current_file:
            # End of the current file block
            if file_type and file_path and file_content:
                file_content_str = '\n'.join(file_content)
                persist_file(thread_id, file_path, file_type, file_content_str)
                debug_print(f"Persisted file: {file_path}")
            current_file = None
            file_content = []
            file_type = None
            file_path = None
        elif current_file:
            if not file_path:
                # Check if this line contains the file path
                file_path = process_file_path(line, file_type)
                if file_path:
                    debug_print(f"Found file path: {file_path}")
                    if file_path.startswith("__snippets"):
                        # If we generated a random path, include this line in the content
                        file_content.append(line)
                elif not line.strip():
                    # Skip empty lines
                    continue
                else:
                    # If we couldn't extract a path, generate a random one and include this line
                    file_path = generate_random_file_path(file_type)
                    debug_print(f"Generated random file path: {file_path}")
                    file_content.append(line)
            else:
                file_content.append(line)

    # Handle case where the last block wasn't closed
    if current_file and file_type and file_path and file_content:
        file_content_str = '\n'.join(file_content)
        persist_file(thread_id, file_path, file_type, file_content_str)
        debug_print(f"Persisted last file: {file_path}")

    return response

def extract_file_info(line: str) -> tuple:
    """Extract file type and path from a line."""
    parts = line.strip('`').split(maxsplit=1)
    file_type = parts[0] if parts else None
    file_path = parts[1] if len(parts) > 1 else None
    return file_type, file_path

def process_file_path(line: str, file_type: str) -> str:
    """Process a line to extract the file path, handling various comment types and invalid characters."""
    # Regular expression to match common comment styles
    comment_pattern = r'^\s*(#|//|/\*|\*|<!--|--)\s*'
    
    # Remove common comment prefixes
    cleaned_line = re.sub(comment_pattern, '', line.strip())
    
    # Remove trailing comment closures if present
    cleaned_line = re.sub(r'\s*(-->|\*/)\s*$', '', cleaned_line)
    
    if cleaned_line:
        # Check if the path contains spaces or other unexpected characters
        if is_valid_path(cleaned_line):
            return cleaned_line
        else:
            debug_print(f"Invalid path detected: {cleaned_line}. Returning None.")
            return None
    else:
        return None

def is_valid_path(path: str) -> bool:
    """Check if the given path is valid (no spaces or unexpected characters)."""
    # Allow alphanumeric characters, underscores, hyphens, periods, and forward slashes
    return bool(re.match(r'^[\w\-./]+$', path))

def generate_random_file_path(file_type: str) -> str:
    """Generate a random file path based on the file type."""
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    file_extensions = {
        'python': '.py',
        'kotlin': '.kt',
        'java': '.java',
        'javascript': '.js',
        'typescript': '.ts',
        'html': '.html',
        'css': '.css',
        'json': '.json',
        'xml': '.xml',
        'yaml': '.yml',
        'markdown': '.md',
        'text': '.txt'
    }
    
    extension = file_extensions.get(file_type.lower(), '')
    return os.path.join("__snippets", f"{random_chars}{extension}")