from typing import List, TypedDict, Annotated
from mylangchain.async_langchain_bot_interface import AsyncLangchainBotInterface
from utils.debug_utils import debug_print
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage
from toolkits.playwright_toolkit import PlaywrightBrowserToolkit
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from langchain_core.messages import AIMessage

class State(TypedDict):
    messages: Annotated[List, add_messages]

class WebScrapingBot(AsyncLangchainBotInterface):
    def __init__(self):
        super().__init__()
        self.tools = None
        self.async_browser = True
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "web-scraping-bot"

    @property
    def description(self) -> str:
        return "Web Scraping Bot - Expert in web scraping using Playwright"

    async def _async_lazy_init(self):
        if self.tools is None:
            await self.initialize_tools()

    async def initialize_tools(self):
        if self.async_browser:
            debug_print("*** Creating asynchronous browser")
            browser = await async_playwright().start()
            async_browser = await browser.chromium.launch()
            self.tools = PlaywrightBrowserToolkit.from_browser(async_browser=async_browser).get_tools()
        else:
            debug_print("*** Creating synchronous browser")
            browser = sync_playwright().start()
            sync_browser = browser.chromium.launch()
            self.tools = PlaywrightBrowserToolkit.from_browser(sync_browser=sync_browser).get_tools()

    def get_tools(self) -> List:
        if self.tools is None:
            raise ValueError("Tools have not been initialized")
        return self.tools

    def create_chatbot(self):
        async def chatbot(state: State):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content="You are an expert web scraping AI assistant using Playwright browser tools.")

            prompt = """
            As an AI assistant specializing in web scraping with Playwright, please follow these guidelines:
            1. Use the Playwright browser tools to interact with web pages and extract information
            2. Break down complex scraping tasks into manageable steps
            3. Provide clear and specific instructions for each step of the scraping process
            4. Handle potential errors or edge cases in web scraping scenarios
            5. Respect website terms of service and ethical scraping practices
            6. If a task cannot be completed with the available tools, explain why and suggest alternatives
            7. Always provide the extracted information in a structured and easy-to-read format
            """

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages
            ai_message = await self.llm_wrapper.llm.ainvoke(messages)
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