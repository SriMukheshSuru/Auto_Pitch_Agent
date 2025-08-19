import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-distilroberta-v1"
PREFERRED_EMAIL_COLUMNS = [
    "Email",
    "email",
    "Email Address",
    "Investor Email",
    "Contact Email",
]

# Load model, FAISS index, and investor data once
print("🔄 Loading model & data...")
model = SentenceTransformer(MODEL_NAME)
df = pd.read_pickle("investor_data.pkl")
index = faiss.read_index("investor_index.faiss")

def find_matching_investors(summary, top_k=5):
    # Encode query
    summary_emb = model.encode([summary]).astype("float32")
    faiss.normalize_L2(summary_emb)  # cosine similarity

    # Search in FAISS
    distances, indices = index.search(summary_emb, top_k)

    # Prepare results
    results = df.iloc[indices[0]].copy()
    results["similarity"] = distances[0]

    # Build a robust set of return columns
    desired_columns = ['Investor name', 'Website']
    # Try to include an email column if present
    for col in PREFERRED_EMAIL_COLUMNS:
        if col in results.columns:
            desired_columns.append(col)
            break
    # Optionally include thesis for better personalization downstream
    if 'Final Investment thesis' in results.columns:
        desired_columns.append('Final Investment thesis')
    desired_columns.append('similarity')

    # Filter to existing columns only (defensive against schema drift)
    desired_columns = [c for c in desired_columns if c in results.columns]
    return results[desired_columns]
    

# Example usage
# if __name__ == "__main__":
#     company_summary = "data science and ai"
#     matches = find_matching_investors(company_summary, top_k=10)
#     print(matches)
