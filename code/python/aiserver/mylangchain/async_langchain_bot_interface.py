import json
import asyncio
from typing import List, Dict, Any, Generator, Optional, AsyncGenerator
from bots.async_bot_interface import AsyncBotInterface
from utils.debug_utils import debug_print
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage, ToolMessage
from langchain_core.runnables.config import RunnableConfig
from mylangchain.langchain_bot_interface import LangchainBotInterface
from processors.persist_files_in_response import persist_files_in_response
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver


class AsyncLangchainBotInterface(LangchainBotInterface, AsyncBotInterface):

    # An opportunity to perform any asynchronous initialization
    # self.llm will already be populated with the correct LLM
    async def _async_lazy_init(self):
        pass

    async def lazy_init_langchain_async(self, llm_provider=None, llm_model=None):
        llm_changed = self._update_llm_wrapper(llm_provider, llm_model)
        await self._async_lazy_init()
        if not self.is_initialized or llm_changed:
            self.lazy_init_retriever()
            self.graph = self.create_graph()
            self.is_initialized = True

    def get_checkpointer(self, checkpointer_type: str = "sqlite", **kwargs):
        if self.checkpointer is None:
            self.checkpointer = AsyncSqliteSaver.from_conn_string(":memory:")
        return self.checkpointer

    async def process_request_async(self, user_input: str, context: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        debug_print(f"{self.__class__.__name__} processing request asynchronously. User input: {user_input}")
        debug_print(f"Context: {context}")
        debug_print(f"Additional kwargs: {kwargs}")

        thread_id = kwargs.pop('thread_id', '1')
        llm_provider = kwargs.pop('llm_provider', None)
        llm_model = kwargs.pop('llm_model', None)

        await self.lazy_init_langchain_async(llm_provider, llm_model)

        input_message = f"Context: {context}\n\nthread_id: {thread_id}\n\nUser query: {user_input}"
        config = self.getGraphConfig(thread_id)

        last_event = None
        event_count = 0
        try:
            debug_print("Starting graph stream")
            async for event in self.graph.astream({"messages": [("user", input_message)]}, config):
                event_count += 1
                debug_print(f"Event {event_count}: {event}")

                if last_event is not None:
                    async for response in self.process_and_emit_content_async(last_event, "intermediate", thread_id):
                        yield response

                last_event = event
                await asyncio.sleep(0)  # Allow other tasks to run

            debug_print(f"Graph stream completed. Total events: {event_count}")

            if last_event is not None:
                async for response in self.process_and_emit_content_async(last_event, "final", thread_id):
                    yield response
            elif event_count == 0:
                debug_print("No events were emitted by the graph")
                yield {"type": "error", "content": "No response generated (no events emitted)"}
            else:
                debug_print("No final event was emitted")
                yield {"type": "error", "content": "No final response generated"}

        except Exception as e:
            self.logger.error(f"Error in process_request_async: {str(e)}", exc_info=True)
            yield {"type": "error", "content": f"An error occurred: {str(e)}"}

    async def process_request_async_final_only(self, user_input: str, context: str, **kwargs) -> str:
        debug_print(
            f"{self.__class__.__name__} processing request asynchronously (final only). User input: {user_input}")

        final_response = None
        async for response in self.process_request_async(user_input, context, **kwargs):
            debug_print(f"Response: {response}")
            if response["type"] == "final":
                final_response = response["content"]

        if final_response is None:
            raise ValueError("No final response was generated")

        return final_response

    async def process_and_emit_content_async(self, event: Dict[str, Any], step_type: str, thread_id: str) -> \
    AsyncGenerator[
        Dict[str, Any], None]:
        for key, value in event.items():
            debug_print(f"Processing event key: {key}")
            debug_print(f"Event value: {value}")
            if value.get("messages") is None:
                debug_print("No messages found in event value")
                continue

            messages = value.get("messages", [])
            debug_print(f"Messages: {messages}")
            if isinstance(value.get("messages", [])[-1], BaseMessage):
                content = value["messages"][-1].content
                if content is not None and content != "":
                    if isinstance(content, str):
                        async for response in self.process_content_async(content, step_type, thread_id):
                            yield response
                    elif asyncio.iscoroutine(content):
                        resolved_content = await content
                        async for response in self.process_content_async(resolved_content, step_type, thread_id):
                            yield response
                    else:
                        async for response in self.process_content_async(json.dumps(content), step_type, thread_id):
                            yield response

    async def process_content_async(self, content: str, step_type: str, thread_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        print(f"Processing content asynchronously (step_type: {step_type}):")
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

        last_processed_content = None
        for item in items:
            processed_item = process_item(item)
            processed_content = await self.process_response_content_async(processed_item, thread_id)
            last_processed_content = processed_content

            if await self.should_emit_response_async(processed_content, step_type):
                yield {"type": step_type, "content": processed_content}

            await asyncio.sleep(0)  # Allow other tasks to run

        if last_processed_content is not None:
            print(f"Processed content: {last_processed_content[:200]}...")  # Print first 200 characters of the last processed item
        else:
            print("No content was processed.")

    async def process_response_content_async(self, content: str, thread_id: str) -> str:
        """
        Process the response content asynchronously. This method now includes file saving functionality.

        :param content: The original response content
        :param thread_id: The thread ID for the current conversation
        :return: The processed response content
        """
        # Attempt to save any files in the response
        # Note: persist_files_in_response should be made async-compatible if it involves I/O operations
        await asyncio.to_thread(persist_files_in_response, thread_id, content)

        # Perform any additional processing (can be overridden in subclasses)
        return await self.post_process_response_async(content, thread_id=thread_id)

    async def post_process_response_async(self, content: str, **kwargs) -> str:
        """
        Post-process the response content asynchronously. This method can be overridden in subclasses
        to implement custom processing of the response content.

        :param content: The original response content
        :param kwargs: Additional keyword arguments
        :return: The processed response content
        """
        return content  # Default implementation returns the content unchanged

    async def should_emit_response_async(self, content: str, step_type: str) -> bool:
        """
        Determine if a response should be emitted asynchronously.
        Override this method in subclasses to customize response emission behavior.

        :param content: The content to be emitted
        :param step_type: The type of step ('intermediate' or 'final')
        :return: True if the response should be emitted, False otherwise
        """
        debug_print(f"Deciding whether to emit response asynchronously (step_type: {step_type})")
        return True  # Emit all responses by default
