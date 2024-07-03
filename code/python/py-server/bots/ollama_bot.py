import os
import requests
from typing import Dict, Any
from bots.bot_interface import BotInterface
from utils.debug_utils import debug_print


class OllamaBot(BotInterface):
    def __init__(self):
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        debug_print(f"OllamaBot initialized with base URL: {self.base_url}")

    @property
    def bot_type(self) -> str:
        return "ollama-bot"

    @property
    def description(self) -> str:
        return "Ollama Bot - Direct interaction with Ollama models"

    def process_request(self, user_input: str, context: str, **kwargs) -> str:
        debug_print(f"OllamaBot processing request. User input: {user_input}")
        debug_print(f"Context: {context}")
        debug_print(f"Additional kwargs: {kwargs}")

        model = kwargs.get('llm_model', 'llama2')  # Default to llama2 if no model specified

        prompt = f"Context: {context}\n\nHuman: {user_input}\n\nAssistant:"

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            answer = result.get('response', '').strip()

            debug_print(f"OllamaBot response: {answer}")
            return answer
        except requests.RequestException as e:
            error_message = f"Error communicating with Ollama: {str(e)}"
            debug_print(error_message)
            return error_message

    def get_config_options(self) -> Dict[str, Any]:
        return {
            "llm_model": {
                "type": "string",
                "description": "The Ollama model to use",
                "default": "llama2"
            }
        }