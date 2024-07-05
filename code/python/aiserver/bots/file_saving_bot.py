# bots/file_saving_bot.py

from typing import List, TypedDict, Annotated
from mylangchain.langchain_bot_interface import LangchainBotInterface
from processors.persist_files_in_response import persist_files_in_response
from utils.debug_utils import debug_print
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage

class State(TypedDict):
    messages: Annotated[List, add_messages]

class FileSavingBot(LangchainBotInterface):
    def __init__(self):
        super().__init__()
        self.tools = []  # FileSavingBot doesn't use any tools
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "file-saving-bot"

    @property
    def description(self) -> str:
        return "File Saving Bot - Conversation with ability to save generated files"

    def get_tools(self) -> List:
        return self.tools

    def create_chatbot(self):
        def chatbot(state: State):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content="You are a helpful AI assistant")

            prompt = """
            As an AI assistant, please provide a helpful and informative response to the user's query.
            Follow these guidelines:
            1. Be clear and specific in your answer
            2. If you're unsure about something, it's okay to admit it
            3. Break down complex information into manageable steps
            4. Use examples where appropriate
            5. Cite sources or provide reasoning for your answers when possible
            6. When generating files or artifacts, use blocks which start with 3 backticks, 
               followed by the file type, then the name (with path) after the file type plus a space. 
               Always do this when generating files and make up a path/name if you have to. 
               When making edits to previously referenced files, always keep the name/path the same.

            Example:
            ```python /path/to/example.py
            print("Hello, World!")
            ```
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
        graph_builder.set_entry_point("chatbot")
        mycheckpointer = self.get_checkpointer()
        return graph_builder.compile(checkpointer=mycheckpointer)

    def post_process_response(self, response: str, **kwargs) -> str:
        thread_id = kwargs.get('thread_id', '1')
        # Process files in the response without modifying it
        persist_files_in_response(thread_id, response)
        # Return the original response unchanged
        return response