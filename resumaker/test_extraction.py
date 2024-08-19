import requests
from bs4 import BeautifulSoup

def fetch_full_page_source(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        response = session.get(url)
        response.raise_for_status()  # Raise an error for bad responses like 429

        return response.text
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {str(e)}")

    return None

def extract_details(html_content):
    """Extract all relevant job details from the HTML using generalized logic."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Initialize an empty dictionary to store extracted details
    details = {}

    # Try different methods to find the job title
    # Job Title: Look for <h1>, <h2> tags that are likely to contain the title
    job_title = soup.find(['h1', 'h2'])
    if not job_title:
        # Try to find a more common pattern if the first attempt fails
        job_title = soup.find('title')  # Sometimes the page title contains the job title
    details['job_title'] = job_title.get_text().strip() if job_title else "Unknown"

    # Company Name: Look for <div> or <span> containing common patterns like "company" or "employer"
    # We'll extract all possible candidates and filter based on known patterns
    possible_company_names = soup.find_all(['div', 'span', 'a'])
    for element in possible_company_names:
        text = element.get_text().strip()
        # Check for typical keywords in the link or span text
        if 'company' in text.lower() or 'employer' in text.lower():
            details['employer_name'] = text
            break
        elif 'at ' in text.lower() or 'by ' in text.lower():
            details['employer_name'] = text.split(' at ')[-1] if 'at ' in text.lower() else text.split(' by ')[-1]
            break
    else:
        details['employer_name'] = "Unknown"

    # Job Description: Combine all <p> tags for the job description
    # Assumption: Job description is the longest continuous block of text
    all_paragraphs = soup.find_all('p')
    job_description = max(all_paragraphs, key=lambda p: len(p.get_text()), default=None)
    details['job_description'] = job_description.get_text().strip() if job_description else "No description available"

    # Location: Check for common location patterns or map points
    possible_locations = soup.find_all(['div', 'span'])
    for element in possible_locations:
        text = element.get_text().strip()
        if any(keyword in text.lower() for keyword in ['location', 'city', 'state', 'country']):
            details['location'] = text
            break
    else:
        details['location'] = "Unknown"

    # Add more fields if needed based on the HTML structure

    # Return extracted details as a dictionary
    return details

def test_extraction(url):
    html_content = fetch_full_page_source(url)

    if not html_content:
        print("Failed to retrieve the HTML content.")
        return

    # Extract job details
    job_details = extract_details(html_content)

    # Print extracted details for inspection
    print("Extracted Job Details:")
    for key, value in job_details.items():
        print(f"{key}: {value}")

if __name__ == '__main__':
    # URL of the job posting to test
    url = "https://www.linkedin.com/jobs/view/3951156859/"  # Replace with the actual URL you want to test
    test_extraction(url)
