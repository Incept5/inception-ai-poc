import os
from typing import List, TypedDict, Annotated, Optional

from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from mylangchain.async_langchain_bot_interface import AsyncLangchainBotInterface
from playwright.async_api import async_playwright
from toolkits.playwright_toolkit import PlaywrightBrowserToolkit
from utils.debug_utils import debug_print


class State(TypedDict):
    messages: Annotated[List, add_messages]

class WebScrapingDBBot(AsyncLangchainBotInterface):
    def __init__(self, retriever_name: Optional[str] = None, db_url: str = os.environ.get("DB_READER_DB_URI")):
        super().__init__(retriever_name)
        self.db_url = db_url
        self.tools = None
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "webscraping-db-bot"

    @property
    def description(self) -> str:
        return "Web Scraping DB Bot - Expert in web scraping and database updating"

    def get_tools(self) -> List:
        return self.tools

    async def _async_lazy_init(self):
        if self.tools is None:
            await self.initialize_tools()

    async def initialize_tools(self):
        debug_print("*** Creating asynchronous browser")
        browser = await async_playwright().start()
        async_browser = await browser.chromium.launch()
        self.tools = PlaywrightBrowserToolkit.from_browser(async_browser=async_browser).get_tools()

        # Add SQL database tools also
        db = SQLDatabase.from_uri(self.db_url)
        sql_toolkit = SQLDatabaseToolkit(db=db,llm=self.llm)
        self.tools.extend(sql_toolkit.get_tools())

        # Need to bind the tools to the LLM as we missed the prior opportunity
        self.llm = self.llm.bind_tools(self.tools)

        debug_print(f"Bound Tools: {self.tools}")


    def create_chatbot(self):
        async def chatbot(state: State):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content="""
            You are an expert web scraping and database management AI assistant. 
            Use the provided tools to interact with web pages and update databases.
            Do not try to tell me how I can write code. Just use the tools to do the job.
            """)

            prompt = """
            As an AI assistant specializing in web scraping and database management, please follow these guidelines:
            1. Use the Playwright browser tools to interact with web pages and extract information
            2. Analyze the scraped data and determine if it matches any existing database tables
            3. If a matching table exists, update it with the new data
            4. If no matching table exists, create a new table and insert the scraped data
            5. Use SQL commands to interact with the database (create tables, insert data, update records)
            6. When doing inserts keep the SQL simple and avoid ON CONFLICT clauses
            7. Provide clear explanations of your actions and any database changes made
            8. Handle potential errors or edge cases in both web scraping and database operations
            9. Always provide a summary of the scraped data and database updates
            """

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages
            ai_message = await self.llm.ainvoke(messages)
            debug_print(f"Chatbot output ai_message: {ai_message}")
            result = {"messages": [ai_message]}
            debug_print(f"Chatbot output result: {result}")
            return result

        return chatbot

    def create_graph(self) -> StateGraph:
        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", self.create_chatbot())
        tool_node = ToolNode(tools=self.get_tools())
        graph_builder.add_node("tools", tool_node)
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.set_entry_point("chatbot")
        mycheckpointer = self.get_checkpointer()
        return graph_builder.compile(checkpointer=mycheckpointer)
