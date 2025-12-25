import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os
import re

# ------------------ CONFIGURATION ------------------
# Get your API key from https://aistudio.google.com/
API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=API_KEY)

st.set_page_config(
    page_title="ResumePro AI 2025",
    page_icon="💎",
    layout="wide"
)

# ------------------ VIBRANT GLASSMORPHIC CSS ------------------
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: radial-gradient(circle at 20% 30%, #4f46e5 0%, transparent 40%),
                    radial-gradient(circle at 80% 70%, #9333ea 0%, transparent 40%),
                    #0f172a;
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }

    /* Hero Section */
    .hero {
        text-align: center;
        padding: 4rem 0 2rem 0;
    }
    .hero h1 {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(to right, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1, #a855f7) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 700 !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(168, 85, 247, 0.4) !important;
    }

    /* Score Badge */
    .score-badge {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        color: #4ade80;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ CORE LOGIC ------------------

def extract_text_from_pdf(uploaded_file):
    """Extracts raw text from PDF bytes."""
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
    """Uses Gemini 3 Flash to generate improvements."""
    # Using the latest Gemini 3 Flash Preview as of Dec 2025
    model = genai.GenerativeModel("gemini-3-flash-preview")
    
    prompt = f"""
    You are an expert Resume Optimizer. Analyze the Resume against the Job Description.
    
    RESUME: {resume_text}
    JD: {job_description if job_description else "General Optimization"}
    
    Output in strictly this format:
    MATCH_SCORE: [Number 0-100]
    ANALYSIS: [Main Feedback]
    IMPROVEMENTS: [Bulleted STAR points]
    KEYWORDS: [List of missing skills]
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"API Error: {str(e)}"

# ------------------ UI LAYOUT ------------------

st.markdown('<div class="hero"><h1>ResumePro AI</h1><p>Master the ATS with PhD-level insights</p></div>', unsafe_allow_html=True)

col_in, col_out = st.columns([1, 1.2], gap="large")

with col_in:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📥 Input Data")
    
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    job_desc = st.text_area("Job Description (Paste below)", height=250, placeholder="Target role details...")
    
    submit = st.button("✨ Analyze & Improve")
    st.markdown('</div>', unsafe_allow_html=True)

with col_out:
    if submit:
        if uploaded_file:
            with st.spinner("🚀 Gemini 3 is thinking..."):
                raw_text = extract_text_from_pdf(uploaded_file)
                if raw_text:
                    result = get_ai_suggestions(raw_text, job_desc)
                    
                    # Simple regex to find the score for visualization
                    score_match = re.search(r"MATCH_SCORE:\s*(\d+)", result)
                    score = int(score_match.group(1)) if score_match else 0
                    
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.markdown("### 🎯 ATS Match Score")
                    
                    # Progress Bar Visualization
                    st.progress(score / 100)
                    st.markdown(f'<div class="score-badge">{score}%</div>', unsafe_allow_html=True)
                    
                    st.markdown("### 💡 AI Recommendations")
                    st.write(result.split("MATCH_SCORE:")[0] if "MATCH_SCORE:" in result else result)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please upload a resume first.")
    else:
        st.markdown('<div class="glass-card" style="text-align:center;"><h3>Ready to scan!</h3><p>Upload a file to see your results.</p></div>', unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown('<div style="text-align:center; color:#64748b; padding:2rem;">Powered by Gemini 3 Flash • December 2025</div>', unsafe_allow_html=True)
