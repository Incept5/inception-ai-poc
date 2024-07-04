from abc import abstractmethod
from typing import List, Dict, Any
from bots.bot_interface import BotInterface
from langgraph.graph import StateGraph
from llms.llm_manager import LLMManager
from utils.debug_utils import debug_print
from langchain_core.messages import BaseMessage

class LangchainBotInterface(BotInterface):
    @abstractmethod
    def create_chatbot(self):
        pass

    @abstractmethod
    def create_graph(self) -> StateGraph:
        pass

    @abstractmethod
    def get_tools(self) -> List:
        pass

    def process_request(self, user_input: str, context: str, **kwargs) -> str:
        debug_print(f"{self.__class__.__name__} processing request. User input: {user_input}")
        debug_print(f"Context: {context}")
        debug_print(f"Additional kwargs: {kwargs}")

        llm_provider = kwargs.get('llm_provider')
        llm_model = kwargs.get('llm_model')

        # If llm_provider or llm_model are provided, create a new LLMWrapper
        if llm_provider or llm_model:
            self.llm_wrapper = LLMManager.get_llm(self.get_tools(), llm_provider, llm_model)
        # Otherwise, use the default LLMWrapper created in the bot's __init__ method
        elif not hasattr(self, 'llm_wrapper'):
            self.llm_wrapper = LLMManager.get_default_llm(self.get_tools())

        graph = self.create_graph()

        input_message = f"Context: {context}\n\nUser query: {user_input}"

        final_response = None
        for event in graph.stream({"messages": [("user", input_message)]}):
            for value in event.values():
                if isinstance(value["messages"][-1], BaseMessage):
                    final_response = value["messages"][-1].content

        debug_print(f"{self.__class__.__name__} response: {final_response}")
        return final_response

    def get_config_options(self) -> Dict[str, Any]:
        return {
            "llm_provider": {
                "type": "string",
                "description": "The LLM provider to use",
                "default": None
            },
            "llm_model": {
                "type": "string",
                "description": "The specific LLM model to use",
                "default": None
            }
        }