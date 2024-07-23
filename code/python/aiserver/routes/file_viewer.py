from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Dict, Optional
import os
import json
import re
from utils.partial_file_utils import PartialFileUtils
import logging

file_viewer_router = APIRouter()

BASE_DIR = '/data/persisted_files'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_file_list(root_dir: str, subpath: str = '') -> List[Dict[str, str]]:
    """
    Generate a list of files for the given root directory.

    Args:
        root_dir (str): Path to the root directory
        subpath (str): Subpath to prepend to all file paths

    Returns:
        List[Dict[str, str]]: A list of dictionaries representing the files
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


def check_partial_files(file_list: List[Dict[str, str]]) -> bool:
    """
    Check if any files in the list are partial files.

    Args:
        file_list (List[Dict[str, str]]): The list of file dictionaries

    Returns:
        bool: True if any partial files are detected, False otherwise
    """
    return any(file['is_partial'] for file in file_list)


def generate_file_structure_response(root_dir: str, subpath: str = '') -> Dict[str, any]:
    """
    Generate the file structure response with the 'files' and 'partial_files_detected' attributes.

    Args:
        root_dir (str): Path to the root directory
        subpath (str): Subpath to prepend to all file paths

    Returns:
        Dict[str, any]: A dictionary containing the file list and partial files detection status
    """
    file_list = get_file_list(root_dir, subpath)
    partial_files_detected = check_partial_files(file_list)

    return {
        "files": file_list,
        "partial_files_detected": partial_files_detected
    }


@file_viewer_router.get('/files')
@file_viewer_router.get('/files/{subpath:path}')
async def get_file_structure_route(subpath: Optional[str] = ''):
    logger.debug(f"Received request for subpath: {subpath}")

    # Input validation for subpath
    if not re.match(r'^[a-zA-Z0-9_\-./]*$', subpath):
        logger.warning(f"Invalid subpath: {subpath}")
        raise HTTPException(status_code=400, detail="Invalid subpath")

    root_dir = os.path.join(BASE_DIR, subpath)

    if not os.path.exists(root_dir):
        logger.warning(f"Path not found: {root_dir}")
        raise HTTPException(status_code=404, detail="Path not found")

    try:
        structure_response = generate_file_structure_response(root_dir, subpath)
        logger.debug(f"Returning structure: {json.dumps(structure_response, indent=2)}")
        return JSONResponse(content=structure_response)
    except Exception as e:
        logger.error(f"Error generating file structure: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@file_viewer_router.get('/file/{file_path:path}')
async def get_file_content(file_path: str):
    logger.debug(f"Received request for file: {file_path}")

    # Input validation for file_path
    if not re.match(r'^[a-zA-Z0-9_\-./]*$', file_path):
        logger.warning(f"Invalid file path: {file_path}")
        raise HTTPException(status_code=400, detail="Invalid file path")

    full_path = os.path.join(BASE_DIR, file_path)
    if os.path.isfile(full_path):
        logger.debug(f"Sending file: {full_path}")
        return FileResponse(full_path)
    else:
        logger.warning(f"File not found: {full_path}")
        raise HTTPException(status_code=404, detail="File not found")