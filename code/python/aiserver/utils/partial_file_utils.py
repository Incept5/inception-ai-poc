import re

class PartialFileUtils:
    # Updated regexes to detect partial files
    PARTIAL_FILE_PATTERNS = [
        r'#\s*\.\.\.\s*\(',  # Matches "# ... ("
        r'//\s*.*?\.\.\.\s*\(',  # Matches "// ... (" with optional whitespace and content before "..."
        r'\[\.\.\.\s*existing\s*content\s*\.\.\.\]',  # Matches "[... existing content ...]"
        r'\[\.\.\.\s*.*?\.\.\.\]',  # Matches "[... ...]" with any content, including "anything"
        r'<!--\s*\.\.\.',  # Matches "<!-- ..."
    ]

    @staticmethod
    def is_partial_file_content(content: str) -> bool:
        """
        Check if the given content is a partial file based on its content.

        Args:
            content (str): The content to check

        Returns:
            bool: True if the content is partial, False otherwise
        """
        for pattern in PartialFileUtils.PARTIAL_FILE_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                return True
        return False

    @staticmethod
    def is_partial_file(file_path: str) -> bool:
        """
        Check if a file is a partial file based on its content.

        Args:
            file_path (str): Path to the file

        Returns:
            bool: True if the file is a partial file, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return PartialFileUtils.is_partial_file_content(content)
        except Exception:
            # If we can't read the file, assume it's not partial
            return False

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python partial_file_utils.py <input_string>")
        sys.exit(1)

    input_string = sys.argv[1]
    is_partial = PartialFileUtils.is_partial_file_content(input_string)
    print(f"Is partial content: {is_partial}")

if __name__ == "__main__":
    main()