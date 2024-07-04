# config.py

import os
from utils.debug_utils import debug_print

class Config:
    LANGSMITH_API_KEY = os.environ.get("LANGSMITH_API_KEY")
    TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
    LANGCHAIN_TRACING_V2 = os.environ.get("LANGCHAIN_TRACING_V2", "true")
    LANGCHAIN_PROJECT = os.environ.get("LANGCHAIN_PROJECT", "LangGraph Tutorial")
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic").lower()
    OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2")

    @classmethod
    def validate(cls):
        if not cls.LANGSMITH_API_KEY or not cls.TAVILY_API_KEY:
            raise ValueError("Required API keys not found. Please check your .env file.")

        debug_print(f"LANGSMITH_API_KEY: {'*' * len(cls.LANGSMITH_API_KEY)}")
        debug_print(f"TAVILY_API_KEY: {'*' * len(cls.TAVILY_API_KEY)}")
        debug_print(f"LANGCHAIN_TRACING_V2: {cls.LANGCHAIN_TRACING_V2}")
        debug_print(f"LANGCHAIN_PROJECT: {cls.LANGCHAIN_PROJECT}")
        debug_print(f"LLM_PROVIDER: {cls.LLM_PROVIDER}")
        debug_print(f"OLLAMA_MODEL: {cls.OLLAMA_MODEL}")

Config.validate()