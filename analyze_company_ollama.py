import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import subprocess
import json

# Load environment variables
MODEL = "llama3:8b"

# Step 1: Get inputs
company_name = input("Enter Company Name: ")
company_website = input("Enter Company Website (with https://): ")

# Step 2: Scrape only homepage
try:
    response = requests.get(company_website, timeout=10)
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
From the following homepage text of {company_name}, identify the main domains or fields this company is interested in.
Give the answer as a short bullet list.

Homepage Text:
{text}
"""

# Step 5: Call Ollama LLM locally
result = subprocess.run(
    ["ollama", "run", MODEL],
    input=prompt.encode("utf-8"),
    capture_output=True
)

# Step 6: Output results
print("\n--- Company Domains / Fields ---")
print(result.stdout.decode("utf-8").strip())

