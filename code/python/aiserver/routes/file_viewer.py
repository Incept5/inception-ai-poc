from flask import Blueprint, jsonify, send_file, request
import os
import json
from processors.file_processor import debug_print, copy_files, get_file_structure

file_viewer_blueprint = Blueprint('file_viewer', __name__)

BASE_DIR = '/data/persisted_files'
SYSTEM_SRC_DIR = '/system_src'

@file_viewer_blueprint.route('/files', methods=['GET'])
@file_viewer_blueprint.route('/files/<path:subpath>', methods=['GET'])
def get_file_structure_route(subpath=''):
    debug_print(f"Received request for file structure. Subpath: {subpath}")
    root_dir = os.path.join(BASE_DIR, subpath)

    if not os.path.exists(root_dir):
        debug_print(f"Path not found: {root_dir}")
        return jsonify({"error": "Path not found"}), 404

    structure = get_file_structure(root_dir)
    debug_print(f"Returning file structure: {json.dumps(structure, indent=2)}")
    return jsonify(structure)

@file_viewer_blueprint.route('/file/<path:file_path>', methods=['GET'])
def get_file_content(file_path):
    debug_print(f"Received request for file content. File path: {file_path}")
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
    debug_print(f"Received POST request to update files. Subpath: {subpath}")
    
    # Remove the '__threads' part from the subpath
    if subpath.startswith('__threads/'):
        subpath = '/'.join(subpath.split('/')[2:])
        debug_print(f"Adjusted subpath: {subpath}")
    
    source_path = os.path.join(BASE_DIR, '__threads', subpath)
    destination_path = os.path.join(SYSTEM_SRC_DIR, subpath)
    
    debug_print(f"Source path: {source_path}")
    debug_print(f"Destination path: {destination_path}")

    if not os.path.exists(source_path):
        debug_print(f"Source path not found: {source_path}")
        return jsonify({"error": "Source path not found"}), 404

    try:
        debug_print("Starting file update process...")
        copy_files(source_path, destination_path)
        debug_print("File update process completed successfully.")
        return jsonify({"message": f"Files in {subpath} have been updated in the system"}), 200
    except Exception as e:
        debug_print(f"Error updating files: {str(e)}")
        return jsonify({"error": f"Error updating files: {str(e)}"}), 500

# Add this blueprint to your app.py
# from routes.file_viewer import file_viewer_blueprint
# app.register_blueprint(file_viewer_blueprint, url_prefix='/api')