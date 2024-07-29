from flask import Flask, render_template, request, send_file, make_response
import requests
import openai
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import logging
import re
import io
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get OpenAI API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("No API key found. Please set the OPENAI_API_KEY environment variable.")

openai.api_key = api_key

# Suppress detailed stacktrace in the output
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('selenium').setLevel(logging.ERROR)

def get_completion(prompt, model="gpt-4-1106-preview"):
    completion = openai.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return completion.choices[0].message.content

def check_employer_accreditation(employer_name):
    url = "https://www.immigration.govt.nz/new-zealand-visas/preparing-a-visa-application/working-in-nz/check-if-an-employer-is-accredited"
    
    # Set up Selenium and open the browser
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    driver.get(url)

    # Find the input field and enter the employer name
    search_field = driver.find_element(By.NAME, 'keywords')
    search_field.send_keys(employer_name)

    # Click the search button
    search_button = driver.find_element(By.CSS_SELECTOR, 'input.btn__primary')
    search_button.click()

    # Wait for results to load
    driver.implicitly_wait(10)

    # Check if the employer is accredited
    try:
        no_results_message = driver.find_element(By.XPATH, "//div[contains(@class, 'banner__alert') and contains(., 'Sorry')]")
        accredited = False
    except:
        accredited = True

    driver.quit()
    
    return accredited

def extract_main_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    main_content = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
    content_text = "\n".join([element.get_text() for element in main_content])
    return content_text

def summarize_content(content):
    prompt = f"Summarize the following content:\n\n{content}"
    summary = get_completion(prompt, model="gpt-3.5-turbo")
    return summary.strip()

def extract_detail(detail, html_content):
    main_content = extract_main_content(html_content)
    summary = summarize_content(main_content)
    prompt = f"""
        Extract the {detail} text from the following summarized content.
        Return back just the precise {detail} text without quotes:
        \n\n{summary}
        \n\nJob Description:
    """
    job_description = get_completion(prompt, model="gpt-3.5-turbo")
    return job_description.strip()

def extract_skills_and_tools(html_content):
    main_content = extract_main_content(html_content)
    summary = summarize_content(main_content)
    prompt = f"""
        Extract a comprehensive list of both hard skills and soft skills required from the following job description.
        Return the skills and tools as a comma-separated list:
        \n\n{summary}
    """
    skills_and_tools = get_completion(prompt, model="gpt-4-1106-preview")
    return [skill.strip() for skill in skills_and_tools.split(',')]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_html', methods=['POST'])
def get_html():
    url = request.form['url']
    try:
        response = requests.get(url)
        html_content = response.text

        # Use OpenAI API to extract employer name
        employer_name = extract_detail("employer name", html_content)

        # Check if employer is accredited
        is_accredited = check_employer_accreditation(employer_name)

        job_role = job_description = skills_and_tools = None
        if is_accredited:
            # Extract job description text
            job_description = extract_detail("job description", html_content)
            
            # Extract job role text
            job_role = extract_detail("job role", html_content)
            
            # Extract skills and tools
            skills_and_tools = extract_skills_and_tools(html_content)

        return render_template('result.html', url=url, job_role=job_role, job_description=job_description, employer_name=employer_name, is_accredited=is_accredited, skills_and_tools=skills_and_tools)

    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
