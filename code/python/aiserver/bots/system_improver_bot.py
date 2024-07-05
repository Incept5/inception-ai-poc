# bots/system_improver_bot.py

import os
from typing import List, TypedDict, Annotated
from mylangchain.langchain_bot_interface import LangchainBotInterface
from processors.persist_files_in_response import persist_files_in_response
from utils.debug_utils import debug_print
from utils.file_tree import file_tree
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.tools import tool

class State(TypedDict):
    messages: Annotated[List, add_messages]

@tool
def file_content(file_path: str) -> str:
    """Get the content of a file from the /system_src directory."""
    full_path = os.path.join('/system_src', file_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        with open(full_path, 'r') as file:
            return file.read()
    return f"Error: File {file_path} not found or is not a file."

class SystemImproverBot(LangchainBotInterface):
    def __init__(self):
        super().__init__()
        self.tools = [file_content]
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "system-improver-bot"

    @property
    def description(self) -> str:
        return "System Improver Bot - Answer questions about the system"

    def get_tools(self) -> List:
        return self.tools

    def create_chatbot(self):
        def chatbot(state: State):
            file_structure = file_tree('/system_src')
            debug_print(f"File structure: {file_structure}")

            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content="You are an AI assistant tasked with helping improve a software system.")

            prompt = f"""
            As an AI assistant, you are tasked with analyzing and suggesting improvements for a software system.
            Follow these guidelines:
            1. Review the system structure tree below and answer questions about the system and suggest improvements where appropriate
            2. Use the file_content tool to retrieve the contents of specific files when needed rather than guessing at what they contain
            3. When generating files or artifacts, use blocks which start with 3 backticks, 
               followed by the file type, then the name (with path) after the file type plus a space. 
               Always do this when generating files and make up a path/name if you have to. 
               When making edits to previously referenced files, always keep the name/path the same.
            4. When choosing a file path for generated artefacts consider the system structure and choose a logical location.
            5. When I mention a specific file name then look for it in the system structure below and use the file_content tool to get the content of that file.

            Example:
            ```python code/python/aiserver/utils/example.py
            print("Hello, World!")
            ```
            
            Example of generating a snippet that doesn't have an obvious home in the system:
            ```python snippets/my_data_loader.py
            def my_data_loader(file_path: str) -> dict:
                return {{"data": "example"}}
            ```

            The system structure is as follows:
            {file_structure}

            IMPORTANT: Remember to ask for specific file contents using the file_content tool when needed.
            IMPORTANT: always add both a type and a file path after the 3 backticks when generating files or snippets.
            """

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages
            result = {"messages": [self.llm_wrapper.invoke(messages)]}
            debug_print(f"Chatbot output: {result}")
            return result

        return chatbot

    def create_graph(self) -> StateGraph:
        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", self.create_chatbot())
        tool_node = ToolNode(tools=self.tools)
        graph_builder.add_node("tools", tool_node)
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.set_entry_point("chatbot")
        mycheckpointer = self.get_checkpointer()
        return graph_builder.compile(checkpointer=mycheckpointer)

    def post_process_response(self, response: str, **kwargs) -> str:
        thread_id = kwargs.get('thread_id', '1')
        # Process files in the response without modifying it
        persist_files_in_response(thread_id, response)
        # Return the original response unchanged
        return response