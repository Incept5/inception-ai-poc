import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from mylangchain.base_bot import BaseBot
from langchain.tools import Tool

class CompanySearchBot(BaseBot):
    @property
    def bot_type(self) -> str:
        return "CompanySearchBot"

    @property
    def description(self) -> str:
        return "A bot that searches for UK company information using the Companies House website."

    def get_system_prompt(self) -> str:
        return """You are a helpful AI assistant specialized in searching for UK company information. 
        Your task is to use the provided tool to search for company details based on the user's input. 
        After retrieving the information, present it in a clear, concise JSON format. 
        If multiple companies are found, list them all. If no companies are found, inform the user.
        Always respond with valid JSON, even if it's an error message."""

    def get_tools(self) -> List[Tool]:
        return [
            Tool(
                name="search_company",
                func=self.search_company,
                description="Searches for UK company information given a company name."
            )
        ]

    def search_company(self, company_name: str) -> str:
        search_page_url = "https://find-and-update.company-information.service.gov.uk/advanced-search"
        session = requests.Session()

        response = session.get(search_page_url)
        if response.status_code != 200:
            return self._format_json_response({"error": f"Error: Received status code {response.status_code} when fetching search page"})

        search_data = {
            'companyNameIncludes': company_name,
        }

        search_url = "https://find-and-update.company-information.service.gov.uk/advanced-search/get-results"
        response = session.get(search_url, params=search_data)
        if response.status_code != 200:
            return self._format_json_response({"error": f"Error: Received status code {response.status_code} when submitting search"})

        soup = BeautifulSoup(response.text, 'html.parser')
        company_links = soup.find_all('a', href=lambda href: href and '/company/' in href)

        companies = []
        for link in company_links:
            company_url = f"https://find-and-update.company-information.service.gov.uk{link['href']}"
            company_info = self._get_company_info(session, company_url)
            if company_info:
                companies.append(company_info)

        if companies:
            return self._format_json_response({"companies": companies})
        else:
            return self._format_json_response({"message": "No companies found matching the search criteria."})

    def _get_company_info(self, session: requests.Session, url: str) -> Dict[str, str]:
        response = session.get(url)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        company_name = soup.find('h1', class_='heading-xlarge')
        company_name = company_name.text.strip() if company_name else "N/A"

        status_element = soup.find(string=lambda text: text and ('Active' in text or 'Dissolved' in text))
        status = status_element.strip() if status_element else "N/A"

        company_type = "N/A"
        incorporation_date = "N/A"

        dt_elements = soup.find_all('dt')
        for dt in dt_elements:
            if 'Company type' in dt.text:
                dd = dt.find_next_sibling('dd')
                if dd:
                    company_type = dd.text.strip()
            elif 'Incorporated on' in dt.text:
                dd = dt.find_next_sibling('dd')
                if dd:
                    incorporation_date = dd.text.strip()

        return {
            "name": company_name,
            "status": status,
            "type": company_type,
            "incorporation_date": incorporation_date
        }

    def _format_json_response(self, data: Dict[str, Any]) -> str:
        import json
        return json.dumps(data, indent=2)

def create_bot(default_llm_provider=None, default_llm_model=None):
    return CompanySearchBot(default_llm_provider, default_llm_model)