from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import (
    User, Student, Company, Role, CompanyRole, CompanySkill,
    RecruitmentRound, RoundSkill, Question, QuestionOption,
    Test, Roadmap, ReadinessWeight, Resource, Difficulty, QuestionCategory
)
from app.schemas.schemas import (
    AdminStatsResponse, CompanyCreate, CompanyUpdate, QuestionCreate,
    ReadinessWeightUpdate, CompanyRoleCreate, RecruitmentRoundCreate
)
from app.auth.dependencies import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin Operations"])

@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    students_count = db.query(Student).count()
    companies_count = db.query(Company).filter(Company.is_active == True).count()
    questions_count = db.query(Question).filter(Question.is_active == True).count()
    roadmaps_count = db.query(Roadmap).count()
    tests_count = db.query(Test).filter(Test.submitted_at.isnot(None)).count()
    
    tests = db.query(Test).filter(Test.submitted_at.isnot(None)).all()
    avg_score = round(sum(t.total_score or 0 for t in tests) / len(tests), 1) if tests else 74.5

    return AdminStatsResponse(
        total_students=students_count,
        total_companies=companies_count,
        total_questions=questions_count,
        active_roadmaps=roadmaps_count,
        completed_tests=tests_count,
        avg_readiness=avg_score
    )

@router.get("/students")
def get_all_students(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    students = db.query(Student).all()
    return [{
        "id": s.id,
        "name": s.full_name,
        "email": s.user.email if s.user else None,
        "college": s.college,
        "branch": s.branch,
        "cgpa": s.cgpa,
        "graduation_year": s.graduation_year,
        "preferred_role": s.preferred_role,
        "roadmaps_count": len(s.roadmaps),
        "tests_count": len(s.tests)
    } for s in students]

@router.post("/companies")
def create_company(
    req: CompanyCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    c = Company(
        name=req.name,
        logo_color=req.logo_color or "#4f46e5",
        logo_initials=req.logo_initials or req.name[:3].upper(),
        description=req.description,
        industry=req.industry,
        difficulty=Difficulty(req.difficulty) if req.difficulty in [e.value for e in Difficulty] else Difficulty.medium,
        min_cgpa=req.min_cgpa or 6.0,
        eligibility_notes=req.eligibility_notes,
        website=req.website,
        is_active=True
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"message": "Company created successfully", "id": c.id}

@router.put("/companies/{id}")
def update_company(
    id: int,
    req: CompanyUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    c = db.query(Company).filter(Company.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Company not found")
        
    for k, v in req.dict(exclude_unset=True).items():
        if k == "difficulty" and v:
            c.difficulty = Difficulty(v) if v in [e.value for e in Difficulty] else c.difficulty
        else:
            setattr(c, k, v)
            
    db.commit()
    return {"message": "Company updated successfully"}

@router.delete("/companies/{id}")
def delete_company(
    id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    c = db.query(Company).filter(Company.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Company not found")
    c.is_active = False
    db.commit()
    return {"message": "Company deactivated successfully"}

@router.post("/companies/{id}/roles")
def add_company_role(
    id: int,
    req: CompanyRoleCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    cr = CompanyRole(
        company_id=id,
        role_id=req.role_id,
        notes=req.notes,
        is_active=True
    )
    db.add(cr)
    db.flush()
    
    for s_info in req.skills:
        cs = CompanySkill(
            company_role_id=cr.id,
            skill_id=s_info["skill_id"],
            required_level=s_info.get("required_level", 3),
            weight=s_info.get("weight", 1.0)
        )
        db.add(cs)
        
    db.commit()
    return {"message": "Role added to company successfully", "id": cr.id}

@router.post("/companies/{id}/rounds")
def add_company_round(
    id: int,
    req: RecruitmentRoundCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    rr = RecruitmentRound(
        company_id=id,
        round_number=req.round_number,
        name=req.name,
        description=req.description,
        difficulty=Difficulty(req.difficulty) if req.difficulty in [e.value for e in Difficulty] else Difficulty.medium,
        estimated_days=req.estimated_days,
        tips=req.tips
    )
    db.add(rr)
    db.flush()
    
    for s_id in req.skill_ids:
        rs = RoundSkill(
            round_id=rr.id,
            skill_id=s_id,
            importance=3
        )
        db.add(rs)
        
    db.commit()
    return {"message": "Recruitment round created successfully", "id": rr.id}

@router.get("/questions")
def get_all_questions(
    category: Optional[str] = None,
    limit: int = 50,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Question)
    if category:
        query = query.filter(Question.category == category)
    questions = query.limit(limit).all()
    
    return [{
        "id": q.id,
        "question_text": q.question_text,
        "category": q.category.value if hasattr(q.category, "value") else str(q.category),
        "topic": q.topic,
        "difficulty": q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty),
        "options_count": len(q.options),
        "is_active": q.is_active
    } for q in questions]

@router.post("/questions")
def create_question(
    req: QuestionCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    q = Question(
        question_text=req.question_text,
        category=QuestionCategory(req.category) if req.category in [e.value for e in QuestionCategory] else QuestionCategory.technical,
        topic=req.topic,
        difficulty=Difficulty(req.difficulty) if req.difficulty in [e.value for e in Difficulty] else Difficulty.medium,
        explanation=req.explanation,
        company_id=req.company_id,
        role_id=req.role_id,
        is_active=True
    )
    db.add(q)
    db.flush()
    
    for idx, opt_data in enumerate(req.options):
        opt = QuestionOption(
            question_id=q.id,
            option_text=opt_data["option_text"],
            is_correct=opt_data.get("is_correct", False),
            option_order=idx + 1
        )
        db.add(opt)
        
    db.commit()
    return {"message": "Question created successfully", "id": q.id}

@router.delete("/questions/{id}")
def delete_question(
    id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    q = db.query(Question).filter(Question.id == id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    q.is_active = False
    db.commit()
    return {"message": "Question deactivated successfully"}

@router.get("/weights")
def get_readiness_weights(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    weights = db.query(ReadinessWeight).all()
    return [{
        "category": w.category,
        "weight_pct": w.weight_pct,
        "description": w.description
    } for w in weights]

@router.put("/weights")
def update_readiness_weights(
    updates: List[ReadinessWeightUpdate],
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    for u in updates:
        w = db.query(ReadinessWeight).filter(ReadinessWeight.category == u.category).first()
        if w:
            w.weight_pct = u.weight_pct
            if u.description:
                w.description = u.description
        else:
            new_w = ReadinessWeight(
                category=u.category,
                weight_pct=u.weight_pct,
                description=u.description
            )
            db.add(new_w)
    db.commit()
    return {"message": "Readiness weights updated successfully"}
