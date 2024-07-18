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

@llm_models_blueprint.route('/llm-providers', methods=['GET'])
def get_llm_providers():
    try:
        providers_data = []
        for provider_name, provider in LLMManager.providers.items():
            models = provider.fetch_models()
            default_model = provider.get_default_model()
            
            # Ensure the default model is the first in the list
            if default_model in models:
                models.remove(default_model)
            models.insert(0, default_model)
            
            providers_data.append({
                "provider": provider_name,
                "models": models
            })
        
        return jsonify({"providers": providers_data})
    except Exception as e:
        return jsonify({"error": f"Failed to fetch LLM providers and models: {str(e)}"}), 500