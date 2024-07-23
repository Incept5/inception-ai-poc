from typing import List
from mylangchain.base_bot import BaseBot
from langchain.tools import Tool
from tools.advanced_company_search_tool import advanced_company_search

class AdvancedCompanySearchBot(BaseBot):
    @property
    def bot_type(self) -> str:
        return "AdvancedCompanySearchBot"

    @property
    def description(self) -> str:
        return "A bot that performs advanced searches for UK company information using the Companies House website, including detailed company overviews, filing history, and people information."

    def get_system_prompt(self) -> str:
        return """You are an advanced AI assistant specialized in searching for detailed UK company information. 
        Your capabilities include:
        1. Searching for companies by name on the Companies House website.
        2. Retrieving detailed company overviews, including registration date, address, and SIC codes.
        3. Fetching recent filing history (up to 5 entries) for each company.
        4. Providing information about key people in the company (up to 5 entries).

        Your task is to use the provided tool to search for company details based on the user's input. 
        After retrieving the information, present it in a clear, concise manner. 
        If multiple companies are found, list them all with their detailed information. If no companies are found, inform the user.
        Always respond with the information in a structured and easy-to-read format."""

    def get_tools(self) -> List[Tool]:
        return [advanced_company_search]

def create_bot(default_llm_provider=None, default_llm_model=None):
    return AdvancedCompanySearchBot(default_llm_provider, default_llm_model)