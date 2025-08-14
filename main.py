# main.py
from m1_analyze_company import analyze_company
from m2_investor_match import find_matching_investors

if __name__ == "__main__":
    # Step 1: Get company summary from Gemini
    summary = analyze_company()
    if not summary:
        print("❌ Could not analyze company.")
        exit()

    print("\n--- Company Domains / Fields ---")
    print(summary)

    # Step 2: Find matching investors
    matches = find_matching_investors(summary, top_k=10)
    print("\n--- Matching Investors ---")
    print(matches.to_string(index=False))
