# main.py (Streamlit UI)

import streamlit as st
import requests
import json

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

    # Step 3: Match job (plain JSON response)
    if job_description:
        st.subheader("Analysis Results")

        match_response = requests.post(
            f"{API_BASE}/match_job",
            json={"resume": {"text": resume_text}, "job": {"description": job_description}}
        )

        result = match_response.json()

        # Display Match Score
        st.metric(label="Match Score", value=f"{result.get('match_percentage', result.get('match_score', 0))}%")

        # Display Skills
        st.subheader("Matched Skills")
        st.write(result.get("skills", []))

        # Display Missing Skills
        st.subheader("Missing Skills")
        st.write(result.get("missing_skills", []))

        # Display Table
        st.subheader("LLM Insights (Table)")
        st.markdown(result.get("table", "No insights returned"))
