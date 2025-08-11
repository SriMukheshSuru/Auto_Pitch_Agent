# Auto_Pitch_Agent

Project Title:
AI-Powered Investor Outreach Automation

Description:
This project automates the process of identifying relevant investors for a startup and sending personalized cold emails using Google Gemini (via LangChain) and a structured investor database.

The workflow is built with LangGraph and consists of four main steps:

Company Profiling – Takes a startup name as input and uses Gemini to generate a concise description including its primary domain.

Investor Matching – Compares the company’s domain with a preloaded CSV of investors. Gemini is used to reason over investor domains and identify the most relevant ones. A custom text normalization process ensures robust matching, even when domain names vary in case, spacing, or punctuation.

Email Drafting – Automatically generates a personalized cold outreach email to potential investors using the company’s profile.

Automated Email Sending – Sends the email to all matched investors via SMTP, with safeguards to avoid sending to placeholder or invalid addresses.

Key Features:

Natural Language Understanding: Uses Gemini to interpret the startup’s industry and domain.

Flexible Domain Matching: Handles variations in domain naming (e.g., “Data Science & AI” vs. “datascience and ai”).

LangGraph Workflow: Modular, state-driven pipeline for smooth execution from profiling to outreach.

Automated Outreach: Generates and sends investor-specific cold emails without manual intervention.

Tech Stack:

Python

LangChain + Google Gemini API

LangGraph for workflow orchestration

Pandas for data handling

SMTP for email sending

dotenv for secure environment variable management

Use Case:
Startups can use this tool to quickly identify the right investors based on their business domain and initiate contact with a professionally drafted cold email — saving hours of manual research and outreach effort.
