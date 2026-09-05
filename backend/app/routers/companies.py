from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import Company, CompanyRole, RecruitmentRound, CompanySkill, Role, Skill
from app.schemas.schemas import (
    CompanyResponse, CompanyListResponse, RecruitmentRoundResponse,
    CompanyRoleResponse, CompanySkillResponse, RoleResponse, RoundSkillInfo
)
from app.services.readiness import LEVEL_LABELS

router = APIRouter(prefix="/api/companies", tags=["Companies"])

@router.get("", response_model=List[CompanyListResponse])
def get_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).filter(Company.is_active == True).all()
    res = []
    for c in companies:
        role_count = len([r for r in c.roles if r.is_active])
        res.append(CompanyListResponse(
            id=c.id,
            name=c.name,
            logo_color=c.logo_color or "#4f46e5",
            logo_initials=c.logo_initials or c.name[:3].upper(),
            description=c.description,
            industry=c.industry,
            difficulty=c.difficulty.value if hasattr(c.difficulty, "value") else str(c.difficulty),
            min_cgpa=c.min_cgpa or 6.0,
            role_count=role_count
        ))
    return res

@router.get("/search")
def search_companies(q: str = Query("", min_length=1), db: Session = Depends(get_db)):
    companies = db.query(Company).filter(
        Company.name.ilike(f"%{q}%"),
        Company.is_active == True
    ).all()
    return [{
        "id": c.id,
        "name": c.name,
        "industry": c.industry,
        "difficulty": c.difficulty.value if hasattr(c.difficulty, "value") else str(c.difficulty)
    } for c in companies]

@router.get("/{id}", response_model=CompanyResponse)
def get_company(id: int, db: Session = Depends(get_db)):
    c = db.query(Company).filter(Company.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Company not found")
        
    roles_res = []
    for cr in c.roles:
        if not cr.is_active:
            continue
        skills_res = []
        for cs in cr.skills:
            if cs.skill:
                skills_res.append(CompanySkillResponse(
                    skill_id=cs.skill.id,
                    skill_name=cs.skill.name,
                    skill_category=cs.skill.category,
                    required_level=cs.required_level,
                    required_level_label=LEVEL_LABELS.get(cs.required_level, "Unknown"),
                    weight=cs.weight or 1.0
                ))
        roles_res.append(CompanyRoleResponse(
            id=cr.id,
            role_id=cr.role_id,
            role_name=cr.role.name if cr.role else "Role",
            notes=cr.notes,
            skills=skills_res
        ))
        
    rounds_res = []
    sorted_rounds = sorted(c.rounds, key=lambda x: x.round_number)
    for r in sorted_rounds:
        round_skills = []
        for rs in r.skills:
            if rs.skill:
                round_skills.append(RoundSkillInfo(
                    skill_id=rs.skill.id,
                    skill_name=rs.skill.name,
                    importance=rs.importance or 3
                ))
        rounds_res.append(RecruitmentRoundResponse(
            id=r.id,
            round_number=r.round_number,
            name=r.name,
            description=r.description,
            difficulty=r.difficulty.value if hasattr(r.difficulty, "value") else str(r.difficulty),
            estimated_days=r.estimated_days or 3,
            tips=r.tips,
            skills=round_skills
        ))

    return CompanyResponse(
        id=c.id,
        name=c.name,
        logo_color=c.logo_color or "#4f46e5",
        logo_initials=c.logo_initials or c.name[:3].upper(),
        description=c.description,
        industry=c.industry,
        difficulty=c.difficulty.value if hasattr(c.difficulty, "value") else str(c.difficulty),
        min_cgpa=c.min_cgpa or 6.0,
        eligibility_notes=c.eligibility_notes,
        website=c.website,
        is_active=c.is_active,
        roles=roles_res,
        rounds=rounds_res
    )

@router.get("/{id}/roles")
def get_company_roles(id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    roles = []
    for cr in company.roles:
        if cr.is_active and cr.role:
            roles.append({
                "company_role_id": cr.id,
                "role_id": cr.role.id,
                "role_name": cr.role.name,
                "description": cr.role.description,
                "skills_count": len(cr.skills)
            })
    return roles

@router.get("/{id}/rounds")
def get_company_rounds(id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    rounds = sorted(company.rounds, key=lambda x: x.round_number)
    return [{
        "id": r.id,
        "round_number": r.round_number,
        "name": r.name,
        "description": r.description,
        "difficulty": r.difficulty.value if hasattr(r.difficulty, "value") else str(r.difficulty),
        "estimated_days": r.estimated_days,
        "tips": r.tips
    } for r in rounds]
