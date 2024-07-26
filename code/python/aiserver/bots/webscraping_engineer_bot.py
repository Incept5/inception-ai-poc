from typing import List, TypedDict, Annotated
from utils.debug_utils import debug_print
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from toolkits.playwright_toolkit import PlaywrightBrowserToolkit
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from .base_system_improver_bot import BaseSystemImproverBot
from tools.file_content_tool import file_content
from tools.file_tree_tool import file_tree_tool

class State(TypedDict):
    messages: Annotated[List, add_messages]
    phase: str
    scraped_data: dict

class WebScrapingEngineerBot(BaseSystemImproverBot):
    def __init__(self):
        super().__init__(system_src='/system_src')
        self.tools = None
        self.async_browser = True
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "webscraping-engineer-bot"

    @property
    def description(self) -> str:
        return "Web Scraping Engineer Bot - Expert in web scraping and improving web scraping systems"

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

        # Add file_content_tool and file_tree_tool
        self.tools.extend([file_content, file_tree_tool])

        # Need to bind the tools to the LLM as we missed the prior opportunity
        self.llm = self.llm.bind_tools(self.tools)

        debug_print(f"Bound Tools: {self.tools}")

    def get_tools(self) -> List:
        return self.tools

    def create_chatbot(self):
        async def chatbot(state: State):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            phase = state.get("phase", "scraping")
            scraped_data = state.get("scraped_data", {})

            system_message = SystemMessage(content="""
            You are an expert web scraping AI assistant and system improver. 
            You work in two phases: 
            1. Web Scraping: Use the provided Playwright tools to interact with web pages and extract information.
            2. System Improvement: Once data is scraped, use it to build or update a webscraper in the system.
            Follow the current phase instructions carefully.
            """)

            if phase == "scraping":
                prompt = """
                Phase 1: Web Scraping
                1. Use the Playwright browser tools to interact with web pages and extract information
                2. Break down complex scraping tasks into manageable steps
                3. Provide clear and specific instructions for each step of the scraping process
                4. Handle potential errors or edge cases in web scraping scenarios
                5. If a task cannot be completed with the available tools, explain why and suggest alternatives
                6. Always provide the extracted information in a structured and easy-to-read format
                7. Once scraping is complete, return the scraped data and set the phase to "improving"
                """
            else:  # phase == "improving"
                prompt = """
                Phase 2: System Improvement
                1. Use the file_tree_tool to get an overview of the system structure
                2. Look for and fetch the content of any "hints.md" file using the file_content tool
                3. Review the scraped data and the route/process we used to scrape it
                4. Optimise the steps we took to scrape the data so the new system is more efficient
                5. Analyze the current system's web scraping capabilities
                6. Determine if a new webscraper should be added or an existing one updated
                7. Use the file_content tool to fetch example code for reference
                8. Write or update the webscraper code in the appropriate language and style
                9. Ensure the new or updated code integrates well with the existing system
                10. Provide clear documentation in the code for the changes made
                11. If no improvements are needed, explain why
                """

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages
            ai_message = await self.llm.ainvoke(messages)
            debug_print(f"Chatbot output ai_message: {ai_message}")

            # Check if we need to transition from scraping to improving phase
            if phase == "scraping" and "scraped data" in ai_message.content.lower():
                # Extract scraped data from the message (this is a simplified example)
                scraped_data = {"data": ai_message.content}
                phase = "improving"

            result = {
                "messages": [ai_message],
                "phase": phase,
                "scraped_data": scraped_data
            }
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
