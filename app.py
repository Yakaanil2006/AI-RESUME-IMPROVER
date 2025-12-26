import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os
import re

# ------------------ CONFIG ------------------
API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

st.set_page_config(
    page_title="ResumePro AI | Glass Edition",
    page_icon="🚀",
    layout="wide"
)

# ------------------ GLASSMORPHISM CSS ------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    /* Background Mesh Gradient */
    .stApp {
        background-color: #0f172a;
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(236, 72, 153, 0.1) 0px, transparent 50%),
            radial-gradient(at 0% 100%, rgba(45, 212, 191, 0.1) 0px, transparent 50%);
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #f1f5f9;
    }

    /* The Glass Effect Container */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(12px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(12px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 24px !important;
        padding: 2rem !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }

    /* Hero Text */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(to right, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
    }

    .hero-tagline {
        text-align: center;
        color: #818cf8;
        font-weight: 600;
        letter-spacing: 2px;
        margin-bottom: 3rem;
        font-size: 0.8rem;
    }

    /* Glass Score Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        margin-bottom: 20px;
    }

    .score-text {
        font-size: 4.5rem;
        font-weight: 800;
        line-height: 1;
        margin: 10px 0;
    }

    /* Button Styling */
    .stButton > button {
        background: rgba(99, 102, 241, 0.2) !important;
        backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: 0.4s all ease !important;
    }

    .stButton > button:hover {
        background: rgba(99, 102, 241, 0.4) !important;
        border: 1px solid #818cf8 !important;
        transform: translateY(-2px);
    }

    /* Custom Input appearance */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ HELPER FUNCTIONS ------------------
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
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        prompt = f"""
        Act as a recruiter. Analyze this resume against the JD. 
        Format your response exactly as:
        MATCH_SCORE: [0-100]
        ---
        ### 💎 Executive Summary
        (Briefly state the fit)
        
        ### 🔥 Missing Critical Keywords
        (List keywords found in JD but not resume)
        
        ### 🛠️ Recommended Actions
        (Actionable bullets to increase score)

        Resume: {resume_text}
        Job Description: {job_desc}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"MATCH_SCORE: 0\n\nError: {str(e)}"

# ------------------ APP INTERFACE ------------------

st.markdown('<div class="hero-title">ResumePro AI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-tagline">PRECISION CAREER OPTIMIZATION</div>', unsafe_allow_html=True)

layout_left, layout_right = st.columns([1, 1.2], gap="large")

with layout_left:
    st.markdown("### 📥 Source Files")
    with st.container():
        resume_file = st.file_uploader("Upload Resume", type=["pdf"])
        job_text = st.text_area("Job Description", height=250, placeholder="Paste requirements...")
        analyze_btn = st.button("Generate AI Audit", use_container_width=True)

with layout_right:
    if analyze_btn and resume_file and job_text:
        with st.spinner("Refining glass optics..."):
            text = extract_text_from_pdf(resume_file)
            if text:
                report = get_ai_analysis(text, job_text)
                
                # Logic to parse the AI response
                score_match = re.search(r"MATCH_SCORE:\s*(\d+)", report)
                score = int(score_match.group(1)) if score_match else 0
                clean_report = re.sub(r"MATCH_SCORE:\s*\d+", "", report).replace("---", "").strip()

                # Visualizing Score with Glassmorphism
                color = "#22c55e" if score > 75 else "#f59e0b" if score > 50 else "#ef4444"
                
                st.markdown(f"""
                <div class="glass-card">
                    <span style="color: #94a3b8; font-size: 0.9rem; font-weight: 600; letter-spacing: 1px;">MATCH ACCURACY</span>
                    <div class="score-text" style="color: {color};">{score}%</div>
                    <div style="width:100%; background:rgba(255,255,255,0.05); height:12px; border-radius:20px;">
                        <div style="width:{score}%; background:{color}; height:100%; border-radius:20px; box-shadow: 0 0 15px {color}66;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(clean_report)
                
                st.download_button(
                    label="Download Report (.md)",
                    data=clean_report,
                    file_name="Resume_Optimization.md",
                    mime="text/markdown",
                    use_container_width=True
                )
    else:
        # Default State
        st.markdown(f"""
        <div style="border: 1px dashed rgba(255,255,255,0.2); border-radius: 24px; padding: 5rem 2rem; text-align: center; background: rgba(255,255,255,0.01);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">💎</div>
            <h4 style="color: #64748b;">Ready to Optimize</h4>
            <p style="color: #475569; font-size: 0.9rem;">Upload your credentials to activate AI insights</p>
        </div>
        """, unsafe_allow_html=True)

# Footer

st.markdown("<div style='text-align:center; padding: 2rem; color: #475569; font-size: 1.5rem;'>ResumePro AI • 2025 •</div>", unsafe_allow_html=True)








change the ui with a clean and more visible effects with matching colors
