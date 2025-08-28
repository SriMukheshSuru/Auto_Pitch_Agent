import os
import io
import contextlib
import time
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from urllib.parse import urlparse

from m1_analyze_company import analyze_company
from m2_investor_match import find_matching_investors
from m3_email_sender import send_personalized_emails

hide_theme_switcher = """
    <style>
        section[data-testid="stSidebarThemeSwitcher"],
        section[data-testid="stToolbar"] div[data-testid="stToolbarActions"] button[title="Settings"] {
            display: none;
        }
    </style>
"""

hide_menu = """
    <style>
        [data-testid="stToolbar"] {
            visibility: hidden;
            height: 0%;
        }
    </style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

st.markdown(hide_theme_switcher, unsafe_allow_html=True)

def show_landing_page():
    """Display the landing page with about and how it works content"""
    # Landing Page - Combined About Us + How It Works
    st.markdown('<h1 class="main-header">🚀 Auto Pitch Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-Powered Investor Matching & Personalized Outreach Platform</p>', unsafe_allow_html=True)
    
    # Hero banner
    banner_url = "assets/banner.jpg"
    try:
        local_banner = os.path.join(os.path.dirname(__file__), "assets", "banner.jpg")
        if os.path.exists(local_banner):
            import base64, mimetypes
            mime, _ = mimetypes.guess_type(local_banner)
            if not mime:
                mime = "image/jpeg"
            with open(local_banner, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            banner_url = f"data:{mime};base64,{b64}"
    except Exception:
        pass

    st.markdown(
        f"""
        <div class="hero-banner"></div>
        <style>
        .hero-banner {{
            background-image: linear-gradient(rgba(0,0,0,0.25), rgba(0,0,0,0.25)), url('{banner_url}');
            background-size: cover;
            background-position: center;
            height: 300px;
            border-radius: 12px;
            margin: 0 0 2rem 0;
            border: 1px solid rgba(49, 51, 63, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .hero-overlay {{
            text-align: center;
            color: white;
            padding: 2rem;
        }}
        .hero-title {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
        }}
        .hero-subtitle {{
            font-size: 1.2rem;
            margin-bottom: 2rem;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
        }}
        .cta-button {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            transition: transform 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }}
        @media (max-width: 640px) {{
            .hero-banner {{ height: 250px; }}
            .hero-title {{ font-size: 2rem; }}
            .hero-subtitle {{ font-size: 1rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Call-to-Action Section
    st.markdown('<div style="text-align: center; margin: 3rem 0;">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Finding Investors", type="primary", use_container_width=True, key="cta_top"):
            st.session_state.active_tab = "Pitch Agent"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # About Section
    st.markdown('<div class="about-section">', unsafe_allow_html=True)
    st.markdown("## 🎯 Revolutionize Your Investor Outreach")
    
    st.markdown("""
    **Auto Pitch Agent** is a cutting-edge AI-powered platform designed to revolutionize how startups connect with investors. 
    We analyze your company profile and match you with the most relevant investors 
    in our comprehensive database.
    """)
    
    # Features
    st.markdown("### ✨ Key Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
        <h4>🤖 AI-Powered Analysis</h4>
        <p>Our advanced AI analyzes your company website using Google's Gemini AI to understand your business domains and create a comprehensive profile.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
        <h4>🎯 Smart Matching</h4>
        <p>Using semantic search and vector embeddings, we match your company with investors who have the right investment thesis and portfolio focus.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
        <h4>📧 Personalized Outreach</h4>
        <p>Generate and send personalized emails to matched investors with tailored messaging that highlights why you're a perfect fit for their portfolio.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # How It Works Section
    st.markdown("---")
    st.markdown("## 📈 How It Works")
    st.markdown("### Simple 4-Step Process")
    
    steps_col1, steps_col2 = st.columns(2)
    
    with steps_col1:
        st.markdown("""
        <div class="feature-card">
        <h4>Step 1: Company Analysis 🔍</h4>
        <ul>
        <li>Enter your company name and website</li>
        <li>Our AI scrapes and analyzes your homepage</li>
        <li>Extracts key business domains and focus areas</li>
        <li>Creates a comprehensive company profile</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
        <h4>Step 3: Email Generation 📝</h4>
        <ul>
        <li>AI generates personalized email content</li>
        <li>Tailored messaging for each investor</li>
        <li>Highlights relevant portfolio fit</li>
        <li>Professional formatting and tone</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with steps_col2:
        st.markdown("""
        <div class="feature-card">
        <h4>Step 2: Investor Matching 🎯</h4>
        <ul>
        <li>Semantic search through investor database</li>
        <li>Matches based on investment thesis</li>
        <li>Considers portfolio companies and focus areas</li>
        <li>Ranks by relevance and fit score</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
        <h4>Step 4: Automated Outreach 🚀</h4>
        <ul>
        <li>Review and select target investors</li>
        <li>Send personalized emails automatically</li>
        <li>Track delivery and engagement</li>
        <li>Follow up strategically</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Technology Stack
    st.markdown("---")
    st.markdown("### 🔧 Powered by Advanced Technology")
    
    tech_col1, tech_col2, tech_col3 = st.columns(3)
    
    with tech_col1:
        st.markdown("""
        <div class="feature-card">
        <h4>🧠 AI & ML</h4>
        <ul>
        <li>Google Gemini AI, Ollama</li>
        <li>Sentence Transformers</li>
        <li>FAISS Vector Search</li>
        <li>Semantic Embeddings</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tech_col2:
        st.markdown("""
        <div class="feature-card">
        <h4>📊 Data Processing</h4>
        <ul>
        <li>Web Scraping</li>
        <li>BeautifulSoup</li>
        <li>CloudScraper</li>
        <li>Text Analysis</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tech_col3:
        st.markdown("""
        <div class="feature-card">
        <h4>⚡ Infrastructure</h4>
        <ul>
        <li>Streamlit Frontend</li>
        <li>Python Backend</li>
        <li>Email Integration</li>
        <li>Real-time Processing</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Mission Statement
    st.markdown("---")
    st.markdown("### 💡 Our Mission")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; text-align: center; margin: 2rem 0;">
        <h3 style="color: white; margin-bottom: 1rem;">Democratizing Access to Investment Opportunities</h3>
        <p style="font-size: 1.1rem; margin: 0;">
            We believe that great startups shouldn't struggle to find the right investors. Our mission is to make 
            the investor discovery and outreach process more efficient, targeted, and successful for entrepreneurs worldwide.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Final CTA
    st.markdown('<div style="text-align: center; margin: 4rem 0 2rem 0;">', unsafe_allow_html=True)
    st.markdown('<h3>Ready to Connect with the Right Investors?</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Launch Auto Pitch Agent", type="primary", use_container_width=True, key="cta_bottom"):
            st.session_state.active_tab = "Pitch Agent"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def show_tool_interface():
    """Display the main tool interface"""
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🏠 Back to Home", type="secondary", use_container_width=True):
            st.session_state.active_tab = "Home"
            st.rerun()
    # with col2:
        # st.markdown('<p style="text-align: center; margin: 0; padding: 0.5rem;"><strong>🚀 Auto Pitch Agent Tool</strong></p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tool header
    st.markdown("# 🚀 Auto Pitch Agent Tool")
    st.markdown("### Enter your company details to find matching investors")

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
        # Normalize and validate website URL
        website = (company_website_input or "").strip()
        if website and not (website.startswith("http://") or website.startswith("https://")):
            website = "https://" + website
        
        def _is_plausible_url(u: str) -> bool:
            try:
                parsed = urlparse(u)
                if parsed.scheme not in ("http", "https"):
                    return False
                if any(ch.isspace() for ch in u):
                    return False
                host = parsed.netloc
                if not host:
                    return False
                # Remove port if present
                if ":" in host:
                    host = host.split(":", 1)[0]
                if host.startswith(".") or host.endswith("."):
                    return False
                labels = host.split(".")
                if len(labels) < 2:
                    return False
                tld = labels[-1]
                if not tld.isalpha() or len(tld) < 2:
                    return False
                return True
            except Exception:
                return False

        is_valid = _is_plausible_url(website)
        if not is_valid:
            st.error("Please enter a valid URL")
            return

        with st.spinner("Analyzing company with Gemini..."):
            summary_text = analyze_company(company_name_input, website)
        if not summary_text:
            st.error("Could not analyze the company. Please enter a valid URL.")
            return

        st.session_state.summary_text = summary_text
        # Persist the company name from the main input for use in signature during send
        st.session_state.company_name_main = company_name_input

        with st.spinner("Finding matching investors..."):
            st.session_state.matches_df = find_matching_investors(summary_text, top_k=top_k)

    # Show analysis if present
    if st.session_state.summary_text:
        summary_placeholder.subheader("Company Domains / Fields")
        summary_placeholder.markdown(st.session_state.summary_text)

    # Show matches and sending UI if available
    if isinstance(st.session_state.matches_df, pd.DataFrame) and not st.session_state.matches_df.empty:
        matches_container = st.container()
        with matches_container:
            st.subheader("Matching Investors (select recipients)")
        editable_df = st.session_state.matches_df.copy()
        if "Include" not in editable_df.columns:
            try:
                editable_df.insert(0, "Include", True)
            except Exception:
                editable_df["Include"] = True
        edited_df = st.data_editor(
            editable_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Include": st.column_config.CheckboxColumn("Include", help="Uncheck to exclude this investor from sending")
            },
            num_rows="fixed",
            key="matches_editor",
        )
        try:
            selected_df = edited_df[edited_df["Include"] == True].drop(columns=["Include"])  # noqa: E712
        except Exception:
            selected_df = st.session_state.matches_df
        st.session_state.matches_df_selected = selected_df
        st.caption(f"Will send to {len(selected_df)}/{len(st.session_state.matches_df)} selected investors.")

        st.divider()
        st.subheader("Send Emails")
        logs_placeholder = st.empty()
        progress_placeholder = st.empty()
        if st.button("Generate and Send Emails", type="primary"):
            with st.spinner("Generating personalized emails and sending..."):
                log_lines = []
                def push_log(line: str):
                    log_lines.append(line)
                    logs_placeholder.code("\n".join(log_lines))
                    time.sleep(0.02)

                selected_to_send = st.session_state.get("matches_df_selected")
                if isinstance(selected_to_send, pd.DataFrame):
                    df_to_send = selected_to_send
                else:
                    df_to_send = st.session_state.matches_df
                total = len(df_to_send)
                progress_bar = progress_placeholder.progress(0, text="Preparing to send emails...")
                def push_progress(done: int, total_count: int):
                    pct = int((done / max(total_count, 1)) * 100)
                    progress_bar.progress(pct, text=f"Sending emails... {done}/{total_count}")

                send_personalized_emails(
                    st.session_state.summary_text,
                    df_to_send,
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
            progress_bar.progress(100, text="Completed")
            st.success("Done.")


def main():
    st.set_page_config(
        page_title="Auto Pitch Agent - AI-Powered Investor Matching", 
        page_icon="icon.png", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    load_dotenv()

    # Custom CSS for professional styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.3rem;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .about-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 2rem 0;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        border-top: 1px solid #eee;
        margin-top: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize tab state
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Home"
    
    # Check if we need to switch tabs
    if st.session_state.active_tab == "Pitch Agent":
        # Show tool directly
        show_tool_interface()
    else:
        # Show landing page
        show_landing_page()

    # Footer
    st.markdown("""
    <div class="footer">
    <p>🚀 <strong>Auto Pitch Agent</strong> - Powered by AI | Built for Entrepreneurs</p>
    <p>© 2025 Auto Pitch Agent. Connecting startups with the right investors.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()