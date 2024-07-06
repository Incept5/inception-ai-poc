from typing import List, TypedDict, Annotated
from mylangchain.langchain_bot_interface import LangchainBotInterface
from utils.debug_utils import debug_print
from processors.persist_files_in_response import persist_files_in_response
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults

class State(TypedDict):
    messages: Annotated[List, add_messages]

class WebAppBot(LangchainBotInterface):
    def __init__(self):
        super().__init__()
        self.tools = [TavilySearchResults(max_results=3)]
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "web-app-bot"

    @property
    def description(self) -> str:
        return "Web App Bot - Creates single-page web applications using Vue"

    def get_tools(self) -> List:
        return self.tools

    def create_chatbot(self):
        def chatbot(state: State):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content="You are a helpful AI assistant specialized in creating single-page web applications using Vue.")

            prompt = """
            Create a single-page web app using the Vue framework, ensuring it will run without any transpiling in all modern browsers. The app should be functional and responsive, capable of running directly in the browser without additional build steps.

            Provide only the complete code for the web application. Start the code block with three backticks followed by 'html' and a suitable filename, like this:

            ```html example_vue_app.html

            You can use the web search tool to find out information if you need it.

            Remember to include all necessary HTML, CSS, and JavaScript (including Vue.js) within a single file.
            IMPORTANT: only output the html file - do not provide bother describing the code.
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