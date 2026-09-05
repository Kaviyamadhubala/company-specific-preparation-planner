from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import (
    User, Student, StudentSkill, Skill, Notification, Test, Roadmap, RoadmapStatus
)
from app.schemas.schemas import (
    StudentProfileResponse, StudentProfileUpdate, StudentSkillResponse,
    BulkSkillUpdate, NotificationResponse
)
from app.auth.dependencies import get_current_user, get_current_student
from app.services.readiness import LEVEL_LABELS

router = APIRouter(prefix="/api/students", tags=["Students"])

@router.get("/profile", response_model=StudentProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    return StudentProfileResponse(
        id=student.id,
        user_id=student.user_id,
        full_name=student.full_name,
        college=student.college,
        degree=student.degree,
        branch=student.branch,
        graduation_year=student.graduation_year,
        cgpa=student.cgpa,
        phone=student.phone,
        location=student.location,
        daily_hours=student.daily_hours or 2.0,
        preferred_role=student.preferred_role,
        preferred_location=student.preferred_location,
        bio=student.bio,
        profile_completed=student.profile_completed,
        email=current_user.email
    )

@router.put("/profile", response_model=StudentProfileResponse)
def update_profile(
    req: StudentProfileUpdate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    for field, val in req.dict(exclude_unset=True).items():
        setattr(student, field, val)
        
    # Mark profile completed if core fields are filled
    if student.college and student.degree and student.cgpa:
        student.profile_completed = True
        
    db.commit()
    db.refresh(student)
    
    return StudentProfileResponse(
        id=student.id,
        user_id=student.user_id,
        full_name=student.full_name,
        college=student.college,
        degree=student.degree,
        branch=student.branch,
        graduation_year=student.graduation_year,
        cgpa=student.cgpa,
        phone=student.phone,
        location=student.location,
        daily_hours=student.daily_hours or 2.0,
        preferred_role=student.preferred_role,
        preferred_location=student.preferred_location,
        bio=student.bio,
        profile_completed=student.profile_completed,
        email=current_user.email
    )

@router.get("/skills", response_model=List[StudentSkillResponse])
def get_student_skills(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    skills = db.query(StudentSkill).filter(StudentSkill.student_id == student.id).all()
    res = []
    for ss in skills:
        skill = ss.skill
        if skill:
            res.append(StudentSkillResponse(
                id=ss.id,
                skill_id=skill.id,
                skill_name=skill.name,
                skill_category=skill.category,
                level=ss.level,
                level_label=LEVEL_LABELS.get(ss.level, "Not Started")
            ))
    return res

@router.put("/skills")
def update_student_skills(
    req: BulkSkillUpdate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    for item in req.skills:
        ss = db.query(StudentSkill).filter(
            StudentSkill.student_id == student.id,
            StudentSkill.skill_id == item.skill_id
        ).first()
        if ss:
            ss.level = item.level
        else:
            new_ss = StudentSkill(
                student_id=student.id,
                skill_id=item.skill_id,
                level=item.level
            )
            db.add(new_ss)
            
    db.commit()
    return {"message": "Skills updated successfully", "count": len(req.skills)}

@router.get("/stats")
def get_student_stats(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    roadmap = db.query(Roadmap).filter(
        Roadmap.student_id == student.id,
        Roadmap.status == RoadmapStatus.active
    ).order_by(Roadmap.id.desc()).first()
    
    completion_pct = 0.0
    if roadmap and roadmap.tasks:
        done = sum(1 for t in roadmap.tasks if t.status.value == "completed" or t.status == "completed")
        completion_pct = round((done / len(roadmap.tasks)) * 100, 1)
        
    tests = db.query(Test).filter(
        Test.student_id == student.id,
        Test.submitted_at.isnot(None)
    ).all()
    avg_score = round(sum(t.total_score or 0 for t in tests) / len(tests), 1) if tests else 0.0
    
    study_hours = 0.0
    if roadmap and roadmap.tasks:
        completed_tasks = [t for t in roadmap.tasks if t.status.value == "completed" or t.status == "completed"]
        study_hours = round(sum((t.estimated_minutes or 60) for t in completed_tasks) / 60.0, 1)
        
    return {
        "roadmap_completion": completion_pct,
        "practice_test_average": avg_score,
        "completed_tests_count": len(tests),
        "study_hours": study_hours,
        "target_company": roadmap.company.name if roadmap and roadmap.company else None,
        "target_role": roadmap.company_role.role.name if roadmap and roadmap.company_role and roadmap.company_role.role else None
    }

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    notifs = db.query(Notification).filter(
        Notification.student_id == student.id
    ).order_by(Notification.created_at.desc()).limit(20).all()
    return notifs

@router.put("/notifications/{id}/read")
def mark_notification_read(
    id: int,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    notif = db.query(Notification).filter(
        Notification.id == id,
        Notification.student_id == student.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"message": "Marked as read"}
