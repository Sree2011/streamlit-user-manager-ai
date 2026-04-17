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

    # Step 3: Match job (streaming score + insights)
    if job_description:
        st.subheader("Analysis Results")
        
        # We use stream=True to handle the StreamingResponse from FastAPI
        with requests.post(
            f"{API_BASE}/match_job",
            json={"resume": {"text": resume_text}, "job": {"description": job_description}},
            stream=True
        ) as response:
            
            # Extract metadata from custom headers
            match_score = response.headers.get("X-Match-Score", "0.0")
            raw_skills = response.headers.get("X-Skills", "[]")
            matched_skills = json.loads(raw_skills)

            # Display Match Score
            st.metric(label="Match Score", value=f"{match_score}%")
            
            # Display LLM Insights using streaming
            st.subheader("LLM Insights")
            
            # Helper generator to decode chunks for st.write_stream
            def stream_content():
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        yield chunk

            st.write_stream(stream_content())