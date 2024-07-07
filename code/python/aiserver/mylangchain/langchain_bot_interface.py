import json
from abc import abstractmethod
from typing import List, Dict, Any, Generator, Optional
from bots.bot_interface import BotInterface
from langgraph.graph import StateGraph
from llms.llm_manager import LLMManager
from utils.debug_utils import debug_print
from langchain_core.messages import BaseMessage
from mylangchain.checkpointer_service import CheckpointerService
from processors.persist_files_in_response import persist_files_in_response
from mylangchain.retriever_manager import retriever_manager
import logging


class LangchainBotInterface(BotInterface):
    def __init__(self):
        self.checkpointer = None
        self.graph = None
        self.llm_wrapper = None
        self.current_llm_provider = None
        self.current_llm_model = None
        self.logger = logging.getLogger(__name__)
        self.retriever = None

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

    def initialize(self, llm_provider=None, llm_model=None, retriever_name=None):
        self._update_llm_wrapper(llm_provider, llm_model)
        self._update_retriever(retriever_name)
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

    def _update_retriever(self, retriever_name):
        if retriever_name:
            self.retriever = retriever_manager.get_retriever(retriever_name)
            if self.retriever:
                self.logger.debug(f"Retriever updated for {retriever_name}")
            else:
                self.logger.warning(f"Failed to get retriever for {retriever_name}")
        else:
            self.retriever = None
            self.logger.debug("Retriever set to None")

    def process_request(self, user_input: str, context: str, **kwargs) -> Generator[Dict[str, Any], None, None]:
        debug_print(f"{self.__class__.__name__} processing request. User input: {user_input}")
        debug_print(f"Context: {context}")
        debug_print(f"Additional kwargs: {kwargs}")

        thread_id = kwargs.pop('thread_id', '1')
        llm_provider = kwargs.pop('llm_provider', None)
        llm_model = kwargs.pop('llm_model', None)
        retriever_name = kwargs.pop('retriever_name', None)

        self.initialize(llm_provider, llm_model, retriever_name)

        input_message = f"Context: {context}\n\nUser query: {user_input}"
        config = {"configurable": {"thread_id": thread_id}}

        last_event = None
        try:
            for event in self.graph.stream({"messages": [("user", input_message)]}, config):
                debug_print(f"Event: {event}")

                if last_event is not None:
                    yield from self.process_and_emit_content(last_event, "intermediate", thread_id)

                last_event = event

            if last_event is not None:
                yield from self.process_and_emit_content(last_event, "final", thread_id)
            else:
                yield {"type": "error", "content": "No response generated"}

        except Exception as e:
            self.logger.error(f"Error in process_request: {str(e)}", exc_info=True)
            yield {"type": "error", "content": f"An error occurred: {str(e)}"}

    def process_and_emit_content(self, event: Dict[str, Any], step_type: str, thread_id: str) -> Generator[
        Dict[str, Any], None, None]:
        for key, value in event.items():
            if isinstance(value.get("messages", [])[-1], BaseMessage):
                content = value["messages"][-1].content
                if content is not None:
                    if isinstance(content, str):
                        yield from self.process_content(content, step_type, thread_id)
                    else:
                        yield from self.process_content(json.dumps(content), step_type, thread_id)

    def process_content(self, content: str, step_type: str, thread_id: str) -> Generator[Dict[str, Any], None, None]:
        print(f"Processing content (step_type: {step_type}):")
        print(f"Raw content: {content[:200]}...")  # Print first 200 characters

        def process_item(item):
            if isinstance(item, dict) and "text" in item:
                return item["text"]
            return json.dumps(item) if isinstance(item, (dict, list)) else str(item)

        try:
            parsed_content = json.loads(content)
            if isinstance(parsed_content, list):
                items = parsed_content
            else:
                items = [parsed_content]
        except json.JSONDecodeError:
            items = [content]

        for item in items:
            processed_item = process_item(item)
            processed_content = self.process_response_content(processed_item, thread_id)

            if self.should_emit_response(processed_content, step_type):
                yield {"type": step_type, "content": processed_content}

        print(
            f"Processed content: {processed_content[:200]}...")  # Print first 200 characters of the last processed item

    def process_response_content(self, content: str, thread_id: str) -> str:
        """
        Process the response content. This method now includes file saving functionality.

        :param content: The original response content
        :param thread_id: The thread ID for the current conversation
        :return: The processed response content
        """
        # Attempt to save any files in the response
        persist_files_in_response(thread_id, content)

        # Perform any additional processing (can be overridden in subclasses)
        return self.post_process_response(content, thread_id=thread_id)

    def post_process_response(self, content: str, **kwargs) -> str:
        """
        Post-process the response content. This method can be overridden in subclasses
        to implement custom processing of the response content.

        :param content: The original response content
        :param kwargs: Additional keyword arguments
        :return: The processed response content
        """
        return content  # Default implementation returns the content unchanged

    def should_emit_response(self, content: str, step_type: str) -> bool:
        """
        Determine if a response should be emitted.
        Override this method in subclasses to customize response emission behavior.

        :param content: The content to be emitted
        :param step_type: The type of step ('intermediate' or 'final')
        :return: True if the response should be emitted, False otherwise
        """
        debug_print(f"Deciding whether to emit response (step_type: {step_type})")
        return True  # Emit all responses by default

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
            },
            "retriever_name": {
                "type": "string",
                "description": "The name of the retriever to use for RAG",
                "default": None
            }
        }