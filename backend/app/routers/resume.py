from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.models import User, Student, CompanyRole, CompanySkill, Skill
from app.schemas.schemas import ResumeAnalysisResponse
from app.auth.dependencies import get_current_student
from app.services.resume_parser import (
    extract_text_from_pdf, extract_text_from_txt,
    extract_skills_from_text, compare_with_company_requirements
)

router = APIRouter(prefix="/api/resume", tags=["Resume Analysis"])

@router.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    file: UploadFile = File(...),
    company_role_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    contents = await file.read()
    if file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(contents)
    elif file.filename.lower().endswith(".txt"):
        text = extract_text_from_txt(contents)
    else:
        # Try decoding as text
        text = extract_text_from_txt(contents)
        
    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from resume. Please ensure it is a valid text-based PDF or TXT file."
        )
        
    extracted = extract_skills_from_text(text)
    
    # Check target company skills if company_role_id provided
    required_skill_names = []
    if company_role_id:
        company_role = db.query(CompanyRole).filter(CompanyRole.id == company_role_id).first()
        if company_role:
            for cs in company_role.skills:
                if cs.skill:
                    required_skill_names.append(cs.skill.name)
                    
    if not required_skill_names:
        # Default standard skills
        required_skill_names = ["Java", "Python", "SQL", "DSA", "OOP", "DBMS", "REST API", "Git"]
        
    comparison = compare_with_company_requirements(
        extracted["all_skills"],
        required_skill_names
    )
    
    return ResumeAnalysisResponse(
        extracted_skills=extracted["all_skills"],
        extracted_languages=extracted["programming_languages"],
        extracted_projects=extracted["projects"],
        extracted_certifications=extracted["certifications"],
        matched_skills=comparison["matched_skills"],
        missing_skills=comparison["missing_skills"],
        match_score=comparison["match_score"],
        recommendations=comparison["recommendations"]
    )
