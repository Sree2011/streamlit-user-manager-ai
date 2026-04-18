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

    # Step 2: Match job (includes skill extraction and LLM analysis)
    if job_description:
        st.subheader("Analysis Results")

    # Step 2: Match job (includes skill extraction and LLM analysis)
    if job_description:
        st.subheader("Analysis Results")

        # First, get skills
        skills_response = requests.post(
            f"{API_BASE}/analyze_resume",
            json={"text": resume_text}
        )
        skills_data = skills_response.json()
        skills = skills_data.get("skills", [])

        # Compute simple match score
        import re
        jd_text = job_description.lower()
        matched = sum(1 for skill in skills if re.search(rf"\b{skill.lower()}\b", jd_text))
        simple_score = (matched / len(skills)) * 100 if skills else 0.0

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Simple Match Score", value=f"{simple_score}%")

        # Stream the LLM analysis
        st.subheader("LLM Analysis (Streaming)")
        stream_placeholder = st.empty()

        accumulated_text = ""
        stream_response = requests.post(
            f"{API_BASE}/stream_match_job",
            json={"resume": {"text": resume_text}, "job": {"description": job_description}},
            stream=True
        )

        for line in stream_response.iter_lines():
            if line:
                chunk = line.decode('utf-8')
                accumulated_text += chunk
                stream_placeholder.text(accumulated_text)

        # After streaming, parse the JSON
        try:
            parsed_json = json.loads(accumulated_text)
            markdown_table = ""
            missing_skills = []
            for item in parsed_json:
                # Build table
                if not markdown_table:
                    markdown_table = "| Skill in JD | Matched in Resume | Evidence/Insight |\n| :--- | :--- | :--- |\n"
                markdown_table += f"| {item.get('skill_in_jd','')} | {item.get('matched_in_resume','')} | {item.get('evidence','')} |\n"
                if item.get('matched_in_resume') == 'No':
                    missing_skills.append(item.get('skill_in_jd'))

            llm_score = (sum(1 for d in parsed_json if d.get("matched_in_resume") == "Yes") / len(parsed_json)) * 100 if parsed_json else 0

            with col2:
                st.metric(label="LLM Match Score", value=f"{llm_score:.2f}%")

            # Display Skills
            st.subheader("Extracted Skills")
            st.write(skills)

            # Display Missing Skills
            st.subheader("Missing Skills (from LLM)")
            st.write(missing_skills)

            # Display Table
            st.subheader("LLM Insights (Table)")
            st.markdown(markdown_table)

        except json.JSONDecodeError:
            st.error("Failed to parse LLM response.")
