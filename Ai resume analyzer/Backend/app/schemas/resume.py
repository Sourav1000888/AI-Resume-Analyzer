from pydantic import BaseModel
from datetime import datetime


class ResumeResponse(BaseModel):
    id: int
    file_name: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class ResumeUploadResponse(BaseModel):
    id: int
    file_name: str
    extracted_text_preview: str
    message: str


from typing import List, Optional


class ResumeListItem(BaseModel):
    id: int
    file_name: str
    uploaded_at: datetime
    match_score: Optional[float] = None

    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    total: int
    resumes: List[ResumeListItem]