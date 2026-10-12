from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.resume import Resume
from app.models.analysis import Analysis
from app.schemas.analysis import AnalyzeRequest, AnalysisResponse
from app.services.llm_analyzer import analyze_resume
from app.core.deps import get_current_user

from app.models.user import User

router = APIRouter()


@router.post("/{resume_id}", response_model=AnalysisResponse)
def run_analysis(resume_id: int, payload: AnalyzeRequest, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if not resume.extracted_text:
        raise HTTPException(status_code=400, detail="Resume has no extracted text")

    try:
        result = analyze_resume(resume.extracted_text, payload.job_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")

    # Upsert: ek resume ki ek hi analysis honi chahiye
    existing = db.query(Analysis).filter(Analysis.resume_id == resume_id).first()
    if existing:
        existing.match_score = result["match_score"]
        existing.skills_found = result["skills_found"]
        existing.missing_skills = result["missing_skills"]
        existing.strengths = result["strengths"]
        existing.weaknesses = result["weaknesses"]
        existing.suggestions = result["suggestions"]
        analysis = existing
    else:
        analysis = Analysis(
            resume_id=resume_id,
            match_score=result["match_score"],
            skills_found=result["skills_found"],
            missing_skills=result["missing_skills"],
            strengths=result["strengths"],
            weaknesses=result["weaknesses"],
            suggestions=result["suggestions"],
        )
        db.add(analysis)

    if payload.job_description:
        resume.job_description = payload.job_description

    db.commit()
    db.refresh(analysis)

    return AnalysisResponse(resume_id=resume_id, **result)


@router.get("/{resume_id}", response_model=AnalysisResponse)
def get_analysis(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.owner_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    analysis = db.query(Analysis).filter(Analysis.resume_id == resume_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return AnalysisResponse(
        resume_id=resume_id,
        match_score=analysis.match_score,
        skills_found=analysis.skills_found,
        missing_skills=analysis.missing_skills,
        strengths=analysis.strengths,
        weaknesses=analysis.weaknesses,
        suggestions=analysis.suggestions,
    )