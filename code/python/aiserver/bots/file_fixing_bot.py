from typing import List, TypedDict, Annotated, Optional, Dict, Any
from mylangchain.langchain_bot_interface import LangchainBotInterface
from utils.debug_utils import debug_print
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage

class State(TypedDict):
    messages: Annotated[List, add_messages]

class FileFixingBot(LangchainBotInterface):
    def __init__(self, retriever_name: Optional[str] = None):
        super().__init__(retriever_name)
        self.tools = []  # FileFixingBot doesn't use any tools
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "file-fixing-bot"

    @property
    def description(self) -> str:
        return "File Fixing Bot - Compares and merges file content using LLM"

    def get_tools(self) -> List:
        return self.tools

    def create_chatbot(self):
        def chatbot(state: State):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content="You are a helpful AI assistant")

            prompt = """
            You are an AI assistant that processes and merges file contents. 
            You will receive two versions of file content: the original and the new version, separated by markers. 
            Your task is to apply the diff to the original file content and return the result without any markers in. 
            Once you have the new file content please double check it is valid for the type of file you are processing. 
            IMPORTANT: Only return the new merged file content and nothing else.
            """

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages

            answer = self.llm_wrapper.invoke(messages).content

            result = {"messages": [HumanMessage(content=answer)]}
            debug_print(f"File Fixing Bot output: {result}")
            return result

        return chatbot

    def create_graph(self) -> StateGraph:
        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", self.create_chatbot())
        graph_builder.set_entry_point("chatbot")
        mycheckpointer = self.get_checkpointer()
        return graph_builder.compile(checkpointer=mycheckpointer)