import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os

# ------------------ CONFIGURATION ------------------
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

st.set_page_config(
    page_title="AI Resume Improver",
    page_icon="📝",
    layout="wide"
)

# ------------------ STYLING ------------------
st.markdown("""
<style>

/* App background */
.stApp {
    background: linear-gradient(to right, #f8fafc, #eef2f7);
    font-family: 'Segoe UI', sans-serif;
}

/* Hero section */
.hero {
    background: linear-gradient(90deg, #2563eb, #4f46e5);
    padding: 2.8rem;
    border-radius: 18px;
    color: white;
    text-align: center;
    margin-bottom: 2.5rem;
}

.hero h1 {
    font-size: 2.7rem;
    font-weight: 700;
}

.hero p {
    font-size: 1.15rem;
    opacity: 0.9;
}

/* Card layout */
.card {
    background: white;
    padding: 2rem;
    border-radius: 18px;
    box-shadow: 0 12px 28px rgba(0,0,0,0.08);
    margin-bottom: 1.5rem;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #2563eb, #4f46e5);
    color: white;
    border-radius: 14px;
    height: 3.3em;
    font-size: 1.05rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(79,70,229,0.4);
}

/* Inputs */
textarea, [data-testid="stFileUploader"] {
    border-radius: 14px !important;
}

/* Footer */
.footer {
    text-align: center;
    color: #64748b;
    font-size: 0.9rem;
    margin-top: 3rem;
}

</style>
""", unsafe_allow_html=True)

# ------------------ FUNCTIONS ------------------
def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF"""
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
    """Gemini AI resume analysis"""
    model = genai.GenerativeModel("gemini-3-flash-preview")

    prompt = f"""
You are an expert Resume Optimizer and ATS Specialist.

TASK:
Analyze the RESUME against the JOB DESCRIPTION (JD).

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description if job_description else "No JD provided. Give general professional improvements."}

DELIVERABLES:
1. MATCH SCORE (0–100%)
2. MISSING KEYWORDS / SKILLS
3. IMPROVED BULLET POINTS (3–5, STAR method)
4. 5 STRONG ACTION VERBS
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

# ------------------ UI ------------------

# Hero
st.markdown("""
<div class="hero">
    <h1>📝 AI Resume Improver</h1>
    <p>Optimize your resume for ATS • Increase interview calls • Powered by AI</p>
</div>
""", unsafe_allow_html=True)

# Columns
col1, col2 = st.columns([1, 1], gap="large")

# ------------------ LEFT CARD ------------------
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📄 Upload Resume & Job Details")

    uploaded_file = st.file_uploader(
        "Upload your Resume (PDF only)",
        type="pdf"
    )

    job_description = st.text_area(
        "Paste Job Description (Highly Recommended)",
        height=220,
        placeholder="Example: Software Engineer role requiring Python, ML, AWS..."
    )

    analyze_button = st.button("🚀 Analyze Resume")
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ RIGHT CARD ------------------
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI Analysis & ATS Suggestions")

    if analyze_button:
        if uploaded_file:
            with st.spinner("🔍 Analyzing resume with AI..."):
                resume_text = extract_text_from_pdf(uploaded_file)

                if resume_text:
                    analysis = get_ai_suggestions(resume_text, job_description)
                    st.markdown("---")
                    st.markdown(analysis)
                    st.success("✅ Analysis Complete!")
                else:
                    st.error("❌ Could not extract text. Scanned PDFs are not supported.")
        else:
            st.warning("📌 Please upload your resume first.")
    else:
        st.info("Upload your resume and click **Analyze Resume** to see AI-powered insights.")

    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("""
<div class="footer">
    Built with ❤️ using Streamlit
    © 2025 AI Resume Improver
</div>
""", unsafe_allow_html=True)
