# processors/persist_files_in_response.py

import re
from processors.persist_file import persist_file


def persist_files_in_response(thread_id: str, response: str) -> str:
    # Regular expression to find code blocks with file paths
    pattern = r"```(\w+)\s+([^\n]+)\n(.*?)```"

    def process_match(match):
        file_type = match.group(1)
        file_path = match.group(2)
        file_content = match.group(3)

        # Call persist_file for each file found
        persist_file(thread_id, file_path, file_type, file_content)

        # Return the original match (to keep the response unchanged)
        return match.group(0)

    # Process all matches in the response
    processed_response = re.sub(pattern, process_match, response, flags=re.DOTALL)

    return processed_response