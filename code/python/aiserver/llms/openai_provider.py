import os
import requests
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from llms.base_llm_provider import BaseLLMProvider
from llms.llm_wrapper import LLMWrapper
from llms.base_audio_transcriber import BaseAudioTranscriber
from llms.openai_audio_transcriber import OpenAIAudioTranscriber
from utils.debug_utils import debug_print


class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.audio_transcriber = OpenAIAudioTranscriber()

    def get_llm(self, tools: List[BaseTool] = None, model: str = None) -> LLMWrapper:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        model = model or os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        llm = ChatOpenAI(model=model)

        if tools:
            llm = llm.bind_tools(tools)

        debug_print(f"Initialized OpenAI LLM with model: {model}")
        return LLMWrapper(llm, "openai")

    def fetch_models(self) -> List[str]:
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            debug_print("OpenAI API key not found")
            return []

        headers = {
            "Authorization": f"Bearer {openai_api_key}"
        }
        try:
            response = requests.get("https://api.openai.com/v1/models", headers=headers)
            if response.status_code == 200:
                models = response.json().get('data', [])
                return [model['id'] for model in models]
            else:
                debug_print(f"Failed to fetch OpenAI models. Status code: {response.status_code}")
                return []
        except Exception as e:
            debug_print(f"Error fetching OpenAI models: {str(e)}")
            return []

    def get_audio_transcriber(self) -> Optional[BaseAudioTranscriber]:
        return self.audio_transcriber