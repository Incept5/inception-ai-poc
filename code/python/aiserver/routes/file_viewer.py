from flask import Blueprint, jsonify, send_file, request
import os
import json
import re
from utils.partial_file_utils import PartialFileUtils
import logging

file_viewer_blueprint = Blueprint('file_viewer', __name__)

BASE_DIR = '/data/persisted_files'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_file_list(root_dir: str, subpath: str = '') -> list:
    """
    Generate a list of files for the given root directory.

    Args:
        root_dir (str): Path to the root directory
        subpath (str): Subpath to prepend to all file paths

    Returns:
        list: A list of dictionaries representing the files
    """
    file_list = []
    try:
        for root, _, files in os.walk(root_dir):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, root_dir)
                file_path = os.path.join(subpath, relative_path)
                if file_path.startswith(os.sep):
                    file_path = file_path[1:]  # Remove leading slash if present
                file_list.append({
                    "name": file,
                    "path": file_path,
                    "is_partial": PartialFileUtils.is_partial_file(full_path)
                })
    except Exception as e:
        logger.error(f"Error in get_file_list: {str(e)}")
        raise
    return file_list


def check_partial_files(file_list: list) -> bool:
    """
    Check if any files in the list are partial files.

    Args:
        file_list (list): The list of file dictionaries

    Returns:
        bool: True if any partial files are detected, False otherwise
    """
    return any(file['is_partial'] for file in file_list)


def generate_file_structure_response(root_dir: str, subpath: str = '') -> dict:
    """
    Generate the file structure response with the 'files' and 'partial_files_detected' attributes.

    Args:
        root_dir (str): Path to the root directory
        subpath (str): Subpath to prepend to all file paths

    Returns:
        dict: A dictionary containing the file list and partial files detection status
    """
    file_list = get_file_list(root_dir, subpath)
    partial_files_detected = check_partial_files(file_list)

    return {
        "files": file_list,
        "partial_files_detected": partial_files_detected
    }


@file_viewer_blueprint.route('/files', methods=['GET'])
@file_viewer_blueprint.route('/files/<path:subpath>', methods=['GET'])
def get_file_structure_route(subpath=''):
    logger.debug(f"Received request for subpath: {subpath}")

    # Input validation for subpath
    if not re.match(r'^[a-zA-Z0-9_\-./]*$', subpath):
        logger.warning(f"Invalid subpath: {subpath}")
        return jsonify({"error": "Invalid subpath"}), 400

    root_dir = os.path.join(BASE_DIR, subpath)

    if not os.path.exists(root_dir):
        logger.warning(f"Path not found: {root_dir}")
        return jsonify({"error": "Path not found"}), 404

    try:
        structure_response = generate_file_structure_response(root_dir, subpath)
        logger.debug(f"Returning structure: {json.dumps(structure_response, indent=2)}")
        return jsonify(structure_response)
    except Exception as e:
        logger.error(f"Error generating file structure: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@file_viewer_blueprint.route('/file/<path:file_path>', methods=['GET'])
def get_file_content(file_path):
    logger.debug(f"Received request for file: {file_path}")

    # Input validation for file_path
    if not re.match(r'^[a-zA-Z0-9_\-./]*$', file_path):
        logger.warning(f"Invalid file path: {file_path}")
        return jsonify({"error": "Invalid file path"}), 400

    full_path = os.path.join(BASE_DIR, file_path)
    if os.path.isfile(full_path):
        logger.debug(f"Sending file: {full_path}")
        return send_file(full_path)
    else:
        logger.warning(f"File not found: {full_path}")
        return jsonify({"error": "File not found"}), 404