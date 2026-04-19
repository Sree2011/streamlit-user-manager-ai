# main.py (Streamlit UI)

import streamlit as st
import requests
import json
import re
import pandas as pd

API_BASE = "http://localhost:8000"  # FastAPI backend

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
st.title("📄 AI Resume Analyzer")


def clean_json_text(text: str) -> str:
    """Remove JS-style comments and trailing commas from streamed JSON."""
    text = re.sub(r'(?m)//.*$', '', text)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r',\s*([}\]])', r'\1', text)
    return text


def generate_recruiter_summary(analysis_data: list) -> str:
    if not analysis_data:
        return "No skill analysis data is available to generate a summary."

    matched = [item.get("skill_in_jd", "") for item in analysis_data if str(item.get("matched_in_resume", "")).strip().lower() == "yes"]
    unmatched = [item.get("skill_in_jd", "") for item in analysis_data if str(item.get("matched_in_resume", "")).strip().lower() != "yes"]

    matched = [skill for skill in matched if skill]
    unmatched = [skill for skill in unmatched if skill]

    if matched:
        if len(matched) == 1:
            strengths = f"The resume demonstrates strong alignment with {matched[0]}."
        elif len(matched) == 2:
            strengths = f"The resume demonstrates strong alignment with {matched[0]} and {matched[1]}."
        else:
            strengths = f"The resume demonstrates strong alignment with {', '.join(matched[:-1])}, and {matched[-1]}."
        strengths += " Evidence indicates relevant exposure and practical experience in these areas."
    else:
        strengths = "The resume does not clearly demonstrate alignment with the required job skills."

    if unmatched:
        if len(unmatched) == 1:
            gaps = f"However, the job description includes {unmatched[0]}, which is not explicitly reflected in the resume."
        else:
            gaps = f"However, several key skills highlighted in the job description — including {', '.join(unmatched[:-1])}, and {unmatched[-1]} — are not explicitly reflected in the resume."
    else:
        gaps = "There are no notable gaps between the job description skills and the resume." 

    tech_gaps = {"Spring", "SQL", "MongoDB", "Git", "CI/CD", "REST", "Angular", "React"}
    if any(skill in tech_gaps for skill in unmatched):
        focus = "This suggests that while the candidate brings solid expertise in core matched technologies, there are notable gaps in full-stack development and modern tooling/frameworks."
    else:
        focus = "This suggests that while the candidate brings solid expertise in matched areas, there are still gaps in other important job-specific skills."

    action = "Addressing these areas through targeted upskilling or by highlighting transferable experience could significantly improve overall fit for the role."

    return f"{strengths} {gaps} {focus} {action}"


uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
job_description = st.text_area("Paste Job Description", height=200)

if uploaded_file and st.button("Analyze Resume"):
    # Step 1: Upload resume to backend
    files = {"file": uploaded_file}
    upload_response = requests.post(f"{API_BASE}/upload_resume", files=files)
    resume_text = upload_response.json()["text"]

    

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

        # Compare resume and JD skills using the backend dictionary matcher
        compare_response = requests.post(
            f"{API_BASE}/compare_skills",
            json={"resume": {"text": resume_text}, "job": {"description": job_description}}
        )
        compare_data = compare_response.json()

        simple_score = compare_data.get("skill_comparison", {}).get("match_score", 0.0)

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Simple Match Score", value=f"{simple_score:.2f}%")

        


        resume_skills = set(compare_data.get("resume_skill_dict", {}).keys())
        jd_skills = set(compare_data.get("jd_skill_dict", {}).keys())
        comparison_dict = compare_data.get("skill_comparison", {})
        
        table1 = pd.DataFrame({
            "Skill in JD": list(jd_skills),
            "Matched in Resume": ["Yes" if skill in resume_skills else "No" for skill in jd_skills]
        })

        st.subheader("Skill Match Table")
        st.table(table1)




        # Stream the LLM analysis
        progress_bar = st.progress(0)
        status_text = st.empty()

        accumulated_text = ""
        cleaned_text = ""
        with st.spinner("Analyzing resume with LLM..."):
            # Pass pre-computed skill data to avoid recomputation
            stream_response = requests.post(
                f"{API_BASE}/stream_match_job",
                json={
                    "resume": {"text": resume_text},
                    "job": {"description": job_description},
                    "resume_skill_dict": compare_data.get("resume_skill_dict", {}),
                    "jd_skill_dict": compare_data.get("jd_skill_dict", {}),
                    "skill_comparison": compare_data.get("skill_comparison", {})
                },
                stream=True,
                timeout=(5, None)
            )
            
            total_chunks = 0
            for line in stream_response.iter_lines(decode_unicode=True):
                if line:
                    chunk = line
                    accumulated_text += chunk
                    cleaned_chunk = clean_json_text(chunk)
                    cleaned_text += cleaned_chunk
                    total_chunks += 1
                    progress_bar.progress(min(total_chunks / 100, 1.0))
                    status_text.text(f"Received {total_chunks} chunks...")
            
            # Debug: if no chunks received, try raw text
            if total_chunks == 0:
                accumulated_text = stream_response.text
                cleaned_text = clean_json_text(accumulated_text)

        progress_bar.empty()
        status_text.empty()

        if not accumulated_text or accumulated_text.strip() == "":
            st.warning("⚠️ No response received from LLM. The stream may be empty or the backend encountered an error.")
        else:
            try:
                cleaned_text = clean_json_text(accumulated_text)
                parsed_json = json.loads(cleaned_text)
                
                # Convert to dictionary for Python processing
                analysis_dict = {item.get('skill_in_jd', ''): item for item in parsed_json}
                
                llm_score = (sum(1 for d in parsed_json if d.get("matched_in_resume") == "Yes") / len(parsed_json)) * 100 if parsed_json else 0

                

                # Display recruiter-style summary
                st.subheader("Recruiter Summary")
                summary_text = generate_recruiter_summary(parsed_json)
                st.write(summary_text)

            except json.JSONDecodeError as e:
                st.error(f"Failed to parse LLM response: {str(e)}")
                st.info("💡 The LLM may have returned malformed JSON or inline comments.")
