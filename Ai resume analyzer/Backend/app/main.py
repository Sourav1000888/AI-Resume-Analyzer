from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.routers import resume
from app.routers import auth
from app.routers import analysis
from app import models  # noqa: F401  -> ensures models are registered before create_all

app = FastAPI(
    title="AI Resume Analyzer + ATS",
    description="LLM-powered resume analysis and applicant tracking system",
    version="1.0.0",
)

# Allow frontend (React/Next.js) to call this API during development.
# Tighten allow_origins before deploying to production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#router
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])

Base.metadata.create_all(bind=engine)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Resume Analyzer API is running"}



