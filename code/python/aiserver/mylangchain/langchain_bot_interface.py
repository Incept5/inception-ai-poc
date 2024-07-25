import json
from abc import abstractmethod
from typing import List, Dict, Any, Generator, Optional
from bots.sync_bot_interface import SyncBotInterface
from langgraph.graph import StateGraph
from llms.llm_manager import LLMManager
from utils.debug_utils import debug_print
from langchain_core.messages import BaseMessage
from langchain_core.runnables.config import RunnableConfig
from mylangchain.checkpointer_service import CheckpointerService
from processors.persist_files_in_response import persist_files_in_response
from mylangchain.retriever_manager import RetrieverManager
from mylangchain.retriever.retriever_builder import retriever_builder
import logging


class LangchainBotInterface(SyncBotInterface):
    def __init__(self, retriever_name: Optional[str] = None, default_llm_provider: Optional[str] = None, default_llm_model: Optional[str] = None):
        self.checkpointer = None
        self.graph = None
        self.llm_wrapper = None
        self.current_llm_provider = None
        self.current_llm_model = None
        self.logger = logging.getLogger(__name__)
        self.is_initialized = False
        self.retriever_manager = RetrieverManager()
        self.retriever_name = retriever_name
        self.retriever = None
        self.default_llm_provider = default_llm_provider
        self.default_llm_model = default_llm_model

    @abstractmethod
    def create_graph(self) -> StateGraph:
        pass

    @abstractmethod
    def get_tools(self) -> List:
        pass

    def getGraphConfig(self, thread_id: str) -> RunnableConfig:
        return RunnableConfig(recursion_limit=50, configurable={"thread_id": thread_id})

    def get_checkpointer(self, checkpointer_type: str = "sqlite", **kwargs):
        if self.checkpointer is None:
            self.checkpointer = CheckpointerService.get_checkpointer(checkpointer_type, **kwargs)
        return self.checkpointer

    def get_retriever(self, name: str):
        return self.retriever_manager.get_retriever(name)

    def initialize(self, llm_provider=None, llm_model=None):
        # This method is now a no-op
        pass

    def lazy_init_langchain(self, llm_provider=None, llm_model=None):
        llm_changed = self._update_llm_wrapper(llm_provider, llm_model)
        if not self.is_initialized or llm_changed:
            self.lazy_init_retriever()
            self.graph = self.create_graph()
            self.is_initialized = True

    def lazy_init_retriever(self):
        if self.retriever_name and self.retriever is None:
            self.retriever = retriever_builder.get_retriever(self.retriever_name)

    def _update_llm_wrapper(self, llm_provider, llm_model) -> bool:
        debug_print("Updating LLM wrapper")
        debug_print(f"Current LLM provider: {self.current_llm_provider}, Current LLM model: {self.current_llm_model}")
        debug_print(f"New LLM provider: {llm_provider}, New LLM model: {llm_model}")

        should_update = (
            llm_provider != self.current_llm_provider
            or llm_model != self.current_llm_model
            or self.llm_wrapper is None
        )

        if should_update:
            debug_print(f"Updating LLM wrapper. New provider: {llm_provider}, New model: {llm_model}")
            if llm_provider and llm_model:
                self.llm_wrapper = LLMManager.get_llm(self.get_tools(), llm_provider, llm_model)
                self.llm = self.llm_wrapper.llm
            else:
                debug_print("Using default LLM wrapper")
                self.llm_wrapper = LLMManager.get_default_llm(self.get_tools())
                self.llm = self.llm_wrapper.llm
            self.current_llm_provider = llm_provider
            self.current_llm_model = llm_model
        else:
            debug_print("LLM wrapper unchanged")

        return should_update

    def process_request_sync_final_only(self, user_input: str, context: str, **kwargs) -> str:
        """
        Process the request synchronously and return only the final response as a string.

        :param user_input: The user's input query
        :param context: The context for the query
        :param kwargs: Additional keyword arguments
        :return: The final response as a string
        """
        debug_print(
            f"{self.__class__.__name__} processing request synchronously (final only). User input: {user_input}")

        final_response = None
        for response in self.process_request(user_input, context, **kwargs):
            debug_print(f"Response: {response}")
            if response["type"] == "final":
                final_response = response["content"]

        if final_response is None:
            raise ValueError("No final response was generated")

        return final_response

    def process_request(self, user_input: str, context: str, **kwargs) -> Generator[Dict[str, Any], None, None]:
        debug_print(f"{self.__class__.__name__} processing request. User input: {user_input}")
        debug_print(f"Context: {context}")
        debug_print(f"Additional kwargs: {kwargs}")

        thread_id = kwargs.pop('thread_id', '1')
        llm_provider = kwargs.pop('llm_provider', None)
        llm_model = kwargs.pop('llm_model', None)

        self.lazy_init_langchain(llm_provider, llm_model)

        input_message = f"Context: {context}\n\nthread_id: {thread_id}\n\nUser query: {user_input}"
        config = self.getGraphConfig(thread_id)

        last_event = None
        event_count = 0
        try:
            debug_print("Starting graph stream")
            for event in self.graph.stream({"messages": [("user", input_message)]}, config):
                event_count += 1
                debug_print(f"Event {event_count}: {event}")

                if last_event is not None:
                    yield from self.process_and_emit_content(last_event, "intermediate", thread_id)

                last_event = event

            debug_print(f"Graph stream completed. Total events: {event_count}")

            if last_event is not None:
                yield from self.process_and_emit_content(last_event, "final", thread_id)
            elif event_count == 0:
                debug_print("No events were emitted by the graph")
                yield {"type": "error", "content": "No response generated (no events emitted)"}
            else:
                debug_print("No final event was emitted")
                yield {"type": "error", "content": "No final response generated"}

        except Exception as e:
            self.logger.error(f"Error in process_request: {str(e)}", exc_info=True)
            yield {"type": "error", "content": f"An error occurred: {str(e)}"}

    def process_and_emit_content(self, event: Dict[str, Any], step_type: str, thread_id: str) -> Generator[
        Dict[str, Any], None, None]:
        for key, value in event.items():
            if isinstance(value.get("messages", [])[-1], BaseMessage):
                content = value["messages"][-1].content
                if content is not None and content != "":
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
                "default": self.default_llm_provider
            },
            "llm_model": {
                "type": "string",
                "description": "The specific LLM model to use",
                "default": self.default_llm_model
            },
            "thread_id": {
                "type": "string",
                "description": "The thread ID for conversation continuity",
                "default": "1"
            }
        }