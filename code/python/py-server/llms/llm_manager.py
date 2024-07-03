# services/llm_manager.py

import os
from langchain_anthropic import ChatAnthropic
from langchain_experimental.llms.ollama_functions import OllamaFunctions, convert_to_ollama_tool
from langchain_openai import ChatOpenAI
from typing import List
from langchain.tools import BaseTool
from llms.llm_wrapper import LLMWrapper
from utils.debug_utils import debug_print

def get_llm(tools: List[BaseTool] = None, llm_provider: str = None, model: str = None) -> LLMWrapper:
    if llm_provider is None:
        llm_provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()

    if llm_provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        model = model or os.environ.get("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        llm = ChatAnthropic(model=model)

    elif llm_provider == "ollama":
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        model = model or os.environ.get("OLLAMA_MODEL", "llama2")
        llm = OllamaFunctions(base_url=base_url, model=model, format="json")
        if tools:
            converted_tools = [convert_to_ollama_tool(tool) for tool in tools]
            llm = llm.bind_tools(converted_tools)

    elif llm_provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        model = model or os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        llm = ChatOpenAI(model=model)

    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")

    if tools and llm_provider != "ollama":
        llm = llm.bind_tools(tools)

    debug_print(f"Initialized LLM for provider: {llm_provider}")
    return LLMWrapper(llm, llm_provider)