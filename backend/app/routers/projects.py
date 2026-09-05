from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.database import get_db
from app.models.models import (
    User, Student, Project, StudentProject, Roadmap, RoadmapStatus
)
from app.schemas.schemas import ProjectResponse
from app.auth.dependencies import get_current_student
from app.services.readiness import calculate_readiness

router = APIRouter(prefix="/api/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
def get_all_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return [ProjectResponse(
        id=p.id,
        title=p.title,
        description=p.description,
        skills_covered=p.skills_covered,
        difficulty=p.difficulty.value if hasattr(p.difficulty, "value") else str(p.difficulty),
        duration_days=p.duration_days or 7,
        why_it_helps=p.why_it_helps,
        technologies=p.technologies
    ) for p in projects]

@router.get("/recommendations", response_model=List[ProjectResponse])
def get_recommended_projects(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    # Check active roadmap to identify weak skills
    active_roadmap = db.query(Roadmap).filter(
        Roadmap.student_id == student.id,
        Roadmap.status == RoadmapStatus.active
    ).order_by(Roadmap.id.desc()).first()
    
    weak_skill_names = []
    if active_roadmap:
        readiness = calculate_readiness(
            db, student.id, active_roadmap.company_id, active_roadmap.company_role_id
        )
        weak_skill_names = [
            g["skill_name"].lower() for g in readiness["skill_gaps"]
            if g["status"] in ("needs_improvement", "major_gap", "not_started")
        ]
        
    projects = db.query(Project).all()
    scored_projects = []
    for p in projects:
        score = 0
        p_skills = (p.skills_covered or "").lower()
        for ws in weak_skill_names:
            if ws in p_skills:
                score += 2
        scored_projects.append((score, p))
        
    scored_projects.sort(key=lambda x: x[0], reverse=True)
    top_projects = [p for _, p in scored_projects[:5]]
    
    return [ProjectResponse(
        id=p.id,
        title=p.title,
        description=p.description,
        skills_covered=p.skills_covered,
        difficulty=p.difficulty.value if hasattr(p.difficulty, "value") else str(p.difficulty),
        duration_days=p.duration_days or 7,
        why_it_helps=p.why_it_helps,
        technologies=p.technologies
    ) for p in top_projects]

@router.post("/{project_id}/save")
def save_student_project(
    project_id: int,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
        
    sp = db.query(StudentProject).filter(
        StudentProject.student_id == student.id,
        StudentProject.project_id == project_id
    ).first()
    if not sp:
        sp = StudentProject(
            student_id=student.id,
            project_id=project_id,
            status="in_progress",
            started_at=datetime.utcnow()
        )
        db.add(sp)
        db.commit()
    return {"message": "Project added to your preparation list"}

@router.get("/my")
def get_my_projects(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    sps = db.query(StudentProject).filter(StudentProject.student_id == student.id).all()
    res = []
    for sp in sps:
        p = sp.project
        if p:
            res.append({
                "id": sp.id,
                "project_id": p.id,
                "title": p.title,
                "skills_covered": p.skills_covered,
                "difficulty": p.difficulty.value if hasattr(p.difficulty, "value") else str(p.difficulty),
                "status": sp.status,
                "started_at": sp.started_at,
                "completed_at": sp.completed_at
            })
    return res
