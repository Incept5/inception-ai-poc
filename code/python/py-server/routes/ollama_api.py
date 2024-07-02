# routes/ollama_api.py

import os
import requests
from flask import Blueprint, jsonify
from utils.debug_utils import debug_print

ollama_blueprint = Blueprint('ollama', __name__)

@ollama_blueprint.route('/ollama-models', methods=['GET'])
def get_ollama_models():
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    try:
        response = requests.get(f"{ollama_base_url}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            return jsonify({"models": [model['name'] for model in models]})
        else:
            debug_print(f"Failed to fetch Ollama models. Status code: {response.status_code}")
            return jsonify({"error": "Failed to fetch Ollama models"}), 500
    except Exception as e:
        debug_print(f"Error fetching Ollama models: {str(e)}")
        return jsonify({"error": str(e)}), 500