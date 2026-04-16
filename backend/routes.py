# backend/routes.py

from fastapi import APIRouter, UploadFile, File, Form
from backend.services import extractor, matcher, ollama_api
from backend.models import Resume,AnalysisResult, JobDescription
router = APIRouter()

@router.post("/upload_resume", response_model=Resume)
def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF/DOCX).
    Extract text and return raw content.
    """
    content = extractor.extract_text(file)
    return Resume(text=content)




@router.post("/analyze_resume", response_model=AnalysisResult)
def analyze_resume(resume: Resume):
    """
    Extract skills from resume text.
    """
    skills = extractor.extract_skills(resume.text)
    return AnalysisResult(skills=skills, match_score=0.0, llm_insights=None)





@router.post("/match_job", response_model=AnalysisResult)
def match_job(resume: Resume, job: JobDescription):
    """
    Compare resume with job description.
    Returns match score and LLM insights.
    """
    skills = extractor.extract_skills(resume.text)
    match_score = matcher.calculate_match(skills, job.description)
    insights = ollama_api.get_llm_insights(resume.text, job.description)

    return AnalysisResult(skills=skills, match_score=match_score, llm_insights=insights)

