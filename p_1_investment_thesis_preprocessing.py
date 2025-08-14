import os
import cloudscraper
import requests
import pandas as pd
from bs4 import BeautifulSoup
import subprocess
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIG ---
load_dotenv()
MODEL = "llama3:8b"  # lightweight model
SHEET_ID = "1Hof1KGq4opP5UFf1xoRRkmCD9K56iI1XVixNgnR8NWI"
SHEET_NAME = "Sheet1"  # Change if needed
SERVICE_ACCOUNT_FILE = "service_account.json"  # Your Google API credentials

# -------- Helper: Scrape homepage text --------
def scrape_homepage(url):
    if not isinstance(url, str) or not url.strip():
        return ""
    try:
        scraper = cloudscraper.create_scraper()  # Create a cloudscraper session
        response = scraper.get(url.strip(), timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return ""
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(soup.stripped_strings)
    return text[:2000]  # limit text length

# -------- Helper: Call Ollama locally --------
def ollama_query(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL],
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=60
        )
        return result.stdout.decode("utf-8").strip()
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return ""

# -------- Main processing --------
def update_google_sheet(sheet_id, sheet_name):
    # Auth to Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)

    # Get all values including empty columns
    all_values = sheet.get_all_values()
    header = all_values[0]
    data_rows = all_values[1:]

    # Find the column index for "Final Investment thesis"
    if "Final Investment thesis" not in header:
        header.append("Final Investment thesis")
        sheet.insert_row(header, 1)
        col_index = len(header)  # new column at the end
    else:
        col_index = header.index("Final Investment thesis") + 1  # 1-based index

    # Convert to DataFrame for easy looping
    df = pd.DataFrame(data_rows, columns=header)

    for idx, row in df.iloc[156:250].iterrows():
        name = row.get("Investor name", "")
        website = row.get("Website", "")
        existing_thesis = row.get("Investment thesis", "")

        print(f"\n🔍 Processing {name} ({website})...")

        homepage_text = scrape_homepage(website)

        if homepage_text:
            prompt = f"""
You are an investment analyst.

From the following homepage text:
{homepage_text}

1. Identify the main domains or fields this investor is interested in.
2. Summarize the investment interests clearly and concisely in 3–5 bullet points.
3. Do not include any introductory phrases like "Based on the homepage text" or "I identify".
4. Output only the bullet points.

After the bullet points, append this additional thesis information from their dataset:
"{existing_thesis}"
"""
            summary = ollama_query(prompt)
        else:
            summary = f"Website data unavailable. Investment thesis: {existing_thesis}"

        # Write directly to the correct cell
        sheet.update_cell(idx + 2, col_index, summary)  # +2 for header

    print("\n✅ Google Sheet updated successfully!")


# -------- Run --------
if __name__ == "__main__":
    update_google_sheet(SHEET_ID, SHEET_NAME)
