# backend/routes.py

from fastapi import APIRouter, UploadFile, File, Form
from backend.services import extractor, matcher, ollama_api

router = APIRouter()

@router.post("/upload_resume")
def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF/DOCX).
    Extract text and return raw content.
    """
    content = extractor.extract_text(file)
    return {"resume_text": content}


@router.post("/analyze_resume")
def analyze_resume(resume_text: str = Form(...)):
    """
    Extract skills from resume text.
    """
    skills = extractor.extract_skills(resume_text)
    return {"skills": skills}


@router.post("/match_job")
def match_job(resume_text: str = Form(...), job_description: str = Form(...)):
    """
    Compare resume with job description.
    Returns match score and LLM insights.
    """
    skills = extractor.extract_skills(resume_text)
    match_score = matcher.calculate_match(skills, job_description)
    insights = ollama_api.get_llm_insights(resume_text, job_description)

    return {
        "skills": skills,
        "match_score": match_score,
        "llm_insights": insights
    }
