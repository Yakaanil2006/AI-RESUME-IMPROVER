import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os
import re

# ------------------ CONFIG ------------------
API_KEY = os.getenv("GOOGLE_API_KEY")  # Set in Streamlit Secrets
genai.configure(api_key=API_KEY)

st.set_page_config(
    page_title="ResumePro AI",
    page_icon="💎",
    layout="wide"
)

# ------------------ CLEAN & USER-FRIENDLY UI ------------------
st.markdown("""
<style>

/* Global */
.stApp {
    background-color: #0f172a;
    color: #e5e7eb;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Hero */
.hero {
    text-align: center;
    padding: 2.5rem 0 2rem 0;
}
.hero h1 {
    font-size: 3rem;
    font-weight: 700;
    color: #f8fafc;
}
.hero p {
    font-size: 1.05rem;
    color: #9ca3af;
}

/* Card */
.card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 16px;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
}

/* Buttons */
.stButton > button {
    background-color: #2563eb !important;
    color: white !important;
    border-radius: 10px !important;
    height: 3em !important;
    font-weight: 600 !important;
    border: none !important;
}
.stButton > button:hover {
    background-color: #1d4ed8 !important;
}

/* Inputs */
textarea,
[data-testid="stFileUploader"] {
    background-color: #020617 !important;
    color: #e5e7eb !important;
    border-radius: 10px !important;
    border: 1px solid #1f2937 !important;
}

/* Score */
.score {
    font-size: 2.6rem;
    font-weight: 700;
    color: #22c55e;
    text-align: center;
    margin-top: 0.5rem;
}

/* Muted */
.muted {
    color: #9ca3af;
}

/* Footer */
.footer {
    text-align: center;
    color: #6b7280;
    padding: 2rem 0;
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
- Short summary feedback

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

# Hero
st.markdown("""
<div class="hero">
    <h1>ResumePro AI</h1>
    <p>Check how well your resume matches a job description</p>
</div>
""", unsafe_allow_html=True)

col_l, col_r = st.columns([1, 1.2], gap="large")

# -------- LEFT COLUMN (INPUT) --------
with col_l:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📄 Upload Your Resume")
    st.caption("PDF format only • No data is stored")

    uploaded_file = st.file_uploader("Resume (PDF)", type="pdf")
    job_desc = st.text_area(
        "Job Description (Optional but recommended)",
        height=220,
        placeholder="Paste the job description here..."
    )

    run = st.button("Analyze Resume")
    st.markdown('</div>', unsafe_allow_html=True)

# -------- RIGHT COLUMN (RESULT – ONLY WHEN READY) --------
if run and uploaded_file:
    with col_r:
        with st.spinner("Analyzing your resume..."):
            resume_text = extract_text_from_pdf(uploaded_file)

            if resume_text:
                result = get_ai_suggestions(resume_text, job_desc)

                score_match = re.search(r"MATCH_SCORE:\s*(\d+)", result)
                score = int(score_match.group(1)) if score_match else 0

                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("🎯 Resume Match Score")
                st.progress(score / 100)
                st.markdown(f"<div class='score'>{score}%</div>", unsafe_allow_html=True)

                st.markdown("---")
                st.subheader("💡 Improvement Suggestions")
                st.markdown(result)

                st.markdown('</div>', unsafe_allow_html=True)

elif run and not uploaded_file:
    st.warning("Please upload a resume first.")

else:
    st.markdown(
        "<p class='muted' style='text-align:center;'>Upload your resume and click Analyze to see results</p>",
        unsafe_allow_html=True
    )

# ------------------ FOOTER ------------------
st.markdown("""
<div class="footer">
    ResumePro AI • Built with Streamlit & Gemini
</div>
""", unsafe_allow_html=True)


