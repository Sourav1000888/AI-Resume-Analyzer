from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False, unique=True)

    match_score = Column(Float, nullable=True)       # e.g. 78.0 (%)
    skills_found = Column(JSON, nullable=True)         # ["Python", "SQL", ...]
    missing_skills = Column(JSON, nullable=True)       # gaps vs job description
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    suggestions = Column(Text, nullable=True)          # improvement tips from LLM

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="analysis")