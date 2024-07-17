from flask import Blueprint, jsonify, request
import os
import traceback
from utils.file_utils import FileUtils
from processors.update_system_file import update_system_file

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
        updated_files = []
        for root, _, files in os.walk(source_path):
            for file in files:
                src_file = os.path.join(root, file)
                rel_path = os.path.relpath(src_file, source_path)
                dest_file = os.path.join(destination_path, rel_path)

                # Check if the file path contains weird characters
                if not FileUtils.has_weird_characters(rel_path):
                    # Read the content of the source file
                    with open(src_file, 'r', encoding='utf-8') as f:
                        file_content = f.read()

                    # Update the system file
                    update_system_file(SYSTEM_SRC_DIR, rel_path, file_content)
                    updated_files.append(rel_path)
                    debug_print(f"Updated file: {rel_path}")
                else:
                    debug_print(f"Skipped file with weird characters: {rel_path}")

        debug_print(f"Files updated in the system: {updated_files}")
        return jsonify({
            "message": f"Files in {subpath} have been updated in the system",
            "updated_files": updated_files
        }), 200
    except FileNotFoundError as e:
        error_message = f"Source path not found: {str(e)}"
        debug_print(error_message)
        debug_print(f"Full stack trace:\n{traceback.format_exc()}")
        return jsonify({"error": error_message}), 404
    except Exception as e:
        error_message = f"Error updating files: {str(e)}"
        debug_print(error_message)
        debug_print(f"Full stack trace:\n{traceback.format_exc()}")
        return jsonify({"error": error_message}), 500