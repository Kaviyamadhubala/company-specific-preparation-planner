from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import User, Student, Company, CompanyRole
from app.schemas.schemas import ReadinessResponse
from app.auth.dependencies import get_current_student
from app.services.readiness import calculate_readiness

router = APIRouter(prefix="/api/readiness", tags=["Readiness"])

@router.get("/{company_id}/{company_role_id}", response_model=ReadinessResponse)
def get_readiness_score(
    company_id: int,
    company_role_id: int,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    company_role = db.query(CompanyRole).filter(
        CompanyRole.id == company_role_id,
        CompanyRole.company_id == company_id
    ).first()
    if not company_role:
        raise HTTPException(status_code=404, detail="Company role not found")
        
    result = calculate_readiness(db, student.id, company_id, company_role_id)
    return result

@router.get("/compare/all")
def compare_all_companies(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    companies = db.query(Company).filter(Company.is_active == True).all()
    results = []
    
    for c in companies:
        best_score = 0.0
        best_role_name = ""
        best_gaps = []
        
        for cr in c.roles:
            if not cr.is_active:
                continue
            readiness = calculate_readiness(db, student.id, c.id, cr.id)
            if readiness["overall_score"] >= best_score:
                best_score = readiness["overall_score"]
                best_role_name = cr.role.name if cr.role else "Role"
                best_gaps = readiness.get("top_weak_areas", [])
                
        results.append({
            "company_id": c.id,
            "company_name": c.name,
            "logo_color": c.logo_color or "#4f46e5",
            "logo_initials": c.logo_initials or c.name[:3].upper(),
            "industry": c.industry,
            "difficulty": c.difficulty.value if hasattr(c.difficulty, "value") else str(c.difficulty),
            "readiness_score": best_score,
            "target_role": best_role_name,
            "weak_areas": best_gaps[:2]
        })
        
    results.sort(key=lambda x: x["readiness_score"], reverse=True)
    return results
