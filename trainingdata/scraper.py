import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import re
from xhtml2pdf import pisa

# === CONFIGURATION ===
BASE_URL = "https://washu.atlassian.net/wiki"
load_dotenv(dotenv_path=".env.local")
USERNAME = os.getenv("USERNAME")
API_TOKEN = os.getenv("API_TOKEN")
SPACE_KEY = "RUD"                 # Replace with your space key
LIMIT = 5                          # Number of pages to fetch
START = 0                          # Start page

# === REQUEST HEADERS ===
headers = {
    "Accept": "application/json"
}

# === MAIN FUNCTION ===
def get_confluence_pages():
    total_pages = 0
    url = f"{BASE_URL}/rest/api/content"

    params = {
        "spaceKey": SPACE_KEY,
        "limit": LIMIT,
        "expand": "body.storage",
        "start": START
    }

    while True:
        response = requests.get(url, headers=headers, auth=HTTPBasicAuth(USERNAME, API_TOKEN), params=params)
        response.raise_for_status()
        if response.json().get("_links", {}).get("next"):
            params["start"] += LIMIT
        else:
            break

        # Parse the JSON response
        num_pages = parse_pages(response)
        total_pages += num_pages
        print(f"Total pages: {total_pages}")

def parse_pages(response):
    data = response.json()
    num_pages = 0
    for page in data.get("results", []):
        num_pages += 1
        title = page.get("title")
        body_html = page.get("body", {}).get("storage", {}).get("value")
        print("="*40)
        print(f"Title: {title}\n")
        print("Body:")

        # Parse the HTML content
        soup = BeautifulSoup(body_html, 'html.parser')

        # Extract text from the parsed HTML
        text = soup.get_text()
        print("Text Content:")
        print(text[:1000])  # Truncate for readability
        # Save the text to a file
        filename = re.sub(r'[<>:"/\\|?*]', '_', title)
        with open(f'trainingdata/Documentation/{filename}.txt', "w", encoding="utf-8") as f:
            f.write(text)

        # Convert HTML to PDF
        pdf_path = f'trainingdata/Documentation/{filename}.pdf'
        with open(pdf_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(body_html, dest=pdf_file)
            if pisa_status.err:
                raise Exception(f"Error creating PDF: {pisa_status.err}")
        
    return num_pages

if __name__ == "__main__":
    get_confluence_pages()