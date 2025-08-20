import os
import io
import contextlib
import time
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from m1_analyze_company import analyze_company
from m2_investor_match import find_matching_investors
from m3_email_sender import send_personalized_emails


def main():
    st.set_page_config(page_title="Auto Pitch Agent", page_icon="icon.png", layout="wide")
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
        founder_email = st.text_input("Your email", os.getenv("FOUNDER_EMAIL", os.getenv("EMAIL_FROM", "")))
        founder_phone = st.text_input("Your phone", os.getenv("FOUNDER_PHONE", ""))
        founder_linkedin = st.text_input("LinkedIn profile URL", os.getenv("FOUNDER_LINKEDIN", ""))

        st.divider()
        top_k = st.slider("Number of investors to match", min_value=1, max_value=25, value=10)

    # Persist results across reruns
    if "summary_text" not in st.session_state:
        st.session_state.summary_text = None
    if "matches_df" not in st.session_state:
        st.session_state.matches_df = None
    if "company_name_main" not in st.session_state:
        st.session_state.company_name_main = None

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

        st.session_state.summary_text = summary_text
        # Persist the company name from the main input for use in signature during send
        st.session_state.company_name_main = company_name_input

        with st.spinner("Finding matching investors..."):
            st.session_state.matches_df = find_matching_investors(summary_text, top_k=top_k)

    # Show analysis if present
    if st.session_state.summary_text:
        summary_placeholder.subheader("Company Domains / Fields")
        summary_placeholder.code(st.session_state.summary_text)

    # Show matches and sending UI if available
    if isinstance(st.session_state.matches_df, pd.DataFrame) and not st.session_state.matches_df.empty:
        matches_container = st.container()
        with matches_container:
            st.subheader("Matching Investors")
            st.dataframe(st.session_state.matches_df, hide_index=True, use_container_width=True)

        st.divider()
        st.subheader("Send Emails")
        logs_placeholder = st.empty()
        progress_placeholder = st.progress(0, text="Preparing to send emails...")
        if st.button("Generate and Send Emails"):
            with st.spinner("Generating personalized emails and sending..."):
                log_lines = []
                def push_log(line: str):
                    log_lines.append(line)
                    logs_placeholder.code("\n".join(log_lines))
                    time.sleep(0.02)

                total = len(st.session_state.matches_df)
                def push_progress(done: int, total_count: int):
                    pct = int((done / max(total_count, 1)) * 100)
                    progress_placeholder.progress(pct, text=f"Sending emails... {done}/{total_count}")

                send_personalized_emails(
                    st.session_state.summary_text,
                    st.session_state.matches_df,
                    founder_name=founder_name.strip() or None,
                    company_name=(st.session_state.company_name_main or "").strip() or None,
                    founder_email=founder_email.strip() or None,
                    founder_phone=founder_phone.strip() or None,
                    founder_linkedin=founder_linkedin.strip() or None,
                    dry_run=dry_run,
                    email_column="Email",
                    on_log=push_log,
                    on_progress=push_progress,
                )
            progress_placeholder.progress(100, text="Completed")
            st.success("Done.")


if __name__ == "__main__":
    main()


