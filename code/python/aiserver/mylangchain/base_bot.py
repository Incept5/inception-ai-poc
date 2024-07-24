from abc import ABC, abstractmethod
from typing import List, Dict, TypedDict, Any, Optional, Annotated
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from llms.llm_manager import LLMManager
from utils.debug_utils import debug_print
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from bots.simple_bot_interface import SimpleBotInterface
import traceback
import sys

class DefaultState(TypedDict):
    messages: Annotated[List, add_messages]

class BaseBot(SimpleBotInterface, ABC):
    def __init__(self, default_llm_provider: Optional[str] = None, default_llm_model: Optional[str] = None):
        self.default_llm_provider = default_llm_provider
        self.default_llm_model = default_llm_model

    @property
    @abstractmethod
    def bot_type(self) -> str:
        """Return the type of the bot."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a short description of the bot."""
        pass

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
            }
        }

    # Default Graph should be okay in most cases
    def create_graph(self, tools: List, llm_wrapper: Any) -> StateGraph:
        graph_builder = StateGraph(DefaultState)
        graph_builder.add_node("bot", self.create_bot(llm_wrapper))
        tool_node = ToolNode(tools=tools)
        graph_builder.add_node("tools", tool_node)
        graph_builder.add_conditional_edges("bot", tools_condition)
        graph_builder.add_edge("tools", "bot")
        graph_builder.set_entry_point("bot")
        return graph_builder.compile()

    # Default bot should be okay in most cases
    def create_bot(self, llm_wrapper: Any):
        def bot(state: DefaultState):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content=self.get_system_prompt())
            messages = [system_message] + messages
            result = {"messages": [llm_wrapper.invoke(messages)]}
            debug_print(f"Chatbot output: {result}")
            return result

        return bot

    # No tools is the default but just define them here
    def get_tools(self) -> List:
        return []

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Return the system prompt for this query.
        This method should be implemented by child classes.
        """
        pass

    def _get_llm_wrapper(self, tools: List, llm_provider: Optional[str], llm_model: Optional[str]) -> Any:
        debug_print(f"Getting LLM wrapper. Provider: {llm_provider}, Model: {llm_model}")

        if llm_provider and llm_model:
            return LLMManager.get_llm(tools, llm_provider, llm_model)
        elif self.default_llm_provider and self.default_llm_model:
            debug_print("Using default LLM wrapper")
            return LLMManager.get_llm(tools, self.default_llm_provider, self.default_llm_model)
        else:
            debug_print("Using system default LLM wrapper")
            return LLMManager.get_default_llm(tools)

    def simple_process_request(self, user_input: str, context: str, **kwargs) -> str:
        """
        Process a user request and return a response.

        :param user_input: The user's input message
        :param context: Additional context for the conversation
        :param kwargs: Additional keyword arguments that might be needed for specific bot implementations
        :return: The bot's response
        """
        debug_print(f"{self.__class__.__name__} processing query. User input: {user_input}")
        debug_print(f"Context: {context}")
        debug_print(f"Additional kwargs: {kwargs}")

        llm_provider = kwargs.pop('llm_provider', None)
        llm_model = kwargs.pop('llm_model', None)

        tools = self.get_tools()
        llm_wrapper = self._get_llm_wrapper(tools, llm_provider, llm_model)
        graph = self.create_graph(tools, llm_wrapper)

        try:
            debug_print("Starting graph execution")
            result = graph.invoke({"messages": [("user", user_input)]})
            debug_print(f"Graph execution completed. Result: {result}")

            final_response = self.extract_final_response(result)
            processed_response = self.process_response(final_response)
            return processed_response

        except Exception as e:
            error_message = f"Error in simple_process_request: {str(e)}"
            debug_print(error_message)
            print(error_message, file=sys.stderr)
            print("Traceback:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return f"An error occurred: {str(e)}"

    def extract_final_response(self, result: Dict[str, Any]) -> str:
        """
        Extract the final response from the graph execution result.
        This method handles both dictionary and list result types.

        :param result: The result from graph execution (Dict[str, Any])
        :return: The extracted final response as a string
        """
        debug_print("Extracting final response")
        debug_print(f"Result type: {type(result)}")

        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, dict) and "messages" in value:
                    messages = value["messages"]
                elif isinstance(value, list):
                    messages = value
                else:
                    continue

                if messages and isinstance(messages[-1], BaseMessage):
                    content = messages[-1].content
                    if content:
                        debug_print(f"Extracted content: {content[:200]}...")  # Print first 200 characters
                        return content

        elif isinstance(result, list):
            if result and isinstance(result[-1], BaseMessage):
                content = result[-1].content
                if content:
                    debug_print(f"Extracted content: {content[:200]}...")  # Print first 200 characters
                    return content

        debug_print("No valid response found in the result")
        return "No valid response was generated."

    def process_response(self, response: str) -> str:
        """
        Process the final response. This method can be overridden in child classes
        to implement custom processing of the response.

        :param response: The original response content
        :return: The processed response content
        """
        debug_print("Processing response")
        debug_print(f"Original response: {response[:200]}...")  # Print first 200 characters
        return response  # Default implementation returns the response unchanged