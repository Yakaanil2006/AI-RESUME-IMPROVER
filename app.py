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
    page_title="ResumePro AI | Premium Optimizer",
    page_icon="✨",
    layout="wide"
)

# ------------------ PREMIUM UI STYLING ------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    :root {
        --primary: #6366f1;
        --secondary: #a855f7;
        --bg-dark: #0f172a;
        --card-bg: rgba(30, 41, 59, 0.7);
    }

    .stApp {
        background: radial-gradient(circle at 0% 0%, #1e1b4b 0%, #0f172a 100%);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Glassmorphism Containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--card-bg) !important;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 24px !important;
        padding: 2rem !important;
        box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
    }

    /* Gradient Typography */
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        letter-spacing: -2px;
        background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    .hero-subtitle {
        color: #818cf8;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }

    /* Score Ring Animation */
    @keyframes precent {
        0% { stroke-dashoffset: 300; }
    }

    .score-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .score-card:hover {
        transform: translateY(-5px);
        border-color: var(--primary);
    }

    /* Button Overrides */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
    }

    /* Input Field Styling */
    .stTextArea textarea, .stFileUploader section {
        background-color: rgba(15, 23, 42, 0.5) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
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
        st.error(f"Error extracting PDF: {e}")
        return None

def get_ai_analysis(resume_text, job_desc):
    try:
        model = genai.GenerativeModel("gemma-3-27b") 
        prompt = f"""
        Role: Expert ATS Resume Strategist
        Task: Analyze the resume against the job description. 
        Format your response exactly as follows:
        MATCH_SCORE: [0-100]
        ---
        ### 🎯 Match Insights
        [Detailed summary]
        
        ### 🚀 Key Improvements
        [Actionable bullet points]
        
        ### 🔑 Missing Keywords
        [Comma separated list]
        
        Resume: {resume_text}
        Job Description: {job_desc}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"MATCH_SCORE: 0\n\nAI Service Error: {str(e)}"

# ------------------ UI LAYOUT ------------------

# Hero Section
st.markdown("""
<div style="text-align: center; padding: 3rem 0;">
    <div class="hero-subtitle">AI-POWERED CAREER ACCELERATOR</div>
    <div class="hero-title">ResumePro AI</div>
</div>
""", unsafe_allow_html=True)

col_input, col_result = st.columns([1, 1.3], gap="large")

with col_input:
    st.markdown("### 🛠️ Configuration")
    with st.container():
        resume_file = st.file_uploader("Drop your resume here", type=["pdf"], help="PDF format only for optimal parsing")
        
        job_text = st.text_area(
            "Target Role Requirements",
            height=280,
            placeholder="Paste the job description here to see how you rank..."
        )
        
        analyze_btn = st.button("Analyze Alignment", use_container_width=True)

with col_result:
    if analyze_btn and resume_file and job_text:
        with st.spinner("⚡ Calibrating Neural Matchers..."):
            text = extract_text_from_pdf(resume_file)
            if text:
                report = get_ai_analysis(text, job_text)
                
                # Parsing
                score_match = re.search(r"MATCH_SCORE:\s*(\d+)", report)
                score = int(score_match.group(1)) if score_match else 0
                clean_report = re.sub(r"MATCH_SCORE:\s*\d+", "", report).strip()
                clean_report = clean_report.replace("---", "")

                # Score Visualization
                st.markdown(f"""
                <div class="score-card">
                    <h2 style="margin:0; color: #94a3b8; font-size: 1rem;">COMPATIBILITY INDEX</h2>
                    <div style="font-size: 4rem; font-weight: 800; color: { '#22c55e' if score > 75 else '#f59e0b' if score > 50 else '#ef4444' };">
                        {score}<span style="font-size: 1.5rem;">%</span>
                    </div>
                    <div style="width:100%; background:rgba(255,255,255,0.1); height:8px; border-radius:10px; margin-top:10px;">
                        <div style="width:{score}%; background:linear-gradient(90deg, #6366f1, #a855f7); height:100%; border-radius:10px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(clean_report)
                
                st.download_button(
                    label="💾 Export Optimization Strategy",
                    data=clean_report,
                    file_name="Optimization_Strategy.md",
                    mime="text/markdown",
                    use_container_width=True
                )
    else:
        # Placeholder State
        st.markdown("""
        <div style="text-align: center; padding: 8rem 2rem; opacity: 0.5;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🔬</div>
            <h3 style="color: #94a3b8; font-weight: 400;">Ready for Analysis</h3>
            <p>Upload your documents to unlock deep keyword insights and compatibility scores.</p>
        </div>
        """, unsafe_allow_html=True)


st.markdown("<div style='text-align:center; padding: 2rem; color: #475569; font-size: 1.5rem;'>ResumePro AI • 2025 •</div>", unsafe_allow_html=True)









