# backend/routes.py

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from backend.services import extractor, matcher, ollama_api
from backend.models import Resume, AnalysisResult, MatchRequest, StreamMatchRequest
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
    resume_skill_dict = extractor.extract_skill_dict(matchresult.resume.text)
    jd_skill_dict = extractor.extract_skill_dict(matchresult.job.description)
    skill_comparison = matcher.compare_skill_dicts(resume_skill_dict, jd_skill_dict)

    # Call Ollama synchronously for full analysis
    result = ollama_api.match_job(
        resume_skill_dict,
        jd_skill_dict,
        skill_comparison
    )

    return {
        "match_score": skill_comparison["match_score"],
        "skills": list(resume_skill_dict.keys()),
        "resume_skill_dict": resume_skill_dict,
        "jd_skill_dict": jd_skill_dict,
        "skill_comparison": skill_comparison,
        "table": result["table"],
        "missing_skills": result["missing_skills"],
        "raw_json": result["raw_json"]
    }


@router.post("/compare_skills")
async def compare_skills(matchresult: MatchRequest):
    """
    Compare extracted skills from resume and job description using dictionaries.
    """
    resume_skill_dict = extractor.extract_skill_dict(matchresult.resume.text)
    jd_skill_dict = extractor.extract_skill_dict(matchresult.job.description)
    return {
        "resume_skill_dict": resume_skill_dict,
        "jd_skill_dict": jd_skill_dict,
        "skill_comparison": matcher.compare_skill_dicts(resume_skill_dict, jd_skill_dict)
    }


@router.post("/stream_match_job")
async def stream_match_job(request: StreamMatchRequest):
    """
    Stream the LLM analysis. Accepts pre-computed skill dicts to avoid redundant computation.
    """
    resume_skill_dict = request.resume_skill_dict
    jd_skill_dict = request.jd_skill_dict
    skill_comparison = request.skill_comparison

    # Only compute if not provided
    if resume_skill_dict is None and request.resume:
        resume_skill_dict = extractor.extract_skill_dict(request.resume.text)
    if jd_skill_dict is None and request.job:
        jd_skill_dict = extractor.extract_skill_dict(request.job.description)
    if skill_comparison is None and resume_skill_dict and jd_skill_dict:
        skill_comparison = matcher.compare_skill_dicts(resume_skill_dict, jd_skill_dict)

    return StreamingResponse(
        ollama_api.stream_resume_analysis(resume_skill_dict, jd_skill_dict, skill_comparison),
        media_type="text/plain"
    )
