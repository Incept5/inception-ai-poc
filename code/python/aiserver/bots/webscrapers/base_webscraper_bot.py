
from mylangchain.base_bot import BaseBot
from typing import List

from toolkits.playwright_toolkit import PlaywrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser

class BaseWebScraperBot(BaseBot):
    def __init__(self, default_llm_provider=None, default_llm_model=None):
        super().__init__(default_llm_provider, default_llm_model)

    @property
    def bot_type(self) -> str:
        return "BaseWebScraperBot"

    @property
    def description(self) -> str:
        return "A base web scraping bot that uses Playwright for browser automation."

    def get_system_prompt(self) -> str:
        return """You are a web scraping assistant that uses Playwright tools to navigate and interact with web pages. 
        Your task is to follow the instructions provided to scrape websites and extract information. 
        Use the available tools to navigate, click, fill forms, and extract data from web pages. 
        Always provide clear and concise summaries of the information you find."""

    def get_tools(self) -> List:
        browser = create_async_playwright_browser()
        toolkit = PlaywrightBrowserToolkit.from_browser(async_browser=browser)
        return toolkit.get_tools()

# This allows the bot to be easily imported and instantiated
def create_bot(default_llm_provider=None, default_llm_model=None):
    return BaseWebScraperBot(default_llm_provider, default_llm_model)