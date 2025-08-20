# main.py
import os
from dotenv import load_dotenv
from m1_analyze_company import analyze_company
from m2_investor_match import find_matching_investors
from m3_email_sender import send_personalized_emails

if __name__ == "__main__":
    load_dotenv()
    # Step 1: Get company summary from Gemini, taking company inputs here
    company_name = input("Company name: ").strip()
    company_website = input("Company website (with https://): ").strip()
    summary = analyze_company(company_name, company_website)
    if not summary:
        print("❌ Could not analyze company.")
        exit()

    print("\n--- Company Domains / Fields ---")
    print(summary)

    # Step 2: Find matching investors
    matches = find_matching_investors(summary, top_k=5)
    print("\n--- Matching Investors ---")
    print(matches.to_string(index=False))

    # Step 3: Generate and send personalized emails
    print("\n--- Sending Personalized Emails ---")
    founder_name = input("Your name (for signature): ").strip()
    founder_email = input("Your email (for signature): ").strip()
    founder_phone = input("Your phone (for signature): ").strip()
    founder_linkedin = input("Your LinkedIn profile URL (for signature): ").strip()
    # Default to actually sending unless explicitly set to true
    DRY_RUN = os.getenv("DRY_RUN", "false").strip().lower() == "true"
    send_personalized_emails(
        summary,
        matches,
        founder_name=founder_name,
        company_name=company_name,
        founder_email=founder_email or None,
        founder_phone=founder_phone or None,
        founder_linkedin=founder_linkedin or None,
        dry_run=DRY_RUN,
    )
