# import os
# import pandas as pd
# import streamlit as st
# from dotenv import load_dotenv

# from m1_analyze_company import analyze_company
# from m2_investor_match import find_matching_investors
# from m3_email_sender import send_personalized_emails


# def send_emails_callback():
#     """Callback used by the "Generate and Send Emails" button.
#     It reads saved analysis & matches from st.session_state so a rerun won't lose them.
#     """
#     if not st.session_state.get("analyzed"):
#         st.error("No analysis found. Please click 'Analyze Company' first.")
#         return

#     summary_text = st.session_state.get("summary_text")
#     matches_df = st.session_state.get("matches_df")
#     founder_name = st.session_state.get("founder_name", None)
#     company_name = st.session_state.get("company_name_sidebar", None)
#     dry_run = st.session_state.get("dry_run_toggle", True)

#     try:
#         send_personalized_emails(
#             summary_text,
#             matches_df,
#             founder_name=founder_name.strip() if founder_name else None,
#             company_name=company_name.strip() if company_name else None,
#             dry_run=dry_run,
#         )
#         st.success("Done. Check console/logs for per-recipient status.")
#     except Exception as e:
#         st.error(f"Error while sending emails: {e}")


# def main():
#     st.set_page_config(page_title="Auto Pitch Agent", page_icon="📧", layout="wide")
#     load_dotenv()

#     st.title("Auto Pitch Agent")
#     st.markdown("Identify investors, generate personalized emails, and send — all in one place.")

#     # --- Sidebar ---
#     with st.sidebar:
#         st.header("Email Sending Settings")
#         # Use a checkbox (more portable than st.toggle)
#         default_dry = os.getenv("DRY_RUN", "true").strip().lower() == "true"
#         st.checkbox("Dry run (don't actually send)", value=default_dry, key="dry_run_toggle")
#         st.caption("When off, messages are sent using your environment's email credentials.")

#         st.divider()
#         st.header("Signature")
#         # store sidebar inputs in session_state so callbacks can access them
#         st.text_input("Your name", os.getenv("FOUNDER_NAME", ""), key="founder_name")
#         st.text_input("Company name", os.getenv("COMPANY_NAME", ""), key="company_name_sidebar")

#         st.divider()
#         st.slider("Number of investors to match", min_value=1, max_value=25, value=10, key="top_k")

#     # --- Main area: inputs ---
#     col1, col2 = st.columns(2)
#     with col1:
#         st.subheader("Company Inputs")
#         company_name_input = st.text_input("Company Name", key="company_name_input")
#         company_website_input = st.text_input("Company Website", placeholder="https://...", key="company_website_input")
#         analyze_clicked = st.button("Analyze Company", type="primary", key="analyze_button")

#     # When user clicks Analyze -> run analysis and save to session_state
#     if analyze_clicked:
#         if not company_name_input or not company_website_input:
#             st.error("Please provide both company name and website.")
#         else:
#             with st.spinner("Analyzing company with Gemini..."):
#                 summary_text = analyze_company(company_name_input, company_website_input)

#             if not summary_text:
#                 st.error("Could not analyze the company. Check your GEMINI_API_KEY and website.")
#             else:
#                 # persist results in session_state so a later rerun (e.g. clicking Send) keeps them
#                 st.session_state["summary_text"] = summary_text

#                 with st.spinner("Finding matching investors..."):
#                     matches_df = find_matching_investors(summary_text, top_k=st.session_state.get("top_k", 10))

#                 # keep the dataframe in session state
#                 st.session_state["matches_df"] = matches_df
#                 st.session_state["analyzed"] = True

#     # --- Display persisted results if available ---
#     if st.session_state.get("analyzed"):
#         st.subheader("Company Domains / Fields")
#         st.code(st.session_state.get("summary_text"))

#         st.subheader("Matching Investors")
#         st.dataframe(st.session_state.get("matches_df"), hide_index=True, use_container_width=True)

#         st.divider()
#         st.subheader("Send Emails")
#         # Use on_click so we get access to session_state values during the callback
#         st.button("Generate and Send Emails", on_click=send_emails_callback, key="send_emails_button")


# if __name__ == "__main__":
#     # initialize session state keys we rely on
#     if "analyzed" not in st.session_state:
#         st.session_state["analyzed"] = False
#     main()




# app.py
import os
import sys
import re
import time
import pandas as pd
from io import StringIO
from contextlib import contextmanager
from dotenv import load_dotenv
import streamlit as st

from m1_analyze_company import analyze_company
from m2_investor_match import find_matching_investors
from m3_email_sender import send_personalized_emails

