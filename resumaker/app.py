from flask import Flask, render_template, request
import requests
import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get OpenAI API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("No API key found. Please set the OPENAI_API_KEY environment variable.")

openai.api_key = api_key

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

    # return completion.choices[0].message['content'].strip()

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

        return render_template('result.html', url=url, employer_name=employer_name)
    except Exception as e:
        return f"An error occurred: {str(e)}"

def extract_employer_name(html_content):
    prompt = f"Extract the employer name from the following job description HTML content:\n\n{html_content}\n\nEmployer Name:"
    employer_name = get_completion(prompt)
    return employer_name

if __name__ == '__main__':
    app.run(debug=True)
