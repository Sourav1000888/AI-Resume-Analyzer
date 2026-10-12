from pydantic import BaseModel
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    job_description: Optional[str] = None


class AnalysisResponse(BaseModel):
    resume_id: int
    match_score: float
    skills_found: List[str]
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: str

    class Config:
        from_attributes = True