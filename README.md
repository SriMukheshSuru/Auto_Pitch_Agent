# 🚀 Auto_Pitch_Agent

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](#-contributions)
[![Stars](https://img.shields.io/github/stars/your-username/Auto_Pitch_Agent?style=social)](https://github.com/your-username/Auto_Pitch_Agent/stargazers)

> **Automate your investor outreach with AI-powered precision.**  
> Identify the right investors and send **personalized cold emails** in minutes — powered by **Google Gemini** and **LangGraph**.

---

## 📌 Overview

💡 Manual investor research is **slow**. Cold emailing is **repetitive**.  
**Auto_Pitch_Agent** solves both problems with a **fully automated pipeline**:

1️⃣ **Company Profiling** → Generates a startup profile with domain insights.  
2️⃣ **Investor Matching** → Finds investors aligned with your business area.  
3️⃣ **Email Drafting** → Creates highly personalized cold emails.  
4️⃣ **Automated Email Sending** → Sends to relevant investors with validation checks.

---

## ✨ Key Features

| 🚀 Feature | 💡 Description |
|------------|----------------|
| 🧠 **Natural Language Understanding** | Google Gemini interprets the startup's domain & industry. |
| 🔍 **Flexible Domain Matching** | Matches even with variations (`"AI & Data Science"` ↔ `"data science ai"`). |
| ⚙ **LangGraph Workflow** | Modular, state-driven execution for smooth orchestration. |
| 📧 **Automated Outreach** | Sends emails via SMTP, skipping invalid/placeholder addresses. |

---

## 🛠 Tech Stack

**💻 Language & AI**  
- Python 3.9+  
- [Google Gemini API](https://ai.google.dev/)  
- [LangGraph](https://www.langchain.com/langgraph)  

**📊 Data Handling**  
- Pandas  

**📨 Email Automation**  
- SMTP  

**🔐 Security**  
- dotenv for environment variables  

---

## 🗂 Workflow

```mermaid
flowchart TD
    A[Startup Name Input] --> B[Company Profiling via Gemini]
    B --> C[Investor Matching with CSV + Normalization]
    C --> D[Personalized Email Drafting]
    D --> E[Automated Email Sending via SMTP]


