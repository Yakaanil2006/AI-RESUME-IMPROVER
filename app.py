import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os
import re

# ------------------ CONFIG ------------------
# prioritize st.secrets for deployment, fallback to environment variables
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

    /* Global Body Styling */
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
        padding: 2rem;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        margin-bottom: 2rem;
    }

    /* Hero Branding */
    .hero-container {
        text-align: center;
        padding: 3rem 0;
    }
    .hero-title {
        font-size: 3.8rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #3b82f6, #2dd4bf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 300;
    }

    /* Custom Button Design */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
    }

    /* Matching Score Badge */
    .score-badge {
        background: rgba(34, 197, 94, 0.15);
        border: 2px solid #22c55e;
        border-radius: 50%;
        width: 110px;
        height: 110px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 1.5rem auto;
        color: #22c55e;
    }
    .score-val { font-size: 2rem; font-weight: 800; }
    .score-lab { font-size: 0.7rem; text-transform: uppercase; opacity: 0.8; }

    /* Clean Footer */
    .footer {
        text-align: center;
        padding: 3rem 0;
        color: #475569;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ UTILITIES ------------------
def extract_text_from_pdf(uploaded_file):
    try:
        text = ""
        # stream=uploaded_file.read() reads the bytes from Streamlit uploader
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return None

def get_ai_analysis(resume_text, job_description):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) and Career Coach.
    Analyze the resume against the provided job description.
    
    Format the response exactly like this:
    MATCH_SCORE: <0-100>

    ### 📝 Summary
    <A brief professional overview of the match>

    ### 🚀 Key Improvements
    - Use STAR method (Situation, Task, Action, Result) for bullet points.
    - Specific phrasing changes.

    ### 🔑 Target Keywords
    - Missing technical skills or industry terms.

    RESUME: {resume_text}
    JOB DESCRIPTION: {job_description if job_description else "General professional improvement"}
    """
    response = model.generate_content(prompt)
    return response.text

# ------------------ UI LAYOUT ------------------

# 1. Header Section
st.markdown("""
<div class="hero-container">
    <div class="hero-title">ResumePro AI</div>
    <div class="hero-subtitle">Instant ATS Optimization & AI Insights</div>
</div>
""", unsafe_allow_html=True)

# 2. Main Interaction Area
col_input, col_result = st.columns([1, 1], gap="large")

with col_input:
    # Opening the card container
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>📤 Upload & Analyze</h3>", unsafe_allow_html=True)
    
    resume_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
    
    job_text = st.text_area(
        "Paste Job Description",
        height=280,
        placeholder="Paste the target job description here for specific matching..."
    )
    
    analyze_click = st.button("Generate Report")
    
    # Closing the card container
    st.markdown('</div>', unsafe_allow_html=True)

with col_result:
    if analyze_click and resume_file:
        with st.spinner("⚡ Processing Analysis..."):
            extracted_text = extract_text_from_pdf(resume_file)
            
            if extracted_text:
                raw_analysis = get_ai_analysis(extracted_text, job_text)
                
                # Extract Score
                score_match = re.search(r"MATCH_SCORE:\s*(\d+)", raw_analysis)
                score_val = int(score_match.group(1)) if score_match else 0
                
                # Strip score from the display text
                clean_report = re.sub(r"MATCH_SCORE:\s*\d+", "", raw_analysis).strip()

                st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                st.markdown("<h3 style='text-align: center; margin-top:0;'>📊 AI Analysis Report</h3>", unsafe_allow_html=True)
                
                # Score Badge Visualization
                st.markdown(f"""
                    <div class="score-badge">
                        <span class="score-val">{score_val}%</span>
                        <span class="score-lab">Match</span>
                    </div>
                """, unsafe_allow_html=True)
                
                st.progress(score_val / 100)
                
                st.markdown("---")
                st.markdown(clean_report)
                st.markdown('</div>', unsafe_allow_html=True)
    
    elif not analyze_click:
        # Instruction State
        st.markdown("""
            <div style="text-align: center; padding: 6rem 2rem; border: 2px dashed rgba(255,255,255,0.1); border-radius: 20px;">
                <h3 style="color: #64748b;">Awaiting Input</h3>
                <p style="color: #475569;">Upload your resume to receive AI-powered feedback and keyword analysis.</p>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">Built with Streamlit• Precision Recruitment Analysis</div>', unsafe_allow_html=True)

