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

/* ---------- GLOBAL ---------- */
.stApp {
    background-color: #f9fafb;
    font-family: "Inter", "Segoe UI", sans-serif;
    color: #111827;
}

/* ---------- HERO ---------- */
.hero {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    padding: 2.5rem;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 2.5rem;
}

.hero h1 {
    font-size: 2.6rem;
    font-weight: 700;
    color: #1f2937;
}

.hero p {
    font-size: 1.1rem;
    color: #4b5563;
}

/* ---------- CARDS ---------- */
.card {
    background: #ffffff;
    padding: 2rem;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    margin-bottom: 1.5rem;
}

/* ---------- BUTTON ---------- */
.stButton > button {
    background-color: #1a73e8;
    color: white;
    border-radius: 12px;
    height: 3.2em;
    font-size: 1rem;
    font-weight: 600;
    border: none;
}

.stButton > button:hover {
    background-color: #1558b0;
}

/* ---------- INPUTS ---------- */
textarea,
[data-testid="stFileUploader"] {
    border-radius: 12px !important;
    border: 1px solid #d1d5db !important;
    background-color: #f9fafb;
}

/* ---------- STATUS COLORS ---------- */
.stAlert-success {
    background-color: #ecfdf5;
    color: #065f46;
}

.stAlert-warning {
    background-color: #fffbeb;
    color: #92400e;
}

.stAlert-error {
    background-color: #fef2f2;
    color: #991b1b;
}

/* ---------- FOOTER ---------- */
.footer {
    text-align: center;
    color: #6b7280;
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

