import os
import re
import smtplib
from email.utils import formataddr
from email.mime.text import MIMEText
from typing import Optional, Tuple, Callable

import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()


def _configure_gemini() -> Optional[str]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("LLM_MODEL", "gemini-2.0-flash").strip()
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file.")
        return None
    genai.configure(api_key=api_key)
    return model_name


def _extract_subject_body(raw_text: str) -> Tuple[str, str]:
    # Expecting the model to return:
    # Subject: ...\n\nBody:\n<content>
    subject = ""
    body = raw_text.strip()
    match = re.search(r"^\s*Subject\s*:\s*(.+)$", raw_text, flags=re.IGNORECASE | re.MULTILINE)
    if match:
        subject = match.group(1).strip()
        body_part = re.split(r"^\s*Body\s*:\s*", raw_text, flags=re.IGNORECASE | re.MULTILINE)
        if len(body_part) > 1:
            body = body_part[1].strip()
        else:
            # Fallback: remove the first line (subject line)
            lines = raw_text.splitlines()
            body = "\n".join(lines[1:]).strip()
    else:
        # Fallback: first line up to 90 chars as subject
        first_line = raw_text.splitlines()[0] if raw_text.splitlines() else ""
        subject = first_line[:90].strip()
        body = raw_text.strip()
    return subject, body


def generate_personalized_email(
    company_summary: str,
    investor_name: str,
    investor_website: str,
    investor_thesis: Optional[str] = None,
    founder_name: Optional[str] = None,
    company_name: Optional[str] = None,
) -> Tuple[str, str]:
    model_name = _configure_gemini()
    if not model_name:
        return "", ""

    prompt = f"""
You are an expert startup fundraiser. Draft a concise, personalized cold email to an investor.

Constraints:
- Audience: {investor_name} (website: {investor_website}).
- Context about our company (from website analysis):\n{company_summary}
- Investor thesis (if provided):\n{investor_thesis or "N/A"}
- Keep it to 120–180 words, 2–3 short paragraphs, no fluff.
- Tailor one sentence to the investor's thesis or portfolio focus.
- Clear CTA for a 20–30 minute chat next week.
- Use a friendly, professional tone.
- Do not use placeholders like [Company] or [Investor]. Fill with best-guess real content from context.
- Output format strictly as:
Subject: <compelling one-line subject>

Body:
<final email body>

Signature should include {founder_name or "Founder"} and {company_name or "our company"}.
"""

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        raw = (response.text or "").strip()
        subject, body = _extract_subject_body(raw)
        return subject, body
    except Exception as e:
        print(f"❌ Error calling Gemini API: {e}")
        return "", ""


