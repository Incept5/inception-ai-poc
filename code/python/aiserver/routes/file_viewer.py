from flask import Blueprint, jsonify, send_file, request
import os
import json
from utils.file_utils import FileUtils

file_viewer_blueprint = Blueprint('file_viewer', __name__)

BASE_DIR = '/data/persisted_files'
SYSTEM_SRC_DIR = '/system_src'

def debug_print(message):
    print(f"[DEBUG] {message}")

@file_viewer_blueprint.route('/files', methods=['GET'])
@file_viewer_blueprint.route('/files/<path:subpath>', methods=['GET'])
def get_file_structure(subpath=''):
    debug_print(f"Received request for subpath: {subpath}")
    root_dir = os.path.join(BASE_DIR, subpath)

    if not os.path.exists(root_dir):
        debug_print(f"Path not found: {root_dir}")
        return jsonify({"error": "Path not found"}), 404

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
            full_path = os.path.join(subpath, path, file)
            if full_path.startswith(os.sep):
                full_path = full_path[1:]  # Remove leading slash if present
            current[file] = full_path

    debug_print(f"Returning structure: {json.dumps(structure, indent=2)}")
    return jsonify(structure)

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

@file_viewer_blueprint.route('/update-files', methods=['POST'])
@file_viewer_blueprint.route('/update-files/<path:subpath>', methods=['POST'])
def update_files(subpath=''):
    debug_print(f"Received POST request to update files for subpath: {subpath}")

    source_path = os.path.join(BASE_DIR, subpath)
    destination_path = SYSTEM_SRC_DIR
    
    debug_print(f"Source path: {source_path}")
    debug_print(f"Destination path: {destination_path}")

    try:
        FileUtils.copy_files_exclude_weird_chars(source_path, destination_path)
        debug_print(f"Files copied from {source_path} to {destination_path}")
        return jsonify({"message": f"Files in {subpath} have been updated in the system"}), 200
    except FileNotFoundError as e:
        debug_print(f"Source path not found: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        debug_print(f"Error updating files: {str(e)}")
        return jsonify({"error": f"Error updating files: {str(e)}"}), 500

# Add this blueprint to your app.py
# from routes.file_viewer import file_viewer_blueprint
# app.register_blueprint(file_viewer_blueprint, url_prefix='/api')