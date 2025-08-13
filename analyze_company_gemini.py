import os
import cloudscraper
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")  # default model

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not found in .env file.")
    exit()

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Step 1: Get inputs
company_name = input("Enter Company Name: ")
company_website = input("Enter Company Website (with https://): ")

# Step 2: Scrape homepage using cloudscraper (bypasses Cloudflare & basic bot protections)
scraper = cloudscraper.create_scraper()
try:
    response = scraper.get(company_website, timeout=15)
    response.raise_for_status()
except Exception as e:
    print(f"Error fetching website: {e}")
    exit()

# Step 3: Extract visible text
soup = BeautifulSoup(response.text, "html.parser")
for tag in soup(["script", "style", "noscript"]):
    tag.decompose()

text = " ".join(soup.stripped_strings)
text = text[:1500]  # Keep only first 1500 characters

# Step 4: Prepare LLM prompt
prompt = f"""
From the following homepage text of {company_name}, list only the main domains or fields this company is interested in. 
Provide them as a simple bullet list of titles—no explanations.
Homepage Text:
{text}
"""

# Step 5: Call Gemini API
try:
    model = genai.GenerativeModel(MODEL)
    gemini_response = model.generate_content(prompt)
except Exception as e:
    print(f"Error calling Gemini API: {e}")
    exit()

# Step 6: Output results
print("\n--- Company Domains / Fields ---")
print(gemini_response.text.strip())
