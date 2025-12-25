import streamlit as st
import fitz 
import google.generativeai as genai
import os

API_KEY = "AIzaSyCi2R516faI1em_ElgydKvdZdjV3hi512I"
genai.configure(api_key=API_KEY)


def extract_text_from_pdf(uploaded_file):
    """Extracts text content from an uploaded PDF file."""
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
    """Interacts with Gemini API to analyze the resume."""
    model = genai.GenerativeModel('gemini-3-flash-preview')
    
    prompt = f"""
    You are an expert Resume Optimizer and ATS Specialist. 
    
    TASK:
    Analyze the RESUME provided below against the JOB DESCRIPTION (JD).
    
    RESUME TEXT:
    {resume_text}
    
    JOB DESCRIPTION:
    {job_description if job_description else "No specific JD provided. Provide general professional improvements."}
    
    DELIVERABLES:
    1. MATCH SCORE: A percentage (0-100%) showing how well the resume matches the JD.
    2. KEYWORD GAP: Identify essential skills/keywords missing from the resume.
    3. BULLET POINT IMPROVEMENTS: Rewrite 3-5 existing bullet points to be more 'Result-Oriented' using the STAR method.
    4. ACTION VERBS: Suggest 5 strong verbs the candidate should use.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"


st.set_page_config(page_title="AI Resume Improver", page_icon="✍️", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📝 AI Resume Improver")
st.subheader("Land more interviews by optimizing your resume for ATS.")

# Layout Columns
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 1. Upload & Input")
    uploaded_file = st.file_uploader("Upload your Resume (PDF format)", type="pdf")
    job_description = st.text_area("Paste the Job Description here (Highly Recommended)", height=250, placeholder="Software Engineer role at Google requires Python, AWS...")
    
    analyze_button = st.button("Analyze Resume")

with col2:
    st.markdown("### 2. AI Analysis & Suggestions")
    
    if analyze_button:
        if uploaded_file is not None:
            with st.spinner("Processing... Analyzing text and generating suggestions."):
                # Execute Pipeline
                resume_text = extract_text_from_pdf(uploaded_file)
                
                if resume_text:
                    analysis_report = get_ai_suggestions(resume_text, job_description)
                    
                    # Display Result
                    st.markdown("---")
                    st.markdown(analysis_report)
                    st.success("Analysis Complete!")
                else:
                    st.error("Could not extract text from the PDF. Is it a scanned image?")
        else:
            st.warning("Please upload a PDF file to begin.")
    else:
        st.info("Upload your resume and click 'Analyze Resume' to see suggestions here.")

# --- 4. FOOTER ---
st.markdown("---")
st.caption("Built with Streamlit")