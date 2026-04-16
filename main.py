# backend/main.py (Streamlit UI)

import streamlit as st
import requests

API_BASE = "http://localhost:8000"  # FastAPI backend

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
st.title("📄 AI Resume Analyzer")

uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
job_description = st.text_area("Paste Job Description", height=200)

if uploaded_file and st.button("Analyze Resume"):
    # Step 1: Upload resume to backend
    files = {"file": uploaded_file}
    upload_response = requests.post(f"{API_BASE}/upload_resume", files=files)
    resume_text = upload_response.json()["text"]

    st.subheader("Resume Text Preview")
    st.write(resume_text[:1000] + "...")

    # Step 2: Analyze resume (skills)
    analyze_response = requests.post(f"{API_BASE}/analyze_resume", json={"text": resume_text})
    skills = analyze_response.json()["skills"]

    st.subheader("Extracted Skills")
    st.write(skills)

    # Step 3: Match job (score + insights)
    if job_description:
        match_response = requests.post(
            f"{API_BASE}/match_job",
            json={"resume": {"text": resume_text}, "job": {"description": job_description}}
        )
        result = match_response.json()

        st.subheader("Match Score")
        st.write(result["match_score"])

        st.subheader("LLM Insights")
        st.write(result["llm_insights"])
