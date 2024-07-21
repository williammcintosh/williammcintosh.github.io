from flask import Flask, render_template, request
import requests
import openai
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import logging

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

def extract_job_description(html_content):
    prompt = f"Extract the job description text from the following HTML content:\n\n{html_content}\n\nJob Description:"
    job_description = get_completion(prompt)
    return job_description.strip()

def generate_resume_prompt(job_description):
    with open("resume_prompt.txt", "r") as file:
        resume_prompt = file.read()
    
    resume_prompt = resume_prompt.replace("{{JOB_DESCRIPTION}}", job_description)
    return resume_prompt

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
        employer_name = extract_employer_name(html_content)

        # Check if employer is accredited
        is_accredited = check_employer_accreditation(employer_name)

        resume_latex = None
        if is_accredited:
            # Extract job description text
            job_description = extract_job_description(html_content)
            
            # Generate resume prompt
            resume_prompt = generate_resume_prompt(job_description)
            
            # Get resume LaTeX content
            resume_latex = get_completion(resume_prompt)
        
        return render_template('result.html', url=url, employer_name=employer_name, is_accredited=is_accredited, resume_latex=resume_latex)

    except Exception as e:
        return f"An error occurred: {str(e)}"

def extract_employer_name(html_content):
    prompt = f"Extract the employer name from the following job description HTML content:\n\n{html_content}\n\nEmployer Name:"
    employer_name = get_completion(prompt)
    return employer_name.strip()

if __name__ == '__main__':
    app.run(debug=True)
