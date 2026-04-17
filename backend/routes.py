# backend/routes.py

from fastapi import APIRouter, UploadFile, File
from backend.services import extractor, matcher, ollama_api
from backend.models import Resume, AnalysisResult, MatchRequest
import json

router = APIRouter()

@router.post("/upload_resume", response_model=Resume)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF/DOCX).
    Extract text and return raw content.
    """
    content = await extractor.extract_text(file)
    return Resume(text=content)

@router.post("/analyze_resume", response_model=AnalysisResult)
async def analyze_resume(resume: Resume):
    """
    Extract skills from resume text.
    """
    skills = await extractor.extract_skills(resume.text)
    return AnalysisResult(skills=skills, match_score=0.0, llm_insights=None)

@router.post("/match_job")
async def match_job(matchresult: MatchRequest):
    """
    Match resume against job description and return JSON results.
    """
    skills = await extractor.extract_skills(matchresult.resume.text)
    match_score = matcher.calculate_match(skills, matchresult.job.description)

    # Call Ollama synchronously for full analysis
    result = ollama_api.analyze_resume(
        matchresult.resume.text,
        matchresult.job.description
    )

    return {
        "match_score": match_score,
        "skills": skills,
        "table": result["table"],
        "missing_skills": result["missing_skills"],
        "raw_json": result["raw_json"]
    }