def _valid_email(addr: str) -> bool:
    if not isinstance(addr, str):
        return False
    addr = addr.strip()
    if not addr or addr.lower() in {"n/a", "na", "-", "none", "null"}:
        return False
    return re.match(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", addr, re.IGNORECASE) is not None


def _get_env_any(keys, default: str = "") -> str:
    for key in keys:
        val = os.getenv(key)
        if val is not None and str(val).strip() != "":
            return str(val).strip()
    return default


def _infer_smtp_host(from_email: str) -> Optional[str]:
    if not _valid_email(from_email):
        return None
    domain = from_email.split("@")[-1].lower()
    mapping = {
        "gmail.com": "smtp.gmail.com",
        "googlemail.com": "smtp.gmail.com",
        "outlook.com": "smtp.office365.com",
        "hotmail.com": "smtp.office365.com",
        "live.com": "smtp.office365.com",
        "office365.com": "smtp.office365.com",
        "yahoo.com": "smtp.mail.yahoo.com",
        "ymail.com": "smtp.mail.yahoo.com",
        "icloud.com": "smtp.mail.me.com",
        "me.com": "smtp.mail.me.com",
        "mac.com": "smtp.mail.me.com",
        "aol.com": "smtp.aol.com",
        "fastmail.com": "smtp.fastmail.com",
        "zoho.com": "smtp.zoho.com",
        "gmx.com": "mail.gmx.com",
        "gmx.de": "mail.gmx.net",
        "proton.me": "smtp.protonmail.ch",
        "protonmail.com": "smtp.protonmail.ch",
    }
    if domain in mapping:
        return mapping[domain]
    # Generic guess
    return f"smtp.{domain}"


def send_email_smtp(to_email: str, subject: str, body: str) -> bool:
    host = _get_env_any([
        "SMTP_HOST", "EMAIL_HOST", "SMTP_SERVER", "MAIL_SERVER"
    ])
    port = int(_get_env_any([
        "SMTP_PORT", "EMAIL_PORT", "MAIL_PORT"
    ], default="587"))
    username = _get_env_any([
        "SMTP_USERNAME", "SMTP_USER", "EMAIL_USERNAME", "EMAIL_USER", "MAIL_USERNAME", "emailuser", "EMAIL", "USER"
    ])
    password = _get_env_any([
        "SMTP_PASSWORD", "SMTP_PASS", "EMAIL_PASSWORD", "EMAIL_PASS", "MAIL_PASSWORD", "pass", "PASS"
    ])
    from_name = _get_env_any([
        "SMTP_FROM_NAME", "EMAIL_FROM_NAME", "MAIL_FROM_NAME", "FROM_NAME"
    ], default="Auto Pitch Agent")
    from_email = _get_env_any([
        "SMTP_FROM", "EMAIL_FROM", "FROM_EMAIL", "SENDER_EMAIL", "MAIL_FROM"
    ], default=username or "")
    use_tls = _get_env_any([
        "SMTP_USE_TLS", "SMTP_TLS", "EMAIL_USE_TLS", "MAIL_USE_TLS"
    ], default="true").lower() != "false"

    # Infer host if missing but from_email is known
    if not host and from_email:
        inferred = _infer_smtp_host(from_email)
        if inferred:
            print(f"ℹ️ Using inferred SMTP host: {inferred}")
            host = inferred

    if not host or not from_email:
        print("❌ Missing SMTP_HOST or SMTP_FROM/SMTP_USERNAME in environment.")
        return False
    if not _valid_email(to_email):
        print(f"⚠️ Skipping invalid email: {to_email}")
        return False

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr((from_name, from_email))
    msg["To"] = to_email

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            if use_tls:
                server.starttls()
            if username and password:
                server.login(username, password)
            server.sendmail(from_email, [to_email], msg.as_string())
        return True
    except Exception as e:
        print(f"❌ SMTP send failed to {to_email}: {e}")
        return False


def send_personalized_emails(
    company_summary: str,
    matches_df: pd.DataFrame,
    founder_name: Optional[str] = None,
    company_name: Optional[str] = None,
    dry_run: bool = False,
    email_column: Optional[str] = None,
    on_log: Optional[Callable[[str], None]] = None,
    on_progress: Optional[Callable[[int, int], None]] = None,
) -> None:
    def log(message: str) -> None:
        try:
            if on_log is not None:
                on_log(message)
        finally:
            print(message)

    # Identify email column if present
    email_col = None
    if email_column and email_column in matches_df.columns:
        email_col = email_column
    else:
        for candidate in ["Email", "email", "Email Address", "Investor Email", "Contact Email"]:
            if candidate in matches_df.columns:
                email_col = candidate
                break

    if email_col is None:
        log("⚠️ No email column found in matches; skipping email sending.")
        return

    sent_count = 0
    total_rows = len(matches_df)
    for idx, (_, row) in enumerate(matches_df.iterrows(), start=1):
        if on_progress is not None:
            try:
                on_progress(idx - 1, total_rows)
            except Exception:
                pass
        investor_name = str(row.get("Investor name", "Investor")).strip()
        investor_website = str(row.get("Website", "")).strip()
        investor_thesis = str(row.get("Final Investment thesis", "")).strip()
        to_email = str(row.get(email_col, "")).strip()

        if not _valid_email(to_email):
            log(f"⚠️ Skipping {investor_name}: invalid email '{to_email}'.")
            continue

        subject, body = generate_personalized_email(
            company_summary=company_summary,
            investor_name=investor_name,
            investor_website=investor_website,
            investor_thesis=investor_thesis or None,
            founder_name=founder_name or os.getenv("FOUNDER_NAME"),
            company_name=company_name or os.getenv("COMPANY_NAME"),
        )

        if not subject or not body:
            log(f"⚠️ Skipping {investor_name}: failed to generate email content.")
            continue

        if dry_run:
            preview = body if len(body) < 300 else body[:300] + "..."
            log(f"\n--- DRY RUN: {investor_name} <{to_email}> ---\nSubject: {subject}\n{preview}")
            continue

        ok = send_email_smtp(to_email, subject, body)
        if ok:
            sent_count += 1
            log(f"✅ Sent to {investor_name} <{to_email}>")
        else:
            log(f"❌ Failed to send to {investor_name} <{to_email}>")

    if not dry_run:
        log(f"\n📨 Done. Sent {sent_count} emails.")
    if on_progress is not None:
        try:
            on_progress(total_rows, total_rows)
        except Exception:
            pass


