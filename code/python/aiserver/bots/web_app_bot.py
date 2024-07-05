from typing import List, TypedDict, Annotated
from mylangchain.langchain_bot_interface import LangchainBotInterface
from processors.persist_files_in_response import persist_files_in_response
from utils.debug_utils import debug_print
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
        return "Web App Bot - Creates single HTML file web applications"

    def get_tools(self) -> List:
        return self.tools

    def create_chatbot(self):
        def chatbot(state: State):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content="You are a helpful AI assistant specialized in creating single HTML file web applications")

            prompt = """
            As an AI assistant specialized in creating single HTML file web applications, please provide a helpful and informative response to the user's query.
            Follow these guidelines:
            1. Create complete, self-contained HTML files that include CSS and JavaScript within the HTML file
            2. Use modern HTML5, CSS3, and ES6+ JavaScript features
            3. Ensure the web app is responsive and works well on different screen sizes
            4. Implement user-friendly interfaces and intuitive interactions
            5. When appropriate, use CSS Flexbox or Grid for layouts
            6. Include comments in the code to explain complex parts or functionality
            7. You can use the web search tool to look up information, libraries or examples if needed
            8. When generating the web app, use a block which starts with 3 backticks, 
               followed by 'html', then the name (with path) after 'html' plus a space. 
               Always do this when generating the web app and make up a path/name if you have to. 
               When making edits to previously referenced files, always keep the name/path the same.

            Example:
            ```html web_apps/todo_app.html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Todo App</title>
                <style>
                    /* CSS styles here */
                </style>
            </head>
            <body>
                <!-- HTML content here -->
                <script>
                    // JavaScript code here
                </script>
            </body>
            </html>
            ```
            """

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages
            result = {"messages": [self.llm_wrapper.invoke(messages)]}
            debug_print(f"Chatbot output: {result}")
            return result

        return chatbot  # Return the chatbot function

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