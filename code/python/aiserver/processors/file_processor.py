import os
import shutil
import re

def debug_print(message):
    print(f"[DEBUG] {message}")

def is_valid_filename(filename):
    # Allow alphanumeric characters, spaces, slashes, dots, underscores, and hyphens
    return re.match(r'^[\w\s/.-]+$', filename) is not None

def copy_files(source_path, destination_path):
    debug_print(f"Starting file copy process:")
    debug_print(f"Source path: {source_path}")
    debug_print(f"Destination path: {destination_path}")
    
    if os.path.isfile(source_path):
        if is_valid_filename(os.path.basename(source_path)):
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            shutil.copy2(source_path, destination_path)
            debug_print(f"Copied file: {source_path} -> {destination_path}")
        else:
            debug_print(f"Skipped invalid filename: {source_path}")
    else:
        for root, dirs, files in os.walk(source_path):
            for file in files:
                if is_valid_filename(file):
                    rel_path = os.path.relpath(root, source_path)
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(destination_path, rel_path, file)
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    shutil.copy2(src_file, dst_file)
                    debug_print(f"Copied file: {src_file} -> {dst_file}")
                else:
                    debug_print(f"Skipped invalid filename: {os.path.join(root, file)}")
    
    debug_print("File copy process completed.")

def get_file_structure(root_dir):
    debug_print(f"Getting file structure for: {root_dir}")
    structure = {}
    for root, dirs, files in os.walk(root_dir):
        path = os.path.relpath(root, root_dir)
        current = structure
        if path != '.':
            for folder in path.split(os.sep):
                if folder not in current:
                    current[folder] = {}
                current = current[folder]
        for file in files:
            if is_valid_filename(file):
                full_path = os.path.join(path, file)
                if full_path.startswith(os.sep):
                    full_path = full_path[1:]  # Remove leading slash if present
                current[file] = full_path
                debug_print(f"Added file to structure: {full_path}")
            else:
                debug_print(f"Skipped invalid filename in structure: {os.path.join(root, file)}")
    
    debug_print("File structure retrieval completed.")
    return structure