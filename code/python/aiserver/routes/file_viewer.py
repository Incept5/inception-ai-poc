from flask import Blueprint, jsonify, send_file, request
import os
import json
import re
from utils.partial_file_utils import PartialFileUtils

file_viewer_blueprint = Blueprint('file_viewer', __name__)

BASE_DIR = '/data/persisted_files'

def debug_print(message):
    print(f"[DEBUG] {message}")

def get_file_structure(root_dir: str, subpath: str = '') -> dict:
    """
    Generate the file structure for the given root directory.

    Args:
        root_dir (str): Path to the root directory
        subpath (str): Subpath to prepend to all file paths

    Returns:
        dict: A dictionary representing the file structure
    """
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
            full_path = os.path.join(path, file)
            if full_path.startswith(os.sep):
                full_path = full_path[1:]  # Remove leading slash if present
            current[file] = os.path.join(subpath, full_path)
    return structure

def check_partial_files(structure: dict, root_dir: str) -> bool:
    """
    Check if any files in the structure are partial files.

    Args:
        structure (dict): The file structure dictionary
        root_dir (str): The root directory path

    Returns:
        bool: True if any partial files are detected, False otherwise
    """

    def check_recursive(current_structure, current_path):
        for key, value in current_structure.items():
            if isinstance(value, dict):
                if check_recursive(value, os.path.join(current_path, key)):
                    return True
            else:
                full_path = os.path.join(root_dir, value)
                if PartialFileUtils.is_partial_file(full_path):
                    return True
        return False

    return check_recursive(structure, '')

def generate_file_structure_response(root_dir: str, subpath: str = '') -> dict:
    """
    Generate the file structure response with the 'tree' and 'partial_files_detected' attributes.

    Args:
        root_dir (str): Path to the root directory
        subpath (str): Subpath to prepend to all file paths

    Returns:
        dict: A dictionary containing the file structure and partial files detection status
    """
    structure = get_file_structure(root_dir, subpath)
    partial_files_detected = check_partial_files(structure, root_dir)

    return {
        "tree": structure,
        "partial_files_detected": partial_files_detected
    }

@file_viewer_blueprint.route('/files', methods=['GET'])
@file_viewer_blueprint.route('/files/<path:subpath>', methods=['GET'])
def get_file_structure_route(subpath=''):
    debug_print(f"Received request for subpath: {subpath}")
    root_dir = os.path.join(BASE_DIR, subpath)

    if not os.path.exists(root_dir):
        debug_print(f"Path not found: {root_dir}")
        return jsonify({"error": "Path not found"}), 404

    structure_response = generate_file_structure_response(root_dir, subpath)
    debug_print(f"Returning structure: {json.dumps(structure_response, indent=2)}")
    return jsonify(structure_response)

@file_viewer_blueprint.route('/file/<path:file_path>', methods=['GET'])
def get_file_content(file_path):
    debug_print(f"Received request for file: {file_path}")
    full_path = os.path.join(BASE_DIR, file_path)
    if os.path.isfile(full_path):
        debug_print(f"Sending file: {full_path}")
        return send_file(full_path)
    else:
        debug_print(f"File not found: {full_path}")
        return jsonify({"error": "File not found"}), 404