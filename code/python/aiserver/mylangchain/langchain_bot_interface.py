from abc import abstractmethod
from typing import List, Dict, Any
from bots.bot_interface import BotInterface
from langgraph.graph import StateGraph
from llms.llm_manager import LLMManager
from utils.debug_utils import debug_print
from langchain_core.messages import BaseMessage
from mylangchain.checkpointer_service import CheckpointerService
import logging

class LangchainBotInterface(BotInterface):
    def __init__(self):
        self.checkpointer = None
        self.graph = None
        self.llm_wrapper = None
        self.current_llm_provider = None
        self.current_llm_model = None
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def create_chatbot(self):
        pass

    @abstractmethod
    def create_graph(self) -> StateGraph:
        pass

    @abstractmethod
    def get_tools(self) -> List:
        pass

    def get_checkpointer(self, checkpointer_type: str = "sqlite", **kwargs):
        if self.checkpointer is None:
            self.checkpointer = CheckpointerService.get_checkpointer(checkpointer_type, **kwargs)
        return self.checkpointer

    def initialize(self, llm_provider=None, llm_model=None):
        self._update_llm_wrapper(llm_provider, llm_model)
        self.graph = self.create_graph()

    def _update_llm_wrapper(self, llm_provider, llm_model):
        if llm_provider != self.current_llm_provider or llm_model != self.current_llm_model:
            self.logger.debug(f"Updating LLM wrapper. New provider: {llm_provider}, New model: {llm_model}")
            if llm_provider or llm_model:
                self.llm_wrapper = LLMManager.get_llm(self.get_tools(), llm_provider, llm_model)
            else:
                self.llm_wrapper = LLMManager.get_default_llm(self.get_tools())
            self.current_llm_provider = llm_provider
            self.current_llm_model = llm_model
        else:
            self.logger.debug("LLM wrapper unchanged")

    def process_request(self, user_input: str, context: str, **kwargs) -> str:
        debug_print(f"{self.__class__.__name__} processing request. User input: {user_input}")
        debug_print(f"Context: {context}")
        debug_print(f"Additional kwargs: {kwargs}")

        thread_id = kwargs.pop('thread_id', '1')
        llm_provider = kwargs.pop('llm_provider', None)
        llm_model = kwargs.pop('llm_model', None)

        self._update_llm_wrapper(llm_provider, llm_model)

        if self.graph is None:
            self.initialize(llm_provider, llm_model)

        input_message = f"Context: {context}\n\nUser query: {user_input}"
        config = {"configurable": {"thread_id": thread_id}}

        snapshot = self.graph.get_state(config)
        debug_print(f"Snapshot before for thread_id: {thread_id}: {snapshot}")

        final_response = None
        for event in self.graph.stream({"messages": [("user", input_message)]}, config):
            for value in event.values():
                if isinstance(value["messages"][-1], BaseMessage):
                    final_response = value["messages"][-1].content

        debug_print(f"{self.__class__.__name__} raw response: {final_response}")

        processed_response = self.post_process_response(final_response, thread_id=thread_id, **kwargs)

        debug_print(f"{self.__class__.__name__} processed response: {processed_response}")
        debug_print(f"Snapshot after for thread_id: {thread_id}: {snapshot}")
        return processed_response

    def post_process_response(self, response: str, **kwargs) -> str:
        thread_id = kwargs.pop('thread_id', '1')
        debug_print(f"Post-processing response for thread_id: {thread_id}")
        return response

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
            },
            "thread_id": {
                "type": "string",
                "description": "The thread ID for conversation continuity",
                "default": "1"
            }
        }