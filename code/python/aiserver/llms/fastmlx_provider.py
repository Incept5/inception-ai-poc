import os
from typing import List, Optional
from .base_llm_provider import BaseLLMProvider


class FastMLXProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = os.getenv('FASTMLX_BASE_URL', 'http://0.0.0.0:8000')
        self.models_list = os.getenv('FASTMLX_MODELS', 'mlx-community/gemma-2-9b-it-4bit')

    @property
    def provider_name(self) -> str:
        return "fastmlx"

    def fetch_models(self) -> List[str]:
        models = [model.strip() for model in self.models_list.split(',')]
        if not models:
            # Fallback to a default model if the environment variable is empty
            models = ["mlx-community/gemma-2-9b-it-4bit"]
        return models

    def get_llm(self, model_name: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None):
        raise NotImplementedError("FastMLX provider does not support getLlm method")

    def get_chat_llm(self, model_name: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None):
        raise NotImplementedError("FastMLX provider does not support getChatLlm method")

    def get_default_model(self) -> str:
        available_models = self.fetch_models()
        if available_models:
            return available_models[0]
        return "No models available"