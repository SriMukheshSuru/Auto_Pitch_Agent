import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from m1_analyze_company import analyze_company
from m2_investor_match import find_matching_investors
from m3_email_sender import send_personalized_emails


def main():
    st.set_page_config(page_title="Auto Pitch Agent", page_icon="📧", layout="wide")
    load_dotenv()

    st.title("Auto Pitch Agent")
    st.markdown("Identify investors, generate personalized emails, and send — all in one place.")

    with st.sidebar:
        st.header("Email Sending Settings")
        default_dry = os.getenv("DRY_RUN", "true").strip().lower() == "true"
        dry_run = st.toggle("Dry run (don't actually send)", value=default_dry)
        st.caption("When off, messages are sent using your environment's email credentials.")

        st.divider()
        st.header("Signature")
        founder_name = st.text_input("Your name", os.getenv("FOUNDER_NAME", ""))
        company_name = st.text_input("Company name", os.getenv("COMPANY_NAME", ""))

        st.divider()
        top_k = st.slider("Number of investors to match", min_value=1, max_value=25, value=10)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Company Inputs")
        company_name_input = st.text_input("Company Name")
        company_website_input = st.text_input("Company Website", placeholder="https://...")
        analyze_clicked = st.button("Analyze Company", type="primary")

    summary_placeholder = st.empty()
    matches_placeholder = st.empty()

    if analyze_clicked:
        if not company_name_input or not company_website_input:
            st.error("Please provide both company name and website.")
            return

        with st.spinner("Analyzing company with Gemini..."):
            summary_text = analyze_company(company_name_input, company_website_input)
        if not summary_text:
            st.error("Could not analyze the company. Check your GEMINI_API_KEY and website.")
            return

        summary_placeholder.subheader("Company Domains / Fields")
        summary_placeholder.code(summary_text)

        with st.spinner("Finding matching investors..."):
            matches_df = find_matching_investors(summary_text, top_k=top_k)

        st.subheader("Matching Investors")
        matches_placeholder.dataframe(matches_df, hide_index=True, use_container_width=True)

        st.divider()
        st.subheader("Send Emails")
        if st.button("Generate and Send Emails"):
            with st.spinner("Generating personalized emails and sending..."):
                send_personalized_emails(
                    summary_text,
                    matches_df,
                    founder_name=founder_name.strip() or None,
                    company_name=company_name.strip() or None,
                    dry_run=dry_run,
                )
            st.success("Done. Check console/logs for per-recipient status.")


if __name__ == "__main__":
    main()


