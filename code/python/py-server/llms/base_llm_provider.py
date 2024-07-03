from abc import ABC, abstractmethod
from typing import List
from langchain.tools import BaseTool
from llms.llm_wrapper import LLMWrapper

class BaseLLMProvider(ABC):
    @abstractmethod
    def get_llm(self, tools: List[BaseTool] = None, model: str = None) -> LLMWrapper:
        pass

    @abstractmethod
    def fetch_models(self) -> List[str]:
        pass