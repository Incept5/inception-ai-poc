import os
import requests
from typing import List
from langchain_experimental.llms.ollama_functions import OllamaFunctions, convert_to_ollama_tool
from langchain.tools import BaseTool
from llms.base_llm_provider import BaseLLMProvider
from llms.llm_wrapper import LLMWrapper
from utils.debug_utils import debug_print


class OllamaProvider(BaseLLMProvider):
    def get_llm(self, tools: List[BaseTool] = None, model: str = None) -> LLMWrapper:
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        model = model or os.environ.get("OLLAMA_MODEL", "llama2")
        llm = OllamaFunctions(base_url=base_url, model=model, format="json")

        if tools:
            converted_tools = [convert_to_ollama_tool(tool) for tool in tools]
            llm = llm.bind_tools(converted_tools)

        debug_print(f"Initialized Ollama LLM with model: {model}")
        return LLMWrapper(llm, "ollama")

    def fetch_models(self) -> List[str]:
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