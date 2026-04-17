# backend/routes.py

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
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
    content = await extractor.extract_text(file) #
    return Resume(text=content) #

@router.post("/analyze_resume", response_model=AnalysisResult)
async def analyze_resume(resume: Resume):
    """
    Extract skills from resume text.
    """
    skills = await extractor.extract_skills(resume.text) #
    return AnalysisResult(skills=skills, match_score=0.0, llm_insights=None) #

@router.post("/match_job")
async def match_job(matchresult: MatchRequest):
    """
    Compare resume with job description.
    Returns match score and streams LLM insights.
    """
    # 1. Perform quick synchronous calculations
    skills = await extractor.extract_skills(matchresult.resume.text) #
    match_score = matcher.calculate_match(skills, matchresult.job.description) #
    
    # 2. Prepare the prompt for the LLM
    prompt = f"Resume: {matchresult.resume.text}\nJob: {matchresult.job.description}"

    # 3. Return a StreamingResponse
    # We pass the metadata (skills/score) via custom headers so the frontend can still read them
    return StreamingResponse(
        ollama_api.ollama_chat(prompt,"phi3"), 
        media_type="text/plain",
        headers={
            "X-Match-Score": str(match_score),
            "X-Skills": json.dumps(skills)
        }
    )