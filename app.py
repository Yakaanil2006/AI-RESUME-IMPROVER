import streamlit as st
import fitz
import google.generativeai as genai
import os
import re

# ------------------ CONFIG ------------------
API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

st.set_page_config(
    page_title="ResumeLens |",
    page_icon="🚀",
    layout="wide"
)

# ------------------ GLASS + LOGO CSS ------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

@keyframes glow {
  0% { text-shadow: 0 0 10px rgba(99,102,241,0.4); }
  50% { text-shadow: 0 0 25px rgba(168,85,247,0.6); }
  100% { text-shadow: 0 0 10px rgba(99,102,241,0.4); }
}

.stApp {
    background-color: #0f172a;
    background-image:
        radial-gradient(at 0% 0%, rgba(99,102,241,0.15), transparent 50%),
        radial-gradient(at 100% 0%, rgba(168,85,247,0.15), transparent 50%),
        radial-gradient(at 100% 100%, rgba(236,72,153,0.1), transparent 50%),
        radial-gradient(at 0% 100%, rgba(45,212,191,0.1), transparent 50%);
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #f1f5f9;
}

/* Glass Containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(12px) saturate(180%);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
}

/* Logo */
.logo-wrap {
    text-align: center;
}
.logo-text {
    font-size: 3.8rem;
    font-weight: 800;
    letter-spacing: -1.5px;
    background: linear-gradient(90deg, #ffffff, #c7d2fe, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: glow 4s ease-in-out infinite;
}
.logo-badge {
    margin-left: 8px;
    padding: 6px 14px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 2px;
    color: #a5b4fc;
    border: 1px solid rgba(129,140,248,0.4);
    border-radius: 999px;
    background: rgba(99,102,241,0.15);
}
.logo-subtitle {
    text-align: center;
    font-size: 0.85rem;
    letter-spacing: 3px;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 3rem;
}

/* Cards */
.glass-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 25px;
    text-align: center;
    margin-bottom: 20px;
}

.score-text {
    font-size: 4.5rem;
    font-weight: 800;
}

/* Buttons */
.stButton > button {
    background: rgba(99,102,241,0.25);
    border: 1px solid rgba(255,255,255,0.25);
    color: white;
    border-radius: 12px;
    padding: 0.6rem 2rem;
    font-weight: 600;
    transition: 0.3s ease;
}
.stButton > button:hover {
    background: rgba(99,102,241,0.45);
    transform: translateY(-2px);
}

/* Inputs */
.stTextArea textarea {
    background: rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.15);
    color: white;
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
Act as a recruiter. Analyze resume vs job description.

FORMAT STRICTLY:
MATCH_SCORE: [0-100]
---
### 💎 Executive Summary
Concise recruiter verdict.

### 🔥 Missing Critical Keywords
JD keywords absent in resume.

### 🛠️ Recommended Actions
Clear ATS optimization steps.

Resume:
{resume_text}

Job Description:
{job_desc}
"""
        return model.generate_content(prompt).text
    except Exception as e:
        return f"MATCH_SCORE: 0\n\nError: {e}"

# ------------------ HEADER ------------------
st.markdown("""
<div class="logo-wrap">
    <span class="logo-text">ResumeLens</span>
</div>
<div class="logo-subtitle">SEE YOUR RESUME THROUGH A RECRUITER’S LENS</div>
""", unsafe_allow_html=True)

# ------------------ LAYOUT ------------------
left, right = st.columns([1, 1.2], gap="large")

with left:
    st.markdown("### 📥 Source Files")
    resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    job_text = st.text_area("Job Description", height=260, placeholder="Paste job requirements...")
    analyze = st.button("Generate AI Audit", use_container_width=True)

    # Alerts
    if analyze:
        if not resume_file and not job_text.strip():
            st.toast("📄 Upload resume and paste job description", icon="⚠️")
        elif not resume_file:
            st.toast("📄 Please upload your resume (PDF)", icon="⚠️")
        elif not job_text.strip():
            st.toast("📝 Please paste the job description", icon="⚠️")

with right:
    if analyze and resume_file and job_text.strip():
        with st.spinner("Refining insights..."):
            resume_text = extract_text_from_pdf(resume_file)
            if resume_text:
                report = get_ai_analysis(resume_text, job_text)

                score_match = re.search(r"MATCH_SCORE:\s*(\d+)", report)
                score = int(score_match.group(1)) if score_match else 0
                clean_report = re.sub(r"MATCH_SCORE:\s*\d+", "", report).replace("---", "").strip()

                color = "#22c55e" if score > 75 else "#f59e0b" if score > 50 else "#ef4444"

                st.markdown(f"""
                <div class="glass-card">
                    <div style="color:#94a3b8;font-size:0.85rem;font-weight:600;">
                        MATCH ACCURACY
                    </div>
                    <div class="score-text" style="color:{color};">{score}%</div>
                    <div style="width:100%;height:12px;background:rgba(255,255,255,0.08);
                                border-radius:20px;">
                        <div style="width:{score}%;height:100%;background:{color};
                                    border-radius:20px;box-shadow:0 0 16px {color}66;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(clean_report)

                st.download_button(
                    "Download Report (.md)",
                    clean_report,
                    "ResumeLens_Report.md",
                    "text/markdown",
                    use_container_width=True
                )
    else:
        st.markdown("""
        <div style="border:1px dashed rgba(255,255,255,0.2);
                    border-radius:24px;
                    padding:5rem 2rem;
                    text-align:center;
                    background:rgba(255,255,255,0.02);">
            <div style="font-size:3rem;">💎</div>
            <h4 style="color:#64748b;">Ready to Analyze</h4>
            <p style="color:#475569;font-size:0.9rem;">
                Upload your resume and job description to begin
            </p>
        </div>
        """, unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown(
    "<div style='text-align:center;padding:2rem;color:#475569;font-size:0.75rem;'>"
    "ResumeLens • 2025"
    "</div>",
    unsafe_allow_html=True
)

