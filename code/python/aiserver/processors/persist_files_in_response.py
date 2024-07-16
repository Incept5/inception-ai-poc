import re
from processors.persist_file import persist_file

def persist_files_in_response(thread_id: str, response: str) -> str:
    # Regular expression to find code blocks with file paths
    pattern = r"```(\w+)\s+([^\n]+)\n(.*?)\n```"

    def process_match(match):
        file_type = match.group(1)
        file_path = match.group(2).strip()
        file_content = match.group(3)

        # Check if there are nested code blocks
        nested_blocks = re.findall(r"```.*?```", file_content, re.DOTALL)
        if nested_blocks:
            # If nested blocks exist, find the last closing backticks
            last_backticks_index = response.rfind("```", match.start())
            if last_backticks_index > match.start():
                file_content = response[match.start(3):last_backticks_index]

        # Remove leading '#' and spaces from the file path
        file_path = re.sub(r'^#\s*', '', file_path)

        if file_path:
            # Call persist_file for each file found
            persist_file(thread_id, file_path, file_type, file_content)
        else:
            print(f"Debug: Empty file path found for {file_type} code block")

        # Return the original match (to keep the response unchanged)
        return match.group(0)

    # Process all matches in the response
    processed_response = re.sub(pattern, process_match, response, flags=re.DOTALL)

    return processed_response