# ---------------------------
# Utility: capture stdout/stderr live and push to a callback
# ---------------------------
class StdoutCatcher:
    """
    Redirects writes to a callback in near-real-time.
    It accumulates partial writes until newline so you get full lines.
    """
    def __init__(self, on_line):
        self.on_line = on_line
        self._buffer = ""

    def write(self, s):
        if not s:
            return
        self._buffer += s
        # splitlines keeps line endings if keepends=True; but we only want completed lines
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            # ignore empty lines
            if line.strip():
                try:
                    self.on_line(line.rstrip())
                except Exception:
                    # swallowing any UI exceptions so sending keeps going
                    pass

    def flush(self):
        # push remaining partial line as well
        if self._buffer.strip():
            try:
                self.on_line(self._buffer.rstrip())
            except Exception:
                pass
        self._buffer = ""

@contextmanager
def capture_output(on_line):
    """Context manager to temporarily redirect stdout/stderr to StdoutCatcher."""
    catcher = StdoutCatcher(on_line)
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = catcher
    sys.stderr = catcher
    try:
        yield
    finally:
        # flush any remaining buffered text
        try:
            catcher.flush()
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

# ---------------------------
# Streamlit app
# ---------------------------
def init_session_state():
    defaults = {
        "analyzed": False,
        "summary_text": None,
        "matches_df": None,
        "logs": [],
        "send_count": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def main():
    st.set_page_config(page_title="Auto Pitch Agent", page_icon="📧", layout="wide")
    load_dotenv()
    init_session_state()

    st.title("Auto Pitch Agent")
    st.markdown("Identify investors, generate personalized emails, and send — all in one place.")

    # Sidebar
    with st.sidebar:
        st.header("Email Sending Settings")
        default_dry = os.getenv("DRY_RUN", "true").strip().lower() == "true"
        # st.checkbox("Dry run (don't actually send)", value=default_dry, key="dry_run_toggle")
        dry_run = st.toggle("Dry run (don't actually send)", value=default_dry, key="dry_run_toggle")
        st.caption("When off, messages are sent using your environment's email credentials.")

        st.divider()
        st.header("Signature")
        st.text_input("Your name", os.getenv("FOUNDER_NAME", ""), key="founder_name")
        st.text_input("Company name", os.getenv("COMPANY_NAME", ""), key="company_name_sidebar")

        st.divider()
        st.slider("Number of investors to match", min_value=1, max_value=25, value=10, key="top_k")

    # Main inputs
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Company Inputs")
        company_name_input = st.text_input("Company Name", key="company_name_input")
        company_website_input = st.text_input("Company Website", placeholder="https://...", key="company_website_input")
        analyze_clicked = st.button("Analyze Company", type="primary", key="analyze_button")

    # Analyze action
    if analyze_clicked:
        if not company_name_input or not company_website_input:
            st.error("Please provide both company name and website.")
        else:
            with st.spinner("Analyzing company with Gemini..."):
                summary_text = analyze_company(company_name_input, company_website_input)

            if not summary_text:
                st.error("Could not analyze the company. Check your GEMINI_API_KEY and website.")
            else:
                # store analysis and matches
                st.session_state["summary_text"] = summary_text
                with st.spinner("Finding matching investors..."):
                    try:
                        matches_df = find_matching_investors(summary_text, top_k=st.session_state.get("top_k", 10))
                        # ensure it's a DataFrame for display; attempt conversion if not
                        if not isinstance(matches_df, pd.DataFrame):
                            try:
                                matches_df = pd.DataFrame(matches_df)
                            except Exception:
                                # at minimum wrap it
                                matches_df = pd.DataFrame({"raw": [str(matches_df)]})
                    except Exception as e:
                        st.error(f"Error while finding investors: {e}")
                        matches_df = pd.DataFrame()

                st.session_state["matches_df"] = matches_df
                st.session_state["analyzed"] = True
                # reset logs & counters when new analysis runs
                st.session_state["logs"] = []
                st.session_state["send_count"] = 0

    # Show results if available
    if st.session_state.get("analyzed"):
        st.subheader("Company Domains / Fields")
        st.code(st.session_state.get("summary_text"))

        st.subheader("Matching Investors")
        st.dataframe(st.session_state.get("matches_df"), hide_index=True, use_container_width=True)

        st.divider()
        st.subheader("Send Emails")

        # UI placeholders for logs and progress
        log_placeholder = st.empty()
        progress_placeholder = st.empty()
        # show compact log area initially (will be updated live)
        log_placeholder.text("Logs will appear here when you send emails.")

        # send button runs callback in-line (so we can capture stdout)
        if st.button("Generate and Send Emails", key="send_emails_button"):
            summary_text = st.session_state.get("summary_text")
            matches_df = st.session_state.get("matches_df")
            founder_name = st.session_state.get("founder_name", None)
            company_name = st.session_state.get("company_name_sidebar", None)
            dry_run = bool(st.session_state.get("dry_run_toggle", True))

            if summary_text is None or matches_df is None or len(matches_df) == 0:
                st.error("No analysis/matches available. Please run Analyze Company first.")
            else:
                total = len(matches_df)
                # prepare session state values
                st.session_state["logs"] = []
                st.session_state["send_count"] = 0

                # define how UI receives each log line
                def on_ui_log(line):
                    """Append log line and update the UI placeholders and progress."""
                    # append trimmed lines only
                    line = line.rstrip()
                    if not line:
                        return
                    st.session_state["logs"].append(line)
                    # keep only last 1000 lines to avoid memory bloat
                    if len(st.session_state["logs"]) > 1000:
                        st.session_state["logs"] = st.session_state["logs"][-1000:]

                    # attempt to detect a 'send' event to increment progress
                    low = line.lower()
                    sent_keywords = ["mail sent", "sent to", "simulated send", "simulated", "delivered", "failed to send", "failed"]
                    if any(k in low for k in sent_keywords):
                        st.session_state["send_count"] += 1
                        # clamp
                        if st.session_state["send_count"] > total:
                            st.session_state["send_count"] = total

                    # update text area and progress bar
                    # show last 300 lines
                    preview = "\n".join(st.session_state["logs"][-300:])
                    log_placeholder.text(preview)

                    # update progress
                    try:
                        pct = int(100 * st.session_state["send_count"] / max(1, total))
                    except Exception:
                        pct = 0
                    progress_placeholder.progress(pct)

                # Try calling send_personalized_emails with on_log if supported.
                # If it doesn't accept on_log, fall back to capturing stdout/stderr.
                exception_raised = None
                returned_logs = None

                # First try: call with on_log keyword (most robust if you've updated m3_email_sender.py)
                try:
                    # important: we rely on the function performing synchronous prints/callbacks
                    returned = send_personalized_emails(
                        summary_text,
                        matches_df,
                        founder_name=founder_name.strip() if founder_name else None,
                        company_name=company_name.strip() if company_name else None,
                        dry_run=dry_run,
                        on_log=on_ui_log,  # pass the UI logger
                    )
                    # if the function returns logs (list), capture them for the final display
                    if isinstance(returned, (list, tuple)):
                        returned_logs = list(returned)
                except TypeError as te:
                    # function likely doesn't accept on_log kwarg — fallback below
                    exception_raised = te
                except Exception as e:
                    # other exception from the function: show it and continue
                    exception_raised = e

                # Fallback if on_log wasn't accepted or an exception occurred before sending
                if exception_raised is not None:
                    # clear any partial progress & logs (we will capture proper output below)
                    st.session_state["logs"] = []
                    st.session_state["send_count"] = 0
                    log_placeholder.text("Switching to stdout-capture fallback (capturing prints).")
                    progress_placeholder.progress(0)
                    time.sleep(0.05)

                    try:
                        # capture prints/stderr during send_personalized_emails call
                        with capture_output(on_ui_log):
                            maybe_returned = send_personalized_emails(
                                summary_text,
                                matches_df,
                                founder_name=founder_name.strip() if founder_name else None,
                                company_name=company_name.strip() if company_name else None,
                                dry_run=dry_run,
                            )
                        if isinstance(maybe_returned, (list, tuple)):
                            returned_logs = list(maybe_returned)
                    except Exception as e:
                        # final fallback: show exception and any logs captured so far
                        st.error(f"Error while sending emails: {e}")
                        # also append exception message to logs for traceability
                        on_ui_log(f"ERROR: {e}")

                # Finalize: if function returned logs and we didn't see them via callback, show them
                if returned_logs:
                    # add returned logs into session logs and update UI
                    for line in returned_logs:
                        on_ui_log(str(line))

                # Final status
                progress_placeholder.empty()
                st.success("Send process finished. See logs above for details.")
                # offer an expander with full logs
                with st.expander("Full logs (downloadable)", expanded=False):
                    st.text_area("Logs", value="\n".join(st.session_state["logs"]), height=400)

                # also provide a download button for the logs
                log_bytes = "\n".join(st.session_state["logs"]).encode("utf-8")
                st.download_button("Download logs", data=log_bytes, file_name="email_send_logs.txt", mime="text/plain")


if __name__ == "__main__":
    main()
