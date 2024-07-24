import requests
from bs4 import BeautifulSoup
import json

def search_company(company_name):
    print(f"Searching for company: {company_name}")
    url = "https://find-and-update.company-information.service.gov.uk/advanced-search/get-results?companyNameIncludes=" + company_name
    print(f"Search URL: {url}")
    response = requests.get(url)
    print(f"Search request status code: {response.status_code}")
    print(f"Search response content: {response.text}")
    soup = BeautifulSoup(response.text, 'html.parser')
    #print(soup)
    active_companies = []
    for row in soup.select('tr.govuk-table__row'):
        #print(row)
        status = row.select_one('.status')
        if status and status.text.strip() == 'Active':
            company_link = row.select_one('a')
            if company_link:
                active_companies.append({
                    'name': company_link.text.strip(),
                    'url': f"https://find-and-update.company-information.service.gov.uk{company_link['href']}"
                })
    print(f"Found {len(active_companies)} active companies")
    return active_companies

def scrape_company_details(company_url):
    print(f"Scraping company details from: {company_url}")
    response = requests.get(company_url)
    print(f"Company details request status code: {response.status_code}")
    soup = BeautifulSoup(response.text, 'html.parser')
    overview = {}
    overview['registered_office_address'] = soup.select_one('.govuk-summary-list__value').text.strip()
    overview['company_status'] = soup.select_one('.govuk-summary-list__value')
    overview['company_type'] = soup.select_one('.govuk-summary-list__value')
    overview['incorporated_on'] = soup.select_one('.govuk-summary-list__value')
    print("Scraped overview details:", overview)

    people_url = f"{company_url}/officers"
    print(f"Scraping people details from: {people_url}")
    people_response = requests.get(people_url)
    print(f"People details request status code: {people_response.status_code}")
    people_soup = BeautifulSoup(people_response.text, 'html.parser')
    people = []
    for officer in people_soup.select('.officer-name-with-appointment-type'):
        person = {
            'name': officer.select_one('h2').text.strip(),
            'role': officer.select_one('span').text.strip()
        }
        people.append(person)
    print(f"Scraped {len(people)} people")
    return {
        'overview': overview,
        'people': people
    }

def main():
    company_name = "Incept5 Limited"
    print(f"Starting search for: {company_name}")
    active_companies = search_company(company_name)
    result = {
        'active_companies': []
    }
    for company in active_companies:
        print(f"Processing company: {company['name']}")
        details = scrape_company_details(company['url'])
        company_data = {
            'name': company['name'],
            'overview': details['overview'],
            'people': details['people']
        }
        result['active_companies'].append(company_data)
    print("Final result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()