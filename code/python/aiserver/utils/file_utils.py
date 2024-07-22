import os
import shutil
import re

class FileUtils:
    # List of regexes to ignore when copying files
    IGNORE_PATTERNS = [
        r'\.git',  # Ignore .git directories
        r'\.vscode',  # Ignore .vscode directories
        r'__pycache__',  # Ignore Python cache directories
        r'\.pyc$',  # Ignore Python compiled files
        r'\.pyo$',  # Ignore Python optimized files
        r'\.swp$',  # Ignore Vim swap files
        r'~$',  # Ignore backup files
        r'snippets',  # Ignore snippets directory
        r'node_modules',  # Ignore node_modules directory
        r'\.DS_Store',  # Ignore macOS system files
    ]

    @staticmethod
    def copy_files(source_path: str, destination_path: str) -> None:
        """
        Copy files from source to destination.
        If source is a file, it copies the file to the destination.
        If source is a directory, it copies the entire directory to the destination.

        Args:
            source_path (str): Path to the source file or directory
            destination_path (str): Path to the destination

        Raises:
            FileNotFoundError: If the source path does not exist
            Exception: For any other errors during the copy process
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source path not found: {source_path}")

        try:
            if os.path.isfile(source_path):
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                shutil.copy2(source_path, destination_path)
                print(f"Copied file: {source_path} -> {destination_path}")
            else:
                shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
                print(f"Copied directory: {source_path} -> {destination_path}")
        except Exception as e:
            raise Exception(f"Error copying files: {str(e)}")

    @staticmethod
    def copy_files_exclude_weird_chars(source_path: str, destination_path: str) -> None:
        """
        Copy files from source to destination, excluding files with weird characters in the path
        and files/directories matching the ignore patterns.
        If source is a file, it copies the file to the destination if it doesn't contain weird characters
        and doesn't match any ignore patterns.
        If source is a directory, it copies the entire directory to the destination, excluding files with
        weird characters and files/directories matching the ignore patterns.

        Args:
            source_path (str): Path to the source file or directory
            destination_path (str): Path to the destination

        Raises:
            FileNotFoundError: If the source path does not exist
            Exception: For any other errors during the copy process
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source path not found: {source_path}")

        def should_ignore(path):
            # Check for weird characters
            if FileUtils.has_weird_characters(path):
                return True

            # Check against ignore patterns
            for pattern in FileUtils.IGNORE_PATTERNS:
                if re.search(pattern, path):
                    return True

            return False

        try:
            if os.path.isfile(source_path):
                if not should_ignore(source_path):
                    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                    shutil.copy2(source_path, destination_path)
                    print(f"Copied file: {source_path} -> {destination_path}")
                else:
                    print(f"Warning: Excluded file: {source_path}")
            else:
                for root, dirs, files in os.walk(source_path):
                    # Remove directories that should be ignored
                    dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d))]

                    for file in files:
                        src_file = os.path.join(root, file)
                        rel_path = os.path.relpath(src_file, source_path)
                        dest_file = os.path.join(destination_path, rel_path)

                        if not should_ignore(rel_path):
                            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                            shutil.copy2(src_file, dest_file)
                            print(f"Copied file: {src_file} -> {dest_file}")
                        else:
                            print(f"Warning: Excluded file: {src_file}")
        except Exception as e:
            raise Exception(f"Error copying files: {str(e)}")

    @staticmethod
    def has_weird_characters(path: str) -> bool:
        """
        Check if a file path contains weird characters.

        Args:
            path (str): The file path to check

        Returns:
            bool: True if the path contains weird characters, False otherwise
        """
        return bool(re.search(r'[^a-zA-Z0-9_\-./\\]', path))