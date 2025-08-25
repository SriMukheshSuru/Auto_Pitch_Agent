import re
import pandas as pd
import numpy as np
import faiss
import pickle
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sentence_transformers import SentenceTransformer

# -----------------
# Google Sheets Auth
# -----------------
# Test VC data set
# SHEET_URL = "https://docs.google.com/spreadsheets/d/1JuOvz1yqnUPaZkA5iGVMxxtVJbECQhLGqz4XkCmd_sA/edit?gid=0"

# original OPEN VC Dataset

SHEET_URL = "https://docs.google.com/spreadsheets/d/1Hof1KGq4opP5UFf1xoRRkmCD9K56iI1XVixNgnR8NWI/edit?gid=0#gid=0"

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
client = gspread.authorize(creds)

# Open the sheet
spreadsheet = client.open_by_url(SHEET_URL)
worksheet = spreadsheet.get_worksheet(0)  # First sheet
data = worksheet.get_all_records()

# Convert to DataFrame
df = pd.DataFrame(data)

# -----------------
# Preprocessing
# -----------------
def clean_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r'<[^>]+>', '', text)  # remove HTML tags
    text = re.sub(r'\s+', ' ', text).strip()
    return text

df['final_investment_thesis_clean'] = df['Final Investment thesis'].apply(clean_text)

# -----------------
# Load model & encode
# -----------------
model = SentenceTransformer("sentence-transformers/all-distilroberta-v1")
embeddings = model.encode(df['final_investment_thesis_clean'].tolist(), show_progress_bar=True)
embeddings = np.array(embeddings, dtype="float32")

# -----------------
# Store in FAISS
# -----------------
dimension = embeddings.shape[1]
faiss.normalize_L2(embeddings)  # for cosine similarity
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

# Save for later
faiss.write_index(index, "investor_index.faiss")
df.to_pickle("investor_data.pkl")

print(f"✅ Stored {len(df)} investors from Google Sheet into FAISS.")
