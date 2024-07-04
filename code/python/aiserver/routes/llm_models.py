from flask import Blueprint, request, jsonify
from llms.llm_manager import LLMManager

llm_models_blueprint = Blueprint('llm_models', __name__)

@llm_models_blueprint.route('/llm-models', methods=['GET'])
def get_llm_models():
    provider = request.args.get('provider', '').lower()

    try:
        models = LLMManager.fetch_models(provider)
        return jsonify({"models": models})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to fetch models for provider {provider}: {str(e)}"}), 500