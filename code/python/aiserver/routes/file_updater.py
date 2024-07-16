from flask import Blueprint, jsonify
import os
from utils.file_utils import FileUtils

file_updater_blueprint = Blueprint('file_updater', __name__)

BASE_DIR = '/data/persisted_files'
SYSTEM_SRC_DIR = '/system_src'


def debug_print(message):
    print(f"[DEBUG] {message}")


@file_updater_blueprint.route('/update-files', methods=['POST'])
@file_updater_blueprint.route('/update-files/<path:subpath>', methods=['POST'])
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