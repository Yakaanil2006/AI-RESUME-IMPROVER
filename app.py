import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os
import re
import pandas as pd
from datetime import datetime

# ------------------ CONFIG ------------------
API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

st.set_page_config(page_title="ResumePro AI | Dashboard", page_icon="🚀", layout="wide")

# Initialize Session States
if 'history' not in st.session_state: st.session_state['history'] = []
if 'report' not in st.session_state: st.session_state['report'] = None

# ------------------ CLEAN UI STYLING ------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    .stApp { background: #0b0f1a; font-family: 'Inter', sans-serif; color: #e2e8f0; }
    
    /* Container Glass Effect */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(23, 32, 53, 0.8) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
    }

    .hero-title { font-size: 3rem; font-weight: 800; text-align: center; color: white; margin-bottom: 0; }
    .hero-accent { background: linear-gradient(90deg, #6366f1, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px; padding: 25px; text-align: center; margin-bottom: 20px;
    }
    
    .history-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px; padding: 12px; margin-bottom: 10px;
        border-left: 4px solid #6366f1;
    }

    .score-text { font-size: 4rem; font-weight: 800; margin: 0; }
    
    /* Buttons */
    .stButton > button {
        background: #6366f1 !important; color: white !important; border-radius: 8px !important;
        font-weight: 700 !important; width: 100%; transition: 0.3s;
    }
    .stButton > button:hover { background: #4f46e5 !important; transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

# ------------------ HELPERS ------------------
def extract_text_from_pdf(uploaded_file):
    try:
        text = ""
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc: text += page.get_text()
        return text
    except Exception as e:
        st.error(f"PDF Error: {e}"); return None

def get_ai_analysis(resume_text, job_desc):
    try:
        model = genai.GenerativeModel("gemma-3-12b")
        prompt = f"""
        Role: Senior Recruiter
        Format strictly as:
        MATCH_SCORE: [0-100]
        TOP_SKILLS: [Skill1, Skill2, Skill3]
        MISSING_SKILLS: [Skill1, Skill2, Skill3]
        ---
        ### 📊 Match Breakdown
        (Suitability summary)
        ### 🚀 Optimization Steps
        (Actionable bullets)
        ### 🎤 Interview Questions
        (3 targeted questions based on gaps)

        Resume: {resume_text}
        Job Description: {job_desc}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"MATCH_SCORE: 0\nError: {str(e)}"

# ------------------ SIDEBAR (FEATURE 1: TRACKER) ------------------
with st.sidebar:
    st.markdown("### 📋 Application Tracker")
    if st.session_state['history']:
        for i, item in enumerate(reversed(st.session_state['history'])):
            st.markdown(f"""
            <div class="history-card">
                <small>{item['date']}</small><br>
                <strong>{item['company']}</strong><br>
                <span style="color:#10b981">Score: {item['score']}%</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Reload {item['company']}", key=f"hist_{i}"):
                st.session_state['report'] = item['report']
    else:
        st.info("No applications yet.")
    
    if st.button("Clear History"):
        st.session_state['history'] = []; st.rerun()

# ------------------ MAIN INTERFACE ------------------
st.markdown('<div class="hero-title">ResumePro <span class="hero-accent">AI</span></div>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color: #94a3b8; margin-bottom: 2rem;'>Elite Resume-to-Job Alignment Dashboard</p>", unsafe_allow_html=True)

col_in, col_out = st.columns([1, 1.2], gap="large")

with col_in:
    st.markdown("#### 🛠️ Audit Setup")
    company = st.text_input("Target Company", placeholder="e.g., Google")
    resume_file = st.file_uploader("Resume (PDF)", type=["pdf"])
    job_text = st.text_area("Job Description", height=250)
    
    if st.button("Analyze Compatibility"):
        if resume_file and job_text:
            with st.spinner("Processing..."):
                text = extract_text_from_pdf(resume_file)
                if text:
                    res = get_ai_analysis(text, job_text)
                    st.session_state['report'] = res
                    # Log History
                    score_val = int(re.search(r"MATCH_SCORE:\s*(\d+)", res).group(1)) if "MATCH_SCORE" in res else 0
                    st.session_state['history'].append({
                        "company": company if company else "General",
                        "score": score_val,
                        "report": res,
                        "date": datetime.now().strftime("%b %d, %H:%M")
                    })
        else:
            st.warning("Input required.")

with col_out:
    if st.session_state['report']:
        report = st.session_state['report']
        
        # Parse Data
        score = int(re.search(r"MATCH_SCORE:\s*(\d+)", report).group(1))
        top_skills = re.search(r"TOP_SKILLS:\s*\[(.*?)\]", report).group(1).split(",")
        missing_skills = re.search(r"MISSING_SKILLS:\s*\[(.*?)\]", report).group(1).split(",")
        clean_md = re.split(r"---", report)[-1]

        # FEATURE 2: VISUALIZATION
        color = "#10b981" if score > 75 else "#f59e0b" if score > 50 else "#ef4444"
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:0.8rem; font-weight:700; color:#94a3b8; letter-spacing:1px;">MATCH RATING</div>
            <div class="score-text" style="color:{color};">{score}%</div>
            <div style="width:100%; background:rgba(255,255,255,0.05); height:10px; border-radius:10px; overflow:hidden; margin-top:10px;">
                <div style="width:{score}%; background:{color}; height:100%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📊 Skill Comparison")
        skills_df = pd.DataFrame({
            "Skill Set": ["Present", "Missing"],
            "Count": [len(top_skills), len(missing_skills)]
        })
        st.bar_chart(skills_df.set_index("Skill Set"), color="#6366f1")

        st.markdown(clean_md)
        
        st.download_button("📥 Download PDF-Ready Report", data=clean_md, file_name="ResumePro_Report.md")
    else:
        st.markdown('<div style="height:400px; display:flex; align-items:center; justify-content:center; border:2px dashed rgba(255,255,255,0.1); border-radius:20px; color:#475569;">Analysis results will appear here</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div style='text-align:center; color: #334155; font-size: 0.8rem;'>RESUMEPRO AI © 2025</div>", unsafe_allow_html=True)
