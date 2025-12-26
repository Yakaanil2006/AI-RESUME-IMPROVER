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
    page_icon="🧠",
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

    /* Target the container specifically to remove the "empty card" artifact */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(30, 41, 59, 0.6) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 1rem !important;
    }

    /* Hero Branding */
    .hero-container {
        text-align: center;
        padding: 1.5rem 0;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3b82f6, #2dd4bf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }

    /* Accuracy Score Visual */
    .score-container {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .score-badge {
        background: rgba(34, 197, 94, 0.1);
        border: 2px solid #22c55e;
        border-radius: 50%;
        width: 120px;
        height: 120px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        color: #22c55e;
    }
    .score-value { font-size: 2.2rem; font-weight: 800; line-height: 1; }
    .score-label { font-size: 0.75rem; text-transform: uppercase; font-weight: 600; margin-top: 4px; }

    /* Button Styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: 0.3s;
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
        st.error(f"Error extracting PDF: {e}")
        return None

def get_ai_analysis(resume_text, job_desc):
    try:
        model = genai.GenerativeModel("gemma-3-12b"or"gemma-3-1b")
        prompt = f"""
        Analyze this resume against the job description. 
        Format your response starting exactly with 'MATCH_SCORE: [number]'. 
        Then provide sections for 'Professional Summary', 'Key Improvements', and 'Missing Keywords'.
        
        Resume: {resume_text}
        Job Description: {job_desc}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"MATCH_SCORE: 0\n\nAI Service Error: {str(e)}"

# ------------------ UI LAYOUT ------------------

st.markdown("""
<div class="hero-container">
    <div class="hero-title">ResumePro AI</div>
    <p style="color: #94a3b8;">High-Precision ATS Matching & Optimization</p>
</div>
""", unsafe_allow_html=True)

col_input, col_result = st.columns([1, 1.2], gap="large")

with col_input:
    with st.container(border=True):
        st.markdown("<h3 style='margin-top:0;'>📤 Input Details</h3>", unsafe_allow_html=True)
        
        resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        
        job_text = st.text_area(
            "Target Job Description",
            height=300,
            placeholder="Paste requirements here to calculate your Match Accuracy..."
        )
        
        analyze_btn = st.button("Generate Detailed Analysis")

with col_result:
    if analyze_btn and resume_file:
        with st.spinner("🧠 AI is analyzing your credentials..."):
            text = extract_text_from_pdf(resume_file)
            if text:
                report = get_ai_analysis(text, job_text)
                
                # Parse Score
                score_match = re.search(r"MATCH_SCORE:\s*(\d+)", report)
                score = int(score_match.group(1)) if score_match else 0
                clean_report = re.sub(r"MATCH_SCORE:\s*\d+", "", report)
                clean_report = re.sub(r"/?100\s*", "", clean_report).strip()

                with st.container(border=True):
                    st.markdown("<h3 style='text-align: center; margin-top:0;'>📊 Performance Report</h3>", unsafe_allow_html=True)
                    st.markdown(f"""
                        <div class="score-container">
                            <div class="score-badge">
                                <div class="score-value">{score}%</div>
                                <div class="score-label">Match Accuracy</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div style="width:100%; background:#1e293b; border-radius:10px; height:10px;">
                        <div style="
                        width:{score}%;
                        background:linear-gradient(90deg,#22c55e,#4ade80);
                        height:100%;
                        border-radius:10px;">
                        </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("---")
                    st.markdown(clean_report)
                    
                    # Download Feature
                    st.download_button(
                        label="📥 Download Report as Text",
                        data=clean_report,
                        file_name="ResumePro_Analysis.txt",
                        mime="text/plain"
                    )
    else:
        st.markdown("""
            <div style="text-align: center; padding: 7rem 2rem; border: 2px dashed rgba(255,255,255,0.1); border-radius: 20px;">
                <h3 style="color: #475569;">Awaiting Data</h3>
                <p style="color: #64748b;">Upload your resume and provide a JD to see your match accuracy and improvement tips.</p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; padding: 2rem; color: #475569; font-size: 1.5rem;'>ResumePro AI • 2025 •</div>", unsafe_allow_html=True)





