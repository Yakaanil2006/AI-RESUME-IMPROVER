import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os
import re

# ------------------ CONFIG ------------------
API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

st.set_page_config(
    page_title="ResumePro AI | Elite",
    page_icon="🚀",
    layout="wide"
)

# ------------------ PREMIUM UI ------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

.stApp {
    background: #0b0f1a;
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
}

/* Glass Layout */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(23, 32, 53, 0.8) !important;
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 2.5rem;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
}

/* Hero */
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
}
.hero-accent {
    background: linear-gradient(90deg, #6366f1, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Cards */
.glass-card {
    background: rgba(255,255,255,0.04);
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 24px;
    text-align: center;
}

/* Score */
.score-text {
    font-size: 4.8rem;
    font-weight: 800;
}

/* Insight Blocks */
.insight-block {
    background: rgba(255,255,255,0.035);
    border-left: 4px solid #6366f1;
    border-radius: 14px;
    padding: 22px 26px;
    margin-bottom: 24px;
}
.insight-title {
    font-weight: 700;
    margin-bottom: 10px;
}

/* Button */
.stButton > button {
    background: #6366f1;
    color: white;
    font-weight: 700;
    border-radius: 10px;
    padding: 0.9rem;
    width: 100%;
}
.stButton > button:hover {
    background: #4f46e5;
}

/* Inputs */
.stTextArea textarea {
    background: rgba(15,23,42,0.95);
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ------------------ HELPERS ------------------
def extract_text_from_pdf(uploaded_file):
    try:
        text = ""
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return None

def get_ai_analysis(resume_text, job_desc):
    try:
        model = genai.GenerativeModel("gemma-3-12b")
        prompt = f"""
Role: Senior Technical Recruiter
Task: Analyze resume vs job description.

STRICT FORMAT:
MATCH_SCORE: [0-100]
---
### 📊 Match Breakdown
Summary of suitability.

### 🎯 Keyword Gaps
Missing technical & soft skills.

### 🚀 Optimization Steps
Actionable improvements.

Resume:
{resume_text}

Job Description:
{job_desc}
"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"MATCH_SCORE: 0\n\nError: {e}"

# ------------------ HEADER ------------------
st.markdown(
    '<div class="hero-title">ResumePro <span class="hero-accent">AI</span></div>',
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;color:#94a3b8;margin-bottom:3rem;'>Elite ATS Analysis & Resume Optimization</p>",
    unsafe_allow_html=True
)

# ------------------ LAYOUT ------------------
col_input, col_output = st.columns([1, 1.2], gap="large")

with col_input:
    st.markdown("### 🛠️ Analysis Input")
    resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    job_text = st.text_area("Target Job Description", height=300)

    if st.button("Start Analysis 🚀"):
        if resume_file and job_text:
            with st.spinner("Analyzing resume alignment..."):
                text = extract_text_from_pdf(resume_file)
                if text:
                    st.session_state["report"] = get_ai_analysis(text, job_text)
        else:
            st.warning("Please upload a resume and job description.")

with col_output:
    if "report" in st.session_state:
        report = st.session_state["report"]

        score_match = re.search(r"MATCH_SCORE:\s*(\d+)", report)
        score = int(score_match.group(1)) if score_match else 0

        label = (
            "Excellent Match" if score > 75 else
            "Moderate Match" if score > 50 else
            "Low Match"
        )
        color = "#10b981" if score > 75 else "#f59e0b" if score > 50 else "#ef4444"

        clean_report = re.sub(r"MATCH_SCORE:\s*\d+", "", report).replace("---", "").strip()

        # Score Card
        st.markdown(f"""
        <div class="glass-card">
            <div style="letter-spacing:2px;font-size:0.75rem;color:#94a3b8;">
                ATS COMPATIBILITY SCORE
            </div>
            <div class="score-text" style="color:{color};">{score}%</div>
            <div style="font-weight:600;color:{color};">{label}</div>

            <div style="margin-top:18px;background:rgba(255,255,255,0.08);
                        height:10px;border-radius:10px;overflow:hidden;">
                <div style="width:{score}%;
                            height:100%;
                            background:linear-gradient(90deg,{color},#ffffff22);
                            transition:width 1.2s ease;">
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Styled Sections
        clean_report = clean_report.replace(
            "### 📊 Match Breakdown",
            "<div class='insight-block'><div class='insight-title'>📊 Match Breakdown</div>"
        ).replace(
            "### 🎯 Keyword Gaps",
            "</div><div class='insight-block'><div class='insight-title'>🎯 Keyword Gaps</div>"
        ).replace(
            "### 🚀 Optimization Steps",
            "</div><div class='insight-block'><div class='insight-title'>🚀 Optimization Steps</div>"
        ) + "</div>"

        st.markdown(clean_report, unsafe_allow_html=True)

        st.download_button(
            "📄 Export Optimization Report",
            clean_report,
            "Resume_Optimization_Report.md",
            "text/markdown"
        )

    else:
        st.markdown("""
        <div style="text-align:center;padding:80px;">
            <div style="font-size:2.4rem;">🚀</div>
            <p style="font-size:1.15rem;font-weight:600;color:#94a3b8;">
                Upload a resume and job description
            </p>
            <p style="color:#475569;">
                Get ATS score, keyword gaps, and optimization steps instantly
            </p>
        </div>
        """, unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-size:0.75rem;color:#475569;'>"
    "Powered by AI • 2025"
    "</div>",
    unsafe_allow_html=True
)
