# backend/models.py

from pydantic import BaseModel
from typing import List, Optional

class Resume(BaseModel):
    text: str

class JobDescription(BaseModel):
    description: str

class AnalysisResult(BaseModel):
    skills: List[str]
    match_score: float
    llm_insights: Optional[str] = None


class MatchRequest(BaseModel):
    resume: Resume
    job: JobDescription