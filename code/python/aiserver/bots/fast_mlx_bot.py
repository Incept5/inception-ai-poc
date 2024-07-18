import os
import requests
import json
from typing import Dict, Any
from bots.bot_interface import SimpleBotInterface
from utils.debug_utils import debug_print


class FastMlxBot(SimpleBotInterface):
    def __init__(self):
        self.base_url = os.getenv('FASTMLX_BASE_URL', 'http://0.0.0.0:8000')
        debug_print(f"FastMlxBot initialized with base URL: {self.base_url}")

    @property
    def bot_type(self) -> str:
        return "fast-mlx-bot"

    @property
    def description(self) -> str:
        return "FastMlx Bot - Direct interaction with FastMlx models"

    def simple_process_request(self, user_input: str, context: str, **kwargs) -> str:
        debug_print(f"FastMlxBot processing request. User input: {user_input}")
        debug_print(f"Context: {context}")
        debug_print(f"Additional kwargs: {kwargs}")

        model = "mlx-community/gemma-2-9b-it-4bit"
        debug_print(f"Using model: {model}")

        messages = [
            {"role": "user", "content": user_input}
        ]
        debug_print(f"Prepared messages: {messages}")

        try:
            debug_print(f"Sending POST request to {self.base_url}/v1/chat/completions")
            debug_print("Request payload:")
            debug_print(json.dumps({
                "model": model,
                "messages": messages,
                "max_tokens": 500
            }, indent=2))

            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "model": model,
                    "messages": messages,
                    "max_tokens": 500
                })
            )
            debug_print(f"Response status code: {response.status_code}")
            debug_print(f"Response headers: {response.headers}")

            response.raise_for_status()
            result = response.json()
            debug_print("API Response:")
            debug_print(json.dumps(result, indent=2))

            answer = result['choices'][0]['message']['content'].strip()

            debug_print(f"FastMlxBot response: {answer}")
            return answer
        except requests.RequestException as e:
            error_message = f"Error communicating with FastMlx API: {str(e)}"
            debug_print(error_message)
            debug_print(f"Response content (if any): {getattr(e.response, 'text', 'N/A')}")
            return error_message

    def get_config_options(self) -> Dict[str, Any]:
        return {
            "llm_provider": {
                "type": "string",
                "description": "The LLM provider to use",
                "default": "fastmlx"
            },
            "llm_model": {
                "type": "string",
                "description": "The FastMlx model to use",
            }
        }

    def get_available_models(self) -> list:
        debug_print(f"Fetching available models from {self.base_url}/v1/models")
        try:
            response = requests.get(f"{self.base_url}/v1/models")
            debug_print(f"Models API response status code: {response.status_code}")
            response.raise_for_status()
            models = response.json()
            debug_print(f"Available models: {models}")
            return [model['id'] for model in models['data']]
        except requests.RequestException as e:
            debug_print(f"Error fetching available models: {str(e)}")
            debug_print(f"Response content (if any): {getattr(e.response, 'text', 'N/A')}")
            return []