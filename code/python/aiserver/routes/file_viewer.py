from flask import Blueprint, jsonify, send_file, request
import os
import json
from utils.file_utils import FileUtils

file_viewer_blueprint = Blueprint('file_viewer', __name__)

BASE_DIR = '/data/persisted_files'


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

    structure_response = FileUtils.generate_file_structure_response(root_dir, subpath)
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