import os
import requests
from flask import Blueprint, request, jsonify
from utils.debug_utils import debug_print

llm_models_blueprint = Blueprint('llm_models', __name__)

def fetch_ollama_models():
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    try:
        response = requests.get(f"{ollama_base_url}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [model['name'] for model in models]
        else:
            debug_print(f"Failed to fetch Ollama models. Status code: {response.status_code}")
            return []
    except Exception as e:
        debug_print(f"Error fetching Ollama models: {str(e)}")
        return []

def fetch_openai_models():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        debug_print("OpenAI API key not found")
        return []

    headers = {
        "Authorization": f"Bearer {openai_api_key}"
    }
    try:
        response = requests.get("https://api.openai.com/v1/models", headers=headers)
        if response.status_code == 200:
            models = response.json().get('data', [])
            return [model['id'] for model in models]
        else:
            debug_print(f"Failed to fetch OpenAI models. Status code: {response.status_code}")
            return []
    except Exception as e:
        debug_print(f"Error fetching OpenAI models: {str(e)}")
        return []

def fetch_anthropic_models():
    # Replace with the actual API call if available, here is a placeholder
    try:
        # Placeholder: Replace with actual call to Anthropic API
        models = [
            "claude-3-5-sonnet-20240620", "claude-3-haiku-20240307"
        ]
        return models
    except Exception as e:
        debug_print(f"Error fetching Anthropic models: {str(e)}")
        return []

@llm_models_blueprint.route('/llm-models', methods=['GET'])
def get_llm_models():
    provider = request.args.get('provider', '').lower()

    if provider == 'ollama':
        models = fetch_ollama_models()
    elif provider == 'openai':
        models = fetch_openai_models()
    elif provider == 'anthropic':
        models = fetch_anthropic_models()
    else:
        return jsonify({"error": "Invalid LLM provider"}), 400

    if models:
        return jsonify({"models": models})
    else:
        return jsonify({"error": f"Failed to fetch models for provider {provider}"}), 500
