import os
from typing import List
from langchain_anthropic import ChatAnthropic
from langchain.tools import BaseTool
from llms.base_llm_provider import BaseLLMProvider
from llms.llm_wrapper import LLMWrapper
from utils.debug_utils import debug_print


class AnthropicProvider(BaseLLMProvider):
    def get_llm(self, tools: List[BaseTool] = None, model: str = None) -> LLMWrapper:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        model = model or os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")
        llm = ChatAnthropic(model=model,max_tokens=4096)

        if tools:
            llm = llm.bind_tools(tools)

        debug_print(f"Initialized Anthropic LLM with model: {model}")
        return LLMWrapper(llm, "anthropic")

    def fetch_models(self) -> List[str]:
        # Replace with actual API call when available
        models = [
            "claude-3-5-sonnet-20240620",
            "claude-3-haiku-20240307"
        ]
        return models

    def get_default_model(self) -> str:
        return os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")