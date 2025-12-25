import streamlit as st
import fitz
import google.generativeai as genai
import os
import re

# ------------------ CONFIG ------------------
API_KEY = os.getenv("GOOGLE_API_KEY")  # DO NOT hardcode in production
genai.configure(api_key=API_KEY)

st.set_page_config(
    page_title="ResumePro AI",
    page_icon="💎",
    layout="wide"
)

# ------------------ REFINED DARK GLASS UI ------------------
st.markdown("""
<style>

/* Global */
.stApp {
    background-color: #0b1020;
    color: #f8fafc;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Hero */
.hero {
    text-align: center;
    padding: 3rem 0 2rem 0;
}
.hero h1 {
    font-size: 3.4rem;
    font-weight: 800;
    color: #f8fafc;
}
.hero p {
    font-size: 1.1rem;
    color: #94a3b8;
}

/* Glass Card */
.glass-card {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    margin-bottom: 2rem;
}

/* Buttons */
.stButton > button {
    background-color: #3b82f6 !important;
    color: white !important;
    border-radius: 12px !important;
    height: 3.2em !important;
    font-weight: 600 !important;
    border: none !important;
}
.stButton > button:hover {
    background-color: #2563eb !important;
}

/* Inputs */
textarea,
[data-testid="stFileUploader"] {
    background-color: rgba(255,255,255,0.05) !important;
    color: #f8fafc !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
}

/* Score */
.score {
    font-size: 3rem;
    font-weight: 800;
    color: #22c55e;
    text-align: center;
    margin-top: 0.5rem;
}

.muted {
    color: #94a3b8;
}

/* Footer */
.footer {
    text-align: center;
    color: #64748b;
    padding: 2rem;
    font-size: 0.85rem;
}

</style>
""", unsafe_allow_html=True)

# ------------------ FUNCTIONS ------------------
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


def get_ai_suggestions(resume_text, job_description):
    model = genai.GenerativeModel("gemini-3-flash-preview")

    prompt = f"""
You are a professional ATS Resume Analyst.

Return strictly in this format:

MATCH_SCORE: <0-100>
ANALYSIS:
- Summary feedback

IMPROVEMENTS:
- STAR-based bullet points

KEYWORDS:
- Missing skills list

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description if job_description else "General optimization"}
"""

    response = model.generate_content(prompt)
    return response.text

# ------------------ UI ------------------
st.markdown("""
<div class="hero">
    <h1>ResumePro AI</h1>
    <p>Clean. Professional. ATS-Optimized.</p>
</div>
""", unsafe_allow_html=True)

col_l, col_r = st.columns([1, 1.2], gap="large")

with col_l:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📄 Upload Resume")

    uploaded_file = st.file_uploader("PDF Resume", type="pdf")
    job_desc = st.text_area("Job Description", height=220, placeholder="Paste target role here...")

    run = st.button("Analyze Resume")
    st.markdown('</div>', unsafe_allow_html=True)

with col_r:
    if run and uploaded_file:
        with st.spinner("Analyzing with Gemini AI..."):
            text = extract_text_from_pdf(uploaded_file)
            if text:
                result = get_ai_suggestions(text, job_desc)

                score_match = re.search(r"MATCH_SCORE:\s*(\d+)", result)
                score = int(score_match.group(1)) if score_match else 0

                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.subheader("🎯 ATS Match Score")
                st.progress(score / 100)
                st.markdown(f"<div class='score'>{score}%</div>", unsafe_allow_html=True)

                st.subheader("💡 AI Feedback")
                st.markdown(result)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='glass-card' style='text-align:center;'>"
            "<p class='muted'>Upload a resume to begin analysis.</p></div>",
            unsafe_allow_html=True
        )

# ------------------ FOOTER ------------------
st.markdown("""
<div class="footer">
    ResumePro AI • Built with Streamlit & Gemini
</div>
""", unsafe_allow_html=True)
