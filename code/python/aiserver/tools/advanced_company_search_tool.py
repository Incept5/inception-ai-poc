import json
import logging
from typing import Dict, Any, Optional
from langchain.tools import tool
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Set up logger
logger = logging.getLogger(__name__)

def _get_detailed_company_info(page, url: str) -> Dict[str, Any]:
    logger.debug(f"Fetching detailed company info from URL: {url}")
    try:
        page.goto(url)
        page.wait_for_load_state('networkidle')

        # Extract basic company information
        company_info = {
            "name": page.text_content('h1.heading-xlarge'),
            "company_number": page.text_content('p.heading-secondary'),
            "status": page.text_content('dd.company-status'),
        }
        logger.debug(f"Basic company info: {company_info}")

        # Extract company overview
        overview = {}
        overview_items = page.query_selector_all('#company-overview dt, #company-overview dd')
        for i in range(0, len(overview_items), 2):
            key = overview_items[i].text_content().strip().lower().replace(' ', '_')
            value = overview_items[i + 1].text_content().strip() if i + 1 < len(overview_items) else "N/A"
            overview[key] = value
        company_info['overview'] = overview
        logger.debug(f"Company overview: {overview}")

        # Extract filing history
        logger.debug("Extracting filing history")
        page.click('a[href$="/filing-history"]')
        page.wait_for_load_state('networkidle')
        filing_history = page.eval_on_selector_all('table.full-width-table tbody tr', """
            (rows) => rows.slice(0, 5).map(row => ({
                date: row.querySelector('td:nth-child(1)').textContent.trim(),
                description: row.querySelector('td:nth-child(2)').textContent.trim(),
            }))
        """)
        company_info['filing_history'] = filing_history
        logger.debug(f"Filing history: {filing_history}")

        # Extract people information
        logger.debug("Extracting people information")
        page.click('a[href$="/officers"]')
        page.wait_for_load_state('networkidle')
        people = page.eval_on_selector_all('.appointment-1', """
            (appointments) => appointments.slice(0, 5).map(app => ({
                name: app.querySelector('h2').textContent.trim(),
                role: app.querySelector('dd.appointment-content').textContent.trim(),
            }))
        """)
        company_info['people'] = people
        logger.debug(f"People information: {people}")

        return company_info
    except PlaywrightTimeoutError:
        logger.error("Timeout occurred while fetching detailed company information.")
        return {"error": "Timeout occurred while fetching detailed company information."}
    except Exception as e:
        logger.error(f"An error occurred while fetching detailed company information: {str(e)}")
        return {"error": f"An error occurred while fetching detailed company information: {str(e)}"}


def _format_json_response(data: Dict[str, Any]) -> str:
    return json.dumps(data, indent=2)


@tool("advanced_company_search")
def advanced_company_search(company_name: Optional[str] = None) -> str:
    """
    Performs an advanced search for UK company information, including detailed overviews, filing history, and people information.
    """
    logger.info(f"Starting advanced company search for: {company_name}")
    if company_name is None:
        logger.warning("Company name is required but was not provided.")
        return _format_json_response({"error": "Company name is required."})

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            # Navigate to the search page
            logger.debug("Navigating to the search page")
            page.goto("https://find-and-update.company-information.service.gov.uk/advanced-search")

            # Fill in the search form
            logger.debug(f"Filling in search form with company name: {company_name}")
            page.fill('input[name="companyNameIncludes"]', company_name)

            logger.debug("Clicking the search button")
            page.click('button[id="advanced-search-button"]')

            # Wait for the results to load
            logger.debug("Waiting for search results")
            page.wait_for_selector('.results-list', timeout=10000)

            # Extract company links
            logger.debug("Extracting company links from search results")
            company_links = page.eval_on_selector_all('.results-list a[href^="/company/"]', """
                (elements) => elements.map(el => ({
                    name: el.textContent.trim(),
                    url: el.href
                }))
            """)
            logger.debug(f"Found {len(company_links)} company links")

            companies = []
            for link in company_links:
                logger.info(f"Fetching detailed information for company: {link['name']}")
                company_info = _get_detailed_company_info(page, link['url'])
                if company_info:
                    companies.append(company_info)

            if companies:
                logger.info(f"Successfully retrieved information for {len(companies)} companies")
                return _format_json_response({"companies": companies})
            else:
                logger.warning("No companies found matching the search criteria.")
                return _format_json_response({"message": "No companies found matching the search criteria."})

        except PlaywrightTimeoutError:
            logger.error("Timeout occurred while searching for companies.")
            return _format_json_response(
                {"error": "Timeout occurred while searching for companies. Please try again later."})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return _format_json_response({"error": f"An error occurred: {str(e)}"})
        finally:
            browser.close()

# Add the main method to test the advanced company search tool
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    test_company_name = "Incept5 Limited"
    print(f"Testing advanced company search for: {test_company_name}")
    result = advanced_company_search(test_company_name)
    print(result)