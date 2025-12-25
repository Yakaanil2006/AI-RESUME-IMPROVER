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
    page_title="ResumePro AI",
    page_icon="💎",
    layout="wide"
)

# ------------------ ENHANCED CSS ------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    .stApp {
        background: radial-gradient(circle at top left, #1e293b, #0f172a);
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }

    /* Modern Glass Card */
    .custom-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }

    /* Hero Branding */
    .hero-container {
        text-align: center;
        padding: 2rem 0;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3b82f6, #2dd4bf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }

    /* Fixing Input Spacing */
    .stTextArea textarea {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }

    /* Button Styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: 0.3s;
    }
    
    /* Score Visual */
    .score-badge {
        background: rgba(34, 197, 94, 0.1);
        border: 2px solid #22c55e;
        border-radius: 50%;
        width: 100px;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 1rem auto;
        color: #22c55e;
        font-size: 1.8rem;
        font-weight: 800;
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
        st.error(f"Error: {e}")
        return None

def get_ai_analysis(resume_text, job_desc):
    model = genai.GenerativeModel("gemini-3-flash-preview")
    prompt = f"Analyze this resume against the job description. Provide a MATCH_SCORE: (0-100) and then sections for Summary, Improvements (STAR method), and Missing Keywords. \nResume: {resume_text}\nJob: {job_desc}"
    response = model.generate_content(prompt)
    return response.text

# ------------------ UI LAYOUT ------------------

st.markdown("""
<div class="hero-container">
    <div class="hero-title">ResumePro AI</div>
    <p style="color: #94a3b8;">Optimize your career path with Generative Intelligence</p>
</div>
""", unsafe_allow_html=True)

col_input, col_result = st.columns([1, 1], gap="large")

with col_input:
    # Everything inside this container is part of the "Input Card"
    with st.container(border=True):
        st.markdown("<h3 style='margin-top:0;'>📥 Input Details</h3>", unsafe_allow_html=True)
        
        resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        
        job_text = st.text_area(
            "Paste Job Description",
            height=250,
            placeholder="Copy and paste requirements here..."
        )
        
        analyze_btn = st.button("Analyze Alignment")

with col_result:
    if analyze_btn and resume_file:
        with st.spinner("Analyzing..."):
            text = extract_text_from_pdf(resume_file)
            if text:
                report = get_ai_analysis(text, job_text)
                
                # Extract Score
                score_match = re.search(r"MATCH_SCORE:\s*(\d+)", report)
                score = int(score_match.group(1)) if score_match else 0
                clean_report = re.sub(r"MATCH_SCORE:\s*\d+", "", report).strip()

                with st.container(border=True):
                    st.markdown("<h3 style='text-align: center;'>Analysis Report</h3>", unsafe_allow_html=True)
                    st.markdown(f'<div class="score-badge">{score}%</div>', unsafe_allow_html=True)
                    st.progress(score / 100)
                    st.markdown("---")
                    st.markdown(clean_report)
    else:
        # Placeholder when no analysis is running
        st.markdown("""
            <div style="text-align: center; padding: 5rem 2rem; border: 2px dashed rgba(255,255,255,0.1); border-radius: 20px;">
                <h3 style="color: #475569;">Ready for Analysis</h3>
                <p style="color: #64748b;">Fill in the details on the left to unlock your insights.</p>
            </div>
        """, unsafe_allow_html=True)

