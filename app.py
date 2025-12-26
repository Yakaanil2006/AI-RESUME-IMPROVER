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

# ------------------ CLEAN & HIGH-VISIBILITY UI ------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    /* Clean Dark Slate Background */
    .stApp {
        background: #0b0f1a;
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }

    /* High-Visibility Glass Container */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(23, 32, 53, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 20px !important;
        padding: 2.5rem !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
    }

    /* Modern Minimalist Header */
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0;
    }
    
    .hero-accent {
        background: linear-gradient(90deg, #6366f1, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Visible Card Effects */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        margin-bottom: 25px;
        transition: border 0.3s ease;
    }
    
    .glass-card:hover {
        border: 1px solid rgba(99, 102, 241, 0.5);
    }

    .score-text {
        font-size: 5rem;
        font-weight: 800;
        margin: 5px 0;
        text-shadow: 0 0 30px rgba(99, 102, 241, 0.3);
    }

    /* Enhanced Button Visibility */
    .stButton > button {
        background: #6366f1 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        width: 100%;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39) !important;
        transition: 0.3s all ease !important;
    }

    .stButton > button:hover {
        background: #4f46e5 !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
    }

    /* Input Focus Visibility */
    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        font-size: 0.95rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
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
        st.error(f"Error reading PDF: {e}")
        return None

def get_ai_analysis(resume_text, job_desc):
    try:
        model = genai.GenerativeModel("gemma-3-12b"
        prompt = f"""
        Role: Senior Recruiter
        Requirement: Analyze the resume against the JD.
        Format response strictly as:
        MATCH_SCORE: [0-100]
        ---
        ### 📊 Match Breakdown
        (Summarize candidate suitability)
        
        ### 🎯 Keyword Gaps
        (List missing technical and soft skills)
        
        ### 🚀 Optimization Steps
        (Bullet points to improve the resume)

        Resume: {resume_text}
        Job Description: {job_desc}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"MATCH_SCORE: 0\n\nError: {str(e)}"

# ------------------ MAIN INTERFACE ------------------

st.markdown('<div class="hero-title">ResumePro <span class="hero-accent">AI</span></div>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color: #94a3b8; margin-bottom: 3rem;'>Elite ATS Analysis & Keyword Optimization</p>", unsafe_allow_html=True)

col_input, col_output = st.columns([1, 1.2], gap="large")

with col_input:
    st.markdown("#### 🛠️ Analysis Input")
    resume_file = st.file_uploader("Upload Professional Resume (PDF)", type=["pdf"])
    job_text = st.text_area("Target Job Description", height=300, placeholder="Paste the job requirements here...")
    
    if st.button("Start Analysis"):
        if resume_file and job_text:
            with st.spinner("Analyzing alignment..."):
                extracted_text = extract_text_from_pdf(resume_file)
                if extracted_text:
                    report = get_ai_analysis(extracted_text, job_text)
                    st.session_state['report'] = report
        else:
            st.warning("Please provide both a resume and a job description.")

with col_output:
    if 'report' in st.session_state:
        report = st.session_state['report']
        score_match = re.search(r"MATCH_SCORE:\s*(\d+)", report)
        score = int(score_match.group(1)) if score_match else 0
        clean_report = re.sub(r"MATCH_SCORE:\s*\d+", "", report).replace("---", "").strip()

        # Score Visual
        color = "#10b981" if score > 75 else "#f59e0b" if score > 50 else "#ef4444"
        
        st.markdown(f"""
        <div class="glass-card">
            <div style="color: #94a3b8; font-size: 0.8rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">Ats Compatibility</div>
            <div class="score-text" style="color: {color};">{score}%</div>
            <div style="width:100%; background:rgba(255,255,255,0.05); height:8px; border-radius:10px; overflow:hidden;">
                <div style="width:{score}%; background:{color}; height:100%; border-radius:10px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(clean_report)
        
        st.download_button(
            label="Export PDF-Ready Insights",
            data=clean_report,
            file_name="Resume_Optimization_Report.md",
            mime="text/markdown"
        )
    else:
        st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 400px; border: 2px dashed rgba(255,255,255,0.05); border-radius: 20px;">
            <p style="color: #475569; font-size: 1.1rem;">Awaiting your files to begin processing...</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div style='text-align:center; color: #334155; font-size: 0.8rem;'>RESUME PRO AI © 2025 •</div>", unsafe_allow_html=True)

