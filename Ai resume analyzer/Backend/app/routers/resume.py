import os
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.resume import Resume  # it is a table
from app.services.parser import extract_resume_text
from app.schemas.resume import ResumeUploadResponse

from app.core.deps import get_current_user
from app.models.user import User

from typing import Optional
from app.models.analysis import Analysis
from app.schemas.resume import ResumeListResponse, ResumeListItem
from pydantic import BaseModel

router = APIRouter()

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE_MB = 5


@router.post("/upload", response_model=ResumeUploadResponse)
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"File too large (max {MAX_FILE_SIZE_MB}MB)")

    try:
        extracted_text = extract_resume_text(file_path)
    except ValueError as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(e))

    if not extracted_text:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Could not extract text — file may be scanned/image-based")

    # TODO: replace owner_id=1 with real logged-in user once auth (Step X) is built
    resume = Resume(
        owner_id=current_user.id,
        file_name=file.filename,
        file_path=file_path,
        extracted_text=extracted_text,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return ResumeUploadResponse(
        id=resume.id,
        file_name=resume.file_name,
        extracted_text_preview=extracted_text[:300],
        message="Resume uploaded and parsed successfully",
    )



@router.get("/", response_model=ResumeListResponse)
def list_resumes(
    search: Optional[str] = None,       # search by file name
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Resume).filter(Resume.owner_id == current_user.id)


    if search:
        query = query.filter(Resume.file_name.ilike(f"%{search}%"))

    total = query.count()
    resumes = query.order_by(Resume.uploaded_at.desc()).offset(skip).limit(limit).all()

    result = []
    for r in resumes:
        analysis = db.query(Analysis).filter(Analysis.resume_id == r.id).first()
        result.append(
            ResumeListItem(
                id=r.id,
                file_name=r.file_name,
                uploaded_at=r.uploaded_at,
                match_score=analysis.match_score if analysis else None,
            )
        )

    return ResumeListResponse(total=total, resumes=result)










