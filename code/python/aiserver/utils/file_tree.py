import os
import fnmatch
from typing import List


def parse_gitignore(root_dir: str) -> List[str]:
    gitignore_path = os.path.join(root_dir, '.gitignore')
    patterns = ['.git']  # Always ignore .git directory

    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            print(f"Reading .gitignore file: {gitignore_path}")
            patterns.extend([line.strip() for line in f if line.strip() and not line.startswith('#')])

    return patterns


def should_ignore(path: str, root_dir: str, ignore_patterns: List[str]) -> bool:
    rel_path = os.path.relpath(path, root_dir)

    for pattern in ignore_patterns:
        if pattern.endswith('/'):
            # If the pattern ends with '/', it should only match directories
            if os.path.isdir(path) and (fnmatch.fnmatch(rel_path, pattern[:-1]) or
                                        fnmatch.fnmatch(rel_path + '/', pattern)):
                return True
        else:
            # For patterns without trailing '/', match both files and directories
            if fnmatch.fnmatch(rel_path, pattern):
                return True

    return False


def generate_tree(root_dir: str, ignore_patterns: List[str], prefix: str = '') -> str:
    output = []
    entries = sorted(os.listdir(root_dir))

    ignore_patterns = parse_gitignore(root_dir) + ignore_patterns

    for i, entry in enumerate(entries):
        path = os.path.join(root_dir, entry)

        if should_ignore(path, root_dir, ignore_patterns):
            continue

        is_last = (i == len(entries) - 1)
        output.append(f"{prefix}{'└── ' if is_last else '├── '}{entry}")

        if os.path.isdir(path):
            output.append(generate_tree(
                path,
                ignore_patterns,
                prefix + ('    ' if is_last else '│   ')
            ))

    return '\n'.join(output)


def file_tree(input_dir: str) -> str:
    if not os.path.isdir(input_dir):
        return f"Error: {input_dir} is not a valid directory."

    tree = generate_tree(input_dir, [])
    return f".\n{tree}"


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python file_tree.py <directory_path>")
        sys.exit(1)

    directory = sys.argv[1]
    print(file_tree(directory))