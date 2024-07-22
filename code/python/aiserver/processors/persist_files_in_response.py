import re
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
                file_path = process_file_path(line)
                if file_path:
                    debug_print(f"Found file path: {file_path}")
                elif not line.strip():
                    # Skip empty lines
                    continue
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

def process_file_path(line: str) -> str:
    """Process a line to extract the file path, handling various comment types."""
    # Regular expression to match common comment styles
    comment_pattern = r'^\s*(#|//|/\*|\*|<!--|--)\s*'
    
    # Remove common comment prefixes
    cleaned_line = re.sub(comment_pattern, '', line.strip())
    
    # Remove trailing comment closures if present
    cleaned_line = re.sub(r'\s*(-->|\*/)\s*$', '', cleaned_line)
    
    return cleaned_line if cleaned_line else None