import os
from typing import Optional
from flask import current_app
from bots.system_bots import SystemBotManager
from utils.file_utils import FileUtils

def update_system_file(system_root_dir: str, file_path: str, file_content: str) -> None:
    """
    Update a system file, checking for partial content and invoking the file fixing bot if necessary.

    Args:
        system_root_dir (str): The root directory of the system
        file_path (str): The path of the file to update, relative to the system root
        file_content (str): The new content for the file

    Raises:
        FileNotFoundError: If the file doesn't exist and partial content is detected
        Exception: For any other errors during the update process
    """
    full_path = os.path.join(system_root_dir, file_path)
    
    # Check if the file content is partial
    is_partial = any(FileUtils.is_partial_file(file_content) for pattern in FileUtils.PARTIAL_FILE_PATTERNS)

    if is_partial:
        # Check if the file already exists
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Cannot update non-existent file with partial content: {file_path}")

        # Invoke the file fixing bot
        file_fixing_bot = SystemBotManager.get_system_bot("file-fixing-bot")
        if file_fixing_bot is None:
            raise Exception("File fixing bot not found")

        # Read the original content
        with open(full_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Prepare the input for the file fixing bot
        bot_input = f"""<-- Original File Start -->
{original_content}
<-- Separator -->
{file_content}
<-- New File End -->"""

        # Process the content using the file fixing bot
        result = file_fixing_bot.process({"messages": [{"content": bot_input}]})
        processed_content = result["messages"][0]["content"]
    else:
        # If not partial, use the provided content as is
        processed_content = file_content

    # Write the processed content to the file
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(processed_content)

    print(f"Updated file: {file_path}")