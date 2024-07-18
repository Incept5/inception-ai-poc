import os
from typing import List, Dict
from langchain.tools import BaseTool
from llms.llm_wrapper import LLMWrapper
from llms.anthropic_provider import AnthropicProvider
from llms.ollama_provider import OllamaProvider
from llms.openai_provider import OpenAIProvider
from llms.groq_provider import GroqProvider
from utils.debug_utils import debug_print

class LLMManager:
    providers: Dict[str, BaseTool] = {
        "anthropic": AnthropicProvider(),
        "ollama": OllamaProvider(),
        "openai": OpenAIProvider(),
        "groq": GroqProvider()
    }

    @classmethod
    def get_llm(cls, tools: List[BaseTool] = None, llm_provider: str = None, model: str = None) -> LLMWrapper:
        if llm_provider is None:
            llm_provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()

        if llm_provider not in cls.providers:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")

        provider = cls.providers[llm_provider]
        debug_print(f"Using LLM provider: {llm_provider}")
        result = provider.get_llm(tools, model)
        debug_print(f"LLM provider: {result.provider}, model: {model}")
        return result

    @classmethod
    def get_default_llm(cls, tools: List[BaseTool] = None) -> LLMWrapper:
        llm_provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()
        model = os.environ.get(f"{llm_provider.upper()}_MODEL")
        return cls.get_llm(tools, llm_provider, model)

    @classmethod
    def fetch_models(cls, llm_provider: str) -> List[str]:
        if llm_provider not in cls.providers:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")

        provider = cls.providers[llm_provider]
        return provider.fetch_models()