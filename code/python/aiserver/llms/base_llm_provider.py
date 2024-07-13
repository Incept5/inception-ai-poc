from abc import ABC, abstractmethod
from typing import List, Optional
from langchain.tools import BaseTool
from llms.llm_wrapper import LLMWrapper
from llms.base_audio_transcriber import BaseAudioTranscriber

class BaseLLMProvider(ABC):
    @abstractmethod
    def get_llm(self, tools: List[BaseTool] = None, model: str = None) -> LLMWrapper:
        pass

    @abstractmethod
    def fetch_models(self) -> List[str]:
        pass

    # Override this if the provider supports audio transcription
    def get_audio_transcriber(self) -> Optional[BaseAudioTranscriber]:
        return None