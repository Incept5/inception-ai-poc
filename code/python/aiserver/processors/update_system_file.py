import os
from typing import Optional
from flask import current_app
from bots.system_bots import SystemBotManager
from utils.file_utils import FileUtils
from utils.partial_file_utils import PartialFileUtils


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
    print(f"[DEBUG] Updating system file: {file_path}")
    print(f"[DEBUG] System root directory: {system_root_dir}")

    full_path = os.path.join(system_root_dir, file_path)
    print(f"[DEBUG] Full file path: {full_path}")

    # Check if the file content is partial using PartialFileUtils
    is_partial = PartialFileUtils.is_partial_file_content(file_content)
    print(f"[DEBUG] Is file content partial? {is_partial}")

    if is_partial:
        print("[DEBUG] Handling partial file content")
        # Check if the file already exists
        if not os.path.exists(full_path):
            print(f"[ERROR] Cannot update non-existent file with partial content: {file_path}")
            raise FileNotFoundError(f"Cannot update non-existent file with partial content: {file_path}")

        # Invoke the file fixing bot
        file_fixing_bot = SystemBotManager.get_system_bot("file-fixing-bot")
        if file_fixing_bot is None:
            print("[ERROR] File fixing bot not found")
            raise Exception("File fixing bot not found")

        print("[DEBUG] Reading original file content")
        # Read the original content
        with open(full_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        print("[DEBUG] Preparing input for file fixing bot")
        # Prepare the input for the file fixing bot
        bot_input = f"""<-- Original File Start -->
{original_content}
<-- Separator -->
{file_content}
<-- New File End -->"""

        print("[DEBUG] Processing content using file fixing bot")
        # Process the content using the file fixing bot
        result = file_fixing_bot.process({"messages": [{"content": bot_input}]})
        processed_content = result["messages"][0]["content"]
        print("[DEBUG] File fixing bot processing complete")
    else:
        print("[DEBUG] Using provided content as is (not partial)")
        # If not partial, use the provided content as is
        processed_content = file_content

    print(f"[DEBUG] Writing processed content to file: {full_path}")
    # Write the processed content to the file
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(processed_content)

    print(f"[DEBUG] Successfully updated file: {file_path}")