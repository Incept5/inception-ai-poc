import os
import requests
from typing import List
from langchain_groq import ChatGroq
from langchain.tools import BaseTool
from llms.llm_wrapper import LLMWrapper
from utils.debug_utils import debug_print


class GroqProvider:
    def get_llm(self, tools: List[BaseTool] = None, model: str = None) -> LLMWrapper:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        model = model or os.environ.get("GROQ_MODEL", "llama3-groq-70b-8192-tool-use-preview")

        llm = ChatGroq(
            temperature=0,
            model=model,
            api_key=api_key
        )

        if tools:
            llm = llm.bind_tools(tools)

        debug_print(f"Initialized Groq LLM with model: {model}")
        return LLMWrapper(llm, "groq")

    def fetch_models(self) -> List[str]:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            debug_print("Groq API key not found")
            return []

        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        try:
            response = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
            if response.status_code == 200:
                models = response.json().get('data', [])
                return [model['id'] for model in models]
            else:
                debug_print(f"Failed to fetch Groq models. Status code: {response.status_code}")
                return []
        except Exception as e:
            debug_print(f"Error fetching Groq models: {str(e)}")
            return []

    def get_default_model(self) -> str:
        return os.environ.get("GROQ_MODEL", "llama3-groq-70b-8192-tool-use-preview")