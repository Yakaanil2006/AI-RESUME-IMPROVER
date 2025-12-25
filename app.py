import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os
import re

# ------------------ CONFIG ------------------
# It's better to use st.secrets for Streamlit Cloud or .env locally
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

    /* Global Overrides */
    .stApp {
        background: radial-gradient(circle at top left, #1e293b, #0f172a);
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphism Card Effect */
    .custom-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
    }

    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 3rem 0;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(to right, #3b82f6, #2dd4bf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.2rem;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%) !important;
        border: none !important;
        padding: 0.75rem 1rem !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
    }

    /* Score Display */
    .score-circle {
        background: rgba(34, 197, 94, 0.1);
        border: 2px solid #22c55e;
        border-radius: 50%;
        width: 120px;
        height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        font-size: 2.2rem;
        font-weight: 800;
        color: #22c55e;
    }

    /* Horizontal Rule */
    hr {
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        margin: 2rem 0;
    }

    /* Sidebar/Footer */
    .footer {
        text-align: center;
        padding: 4rem 0 2rem;
        color: #64748b;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ LOGIC ------------------
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

def get_ai_suggestions(resume_text, job_description):
    model = genai.GenerativeModel("gemini-1.5-flash") # Updated to 1.5 Flash
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) consultant. 
    Analyze the resume against the job description.
    
    Format the response exactly like this:
    MATCH_SCORE: <number between 0-100>
    
    ### 📝 Executive Summary
    <Short summary of alignment>
    
    ### 🚀 Top Improvements
    <3-4 bullet points using STAR method>
    
    ### 🔑 Missing Keywords
    <Comma separated list of keywords>
    
    RESUME: {resume_text}
    JOB DESCRIPTION: {job_description}
    """
    response = model.generate_content(prompt)
    return response.text

# ------------------ UI LAYOUT ------------------

# Header
st.markdown("""
<div class="hero-container">
    <div class="hero-title">ResumePro AI</div>
    <div class="hero-subtitle">Optimize your career path with Generative Intelligence</div>
</div>
""", unsafe_allow_html=True)

# Main Body
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("📤 Input Details")
    
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf", help="Your data is processed locally and never stored.")
    
    job_desc = st.text_area(
        "Paste Job Description",
        height=250,
        placeholder="Copy and paste the job requirements here for a tailored analysis..."
    )
    
    analyze_btn = st.button("Analyze Alignment")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if analyze_btn and uploaded_file:
        with st.spinner("🧠 AI is analyzing your profile..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            
            if resume_text:
                raw_result = get_ai_suggestions(resume_text, job_desc)
                
                # Parsing Score
                score_match = re.search(r"MATCH_SCORE:\s*(\d+)", raw_result)
                score = int(score_match.group(1)) if score_match else 0
                
                # Clean result text for display
                display_text = re.sub(r"MATCH_SCORE:\s*\d+", "", raw_result).strip()

                st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                st.markdown("<h3 style='text-align: center;'>Analysis Result</h3>", unsafe_allow_html=True)
                
                # Visual Score Circle
                st.markdown(f"""
                    <div class="score-circle">{score}%</div>
                    <p style='text-align: center; color: #94a3b8; margin-top: 10px;'>Match Accuracy</p>
                """, unsafe_allow_html=True)
                
                st.progress(score / 100)
                
                st.markdown("---")
                st.markdown(display_text)
                st.markdown('</div>', unsafe_allow_html=True)
    
    elif not analyze_btn:
        st.markdown("""
            <div style="text-align: center; padding: 5rem 2rem; border: 2px dashed rgba(255,255,255,0.1); border-radius: 20px;">
                <h2 style="color: #475569;">Ready for Analysis</h2>
                <p style="color: #64748b;">Fill in the details on the left to unlock your resume score and insights.</p>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">Built with Streamlit• Precision Recruitment Analysis</div>', unsafe_allow_html=True)
