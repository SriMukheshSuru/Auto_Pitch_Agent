# 🚀 Auto_Pitch_Agent

**Automate your investor outreach with AI-powered precision.**

Auto_Pitch_Agent streamlines the process of **identifying relevant investors** for a startup and sending **personalized cold emails** — all in a single automated pipeline powered by **Google Gemini**, **LangChain**, and **LangGraph**.

---

## 📌 Overview

Manual investor research and cold emailing can be **time-consuming** and **error-prone**.  
Auto_Pitch_Agent solves this by automating the **entire process**:

1. **Company Profiling** → Generate a concise startup profile, including its **primary domain**.
2. **Investor Matching** → Identify investors whose domains align with your startup.
3. **Email Drafting** → Create **personalized outreach emails** for each investor.
4. **Automated Email Sending** → Deliver professional emails directly to investor inboxes.

---

## ✨ Key Features

- **🧠 Natural Language Understanding**  
  Uses **Google Gemini** to interpret a startup's **industry** and **domain**.
  
- **🔍 Flexible Domain Matching**  
  Robust matching with **text normalization** to handle variations:  
  `"Data Science & AI"` ↔ `"datascience and ai"`

- **⚙ Modular LangGraph Workflow**  
  State-driven execution ensures **smooth orchestration** from profiling to outreach.

- **📧 Automated Email Outreach**  
  Sends **investor-specific cold emails** via SMTP with safety checks for invalid/placeholder emails.

---

## 🛠 Tech Stack

- **Language & Orchestration**
  - Python
  - [LangChain](https://www.langchain.com/) + [Google Gemini API](https://ai.google.dev/)
  - [LangGraph](https://www.langchain.com/langgraph)

- **Data Handling**
  - Pandas

- **Email Sending**
  - SMTP

- **Security**
  - dotenv for environment variable management

---

## 🗂 Workflow

```mermaid
flowchart TD
    A[Startup Name Input] --> B[Company Profiling]
    B --> C[Investor Matching]
    C --> D[Email Drafting]
    D --> E[Automated Email Sending]
