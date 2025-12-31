# AI-RESUME-IMPROVER

ResumeLens is a high-performance, AI-powered ATS (Applicant Tracking System) resume optimizer that helps job seekers evaluate their resumes the way recruiters do.
It leverages Google Gemini to deliver fast, actionable insights on resume–job description alignment.

✨ Key Features
🎨 Modern Glassmorphic UI

A sleek, dark-themed interface built with custom CSS for a premium and intuitive user experience.

🤖 AI-Powered Resume Audit

Uses the Gemma-3-27B-IT (Gemini) model to analyze semantic alignment between your resume and the target job description.

📊 Visual Match Score

Instant feedback with a color-coded percentage bar that clearly shows how well your resume matches the role.

🔍 Keyword Gap Analysis

Automatically detects missing or weak keywords commonly used by recruiters and ATS systems.

🧠 Executive Summary

A concise “recruiter-style verdict” summarizing your suitability for the role.

📄 PDF Resume Processing

Accurate text extraction from PDF resumes using PyMuPDF.

📥 Downloadable Reports

Export your AI audit results as a clean .txt report for offline review and iteration.

🛠️ Installation & Setup
1️⃣ Prerequisites

Python 3.9+

Pip package manager

2️⃣ Clone the Repository
git clone https://github.com/yourusername/resumelens.git
cd resumelens

3️⃣ Install Dependencies
pip install streamlit pymupdf google-generativeai

4️⃣ Configure Google Gemini API Key

You’ll need a Google Gemini API key from Google AI Studio.

Option A — Environment Variable

export GOOGLE_API_KEY="your_api_key_here"


Option B — Streamlit Secrets
Create a .streamlit/secrets.toml file:

GOOGLE_API_KEY = "your_api_key_here"

5️⃣ Run the Application
streamlit run app.py

📖 How to Use

Upload Resume – Upload your resume in PDF format

Paste Job Description – Add the target job requirements

Generate AI Audit – Let the model analyze your profile

Review Results – Check match score, gaps, and summary

Download Report – Use the insights to improve your resume

📦 Project Structure
├── app.py              # Main Streamlit application
├── requirements.txt    # Project dependencies
├── .streamlit/         # Secrets & configuration (optional)
└── README.md           # Documentation
