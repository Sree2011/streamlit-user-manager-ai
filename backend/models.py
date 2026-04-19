from pydantic import BaseModel
from typing import List, Optional, Dict

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


class StreamMatchRequest(BaseModel):
    resume: Optional[Resume] = None
    job: Optional[JobDescription] = None
    resume_skill_dict: Optional[Dict[str, int]] = None
    jd_skill_dict: Optional[Dict[str, int]] = None
    skill_comparison: Optional[Dict] = None
