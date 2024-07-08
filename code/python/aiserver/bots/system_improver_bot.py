import os
from typing import List, TypedDict, Annotated, Dict, Any
from mylangchain.langchain_bot_interface import LangchainBotInterface
from processors.persist_files_in_response import persist_files_in_response
from utils.debug_utils import debug_print
from utils.file_tree import file_tree
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.tools import tool
from prompts.system_prompts import file_saving_prompt


class State(TypedDict):
    messages: Annotated[List, add_messages]


@tool
def file_content(file_path: str) -> str:
    """Get the content of a file, handling paths that may or may not start with /system_src."""
    if file_path.startswith('/system_src'):
        full_path = file_path
    else:
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
            system_message = SystemMessage(content=file_saving_prompt())

            # Check for hints.md file
            hints_content = file_content("/system_src/hints.md")
            hints_section = ""
            if not hints_content.startswith("Error:"):
                hints_section = f"""
                Here are some hints about the system:
                {hints_content}
                """

            prompt = f"""
            As an AI assistant, you are tasked with analyzing and suggesting improvements for a software system.
            Follow these guidelines:
            1. Review the system structure tree below and answer questions about the system and suggest improvements where appropriate
            2. Use the file_content tool to retrieve the contents of specific files when needed rather than guessing at what they contain
               When making edits to previously referenced files, always keep the name/path the same.
            3. When choosing a file path for generated artefacts consider the system structure and choose a logical location.
            4. When I mention a specific file name then look for it in the system structure below and use the file_content tool to get the content of that file.

            The system structure is as follows:
            {file_structure}

            {hints_section}

            IMPORTANT: Remember to ask for specific file contents using the file_content tool when needed.
            VERY IMPORTANT: Always generate FULL source code files rather than diffs or partial code snippets.
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