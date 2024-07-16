from typing import List, TypedDict, Annotated, Optional
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
            system_message = SystemMessage(content="""You are an AI assistant that processes and merges file contents. 
            You will receive two versions of file content: the original and the new version, separated by markers.
            Your task is to analyze and process these versions according to the following rules:

            1. If the new file content looks like a complete file, return it as is.
            2. If the new file content appears to be a partial file or contains diff-like markers, merge it with the original content.
            3. For partial files, look for indicators such as:
               - "# ... (existing method, unchanged)"
               - "// ... ("
               - "[... existing content ...]"
               - "[... anything ...]"
            4. When merging, replace the corresponding sections in the original file with the new content.
            5. Ensure that the final output is a complete, valid file.

            Only return the processed file contents with no other information or explanations.""")

            prompt = """Please process the following file contents and provide the resulting merged or new file content:

            <-- Original File Start -->
            {original_content}
            <-- Separator -->
            {new_content}
            <-- New File End -->

            Remember to only return the processed file contents with no other information."""

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages

            processed_content = self.llm_wrapper.invoke(messages).content

            result = {"messages": [HumanMessage(content=processed_content)]}
            debug_print(f"Chatbot output: {result}")
            return result

        return chatbot

    def create_graph(self) -> StateGraph:
        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", self.create_chatbot())
        graph_builder.set_entry_point("chatbot")
        mycheckpointer = self.get_checkpointer()
        return graph_builder.compile(checkpointer=mycheckpointer)