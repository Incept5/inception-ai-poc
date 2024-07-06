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

    def process_request(self, user_input: str, context: str, **kwargs) -> Generator[Dict[str, Any], None, None]:
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
        debug_print(f"Processing content (step_type: {step_type}):")
        debug_print(f"Raw content: {content[:200]}...")  # Print first 200 characters to avoid overwhelming logs

        try:
            content_list = json.loads(content)
            debug_print(f"Content successfully parsed as JSON")

            if isinstance(content_list, list):
                debug_print(f"Content is a list with {len(content_list)} items")
                for index, item in enumerate(content_list):
                    debug_print(f"Processing item {index + 1}/{len(content_list)}")
                    processed_content = self.process_response_content(json.dumps(item), thread_id)
                    debug_print(f"Processed item {index + 1}: {processed_content[:200]}...")

                    if self.should_emit_response(processed_content, step_type):
                        debug_print(f"Emitting response for item {index + 1}")
                        yield {"type": step_type, "content": processed_content}
                    else:
                        debug_print(f"Skipping emission for item {index + 1}")
            else:
                debug_print("Content is not a list, processing as a single item")
                processed_content = self.process_response_content(content, thread_id)
                debug_print(f"Processed content: {processed_content[:200]}...")

                if self.should_emit_response(processed_content, step_type):
                    debug_print("Emitting response for single item")
                    yield {"type": step_type, "content": processed_content}
                else:
                    debug_print("Skipping emission for single item")
        except json.JSONDecodeError:
            debug_print("Content is not valid JSON, processing as plain text")
            processed_content = self.process_response_content(content, thread_id)
            debug_print(f"Processed content: {processed_content[:200]}...")

            if self.should_emit_response(processed_content, step_type):
                debug_print("Emitting response for plain text content")
                yield {"type": step_type, "content": processed_content}
            else:
                debug_print("Skipping emission for plain text content")

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
            }
        }