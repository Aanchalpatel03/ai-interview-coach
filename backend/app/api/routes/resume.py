from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.resume import ResumeAnalysisResponse
from app.services.resume_service import extract_skills_from_resume, suggested_roles, validate_resume_file
from app.services.storage_service import upload_resume_stub

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        await validate_resume_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    resume_url = upload_resume_stub(current_user.id, file.filename)
    skills = extract_skills_from_resume(file.filename)
    current_user.resume_url = resume_url
    current_user.extracted_skills = ",".join(skills)
    db.add(current_user)
    db.commit()
    return {"resume_url": resume_url, "skills": skills}


@router.get("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(current_user=Depends(get_current_user)):
    skills = (current_user.extracted_skills or "").split(",") if current_user.extracted_skills else []
    return ResumeAnalysisResponse(
        resume_url=current_user.resume_url,
        extracted_skills=skills,
        suggested_roles=suggested_roles(skills),
    )
