from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.database import get_db
from app.models.models import (
    User, Student, Roadmap, RoadmapTask, RoadmapWeek, RoadmapStatus, TaskStatus
)
from app.schemas.schemas import (
    RoadmapGenerateRequest, RoadmapResponse, WeekResponse, TaskResponse, TaskUpdateRequest
)
from app.auth.dependencies import get_current_student
from app.services.roadmap import generate_roadmap, get_completion_percentage, adapt_roadmap

router = APIRouter(prefix="/api/roadmap", tags=["Roadmap"])

def format_roadmap(r: Roadmap) -> RoadmapResponse:
    weeks_res = []
    sorted_weeks = sorted(r.weeks, key=lambda w: w.week_number)
    for w in sorted_weeks:
        tasks_res = []
        sorted_tasks = sorted(w.tasks, key=lambda t: (t.day_number, t.id))
        for t in sorted_tasks:
            tasks_res.append(TaskResponse(
                id=t.id,
                day_number=t.day_number,
                title=t.title,
                description=t.description,
                topic=t.topic,
                category=t.category,
                difficulty=t.difficulty.value if hasattr(t.difficulty, "value") else str(t.difficulty),
                estimated_minutes=t.estimated_minutes,
                status=t.status.value if hasattr(t.status, "value") else str(t.status),
                score=t.score,
                completed_at=t.completed_at
            ))
        weeks_res.append(WeekResponse(
            id=w.id,
            week_number=w.week_number,
            theme=w.theme or f"Week {w.week_number}",
            focus_areas=w.focus_areas,
            tasks=tasks_res
        ))
        
    return RoadmapResponse(
        id=r.id,
        student_id=r.student_id,
        company_id=r.company_id,
        company_role_id=r.company_role_id,
        company_name=r.company.name if r.company else "Target Company",
        role_name=r.company_role.role.name if r.company_role and r.company_role.role else "Target Role",
        start_date=r.start_date,
        end_date=r.end_date,
        total_days=r.total_days,
        daily_hours=r.daily_hours,
        status=r.status.value if hasattr(r.status, "value") else str(r.status),
        completion_pct=get_completion_percentage(r),
        weeks=weeks_res
    )

@router.post("/generate", response_model=RoadmapResponse)
def create_roadmap(
    req: RoadmapGenerateRequest,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    roadmap = generate_roadmap(
        db=db,
        student_id=student.id,
        company_id=req.company_id,
        company_role_id=req.company_role_id,
        total_days=req.total_days,
        daily_hours=req.daily_hours,
        exam_date=req.exam_date
    )
    return format_roadmap(roadmap)

@router.get("/current", response_model=RoadmapResponse)
def get_current_roadmap(
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
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="No active roadmap found. Please select a company and generate one.")
        
    return format_roadmap(roadmap)

@router.get("/{roadmap_id}", response_model=RoadmapResponse)
def get_roadmap_by_id(
    roadmap_id: int,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    roadmap = db.query(Roadmap).filter(
        Roadmap.id == roadmap_id,
        Roadmap.student_id == student.id
    ).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    return format_roadmap(roadmap)

@router.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    req: TaskUpdateRequest,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    task = db.query(RoadmapTask).filter(RoadmapTask.id == task_id).first()
    if not task or task.roadmap.student_id != student.id:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if req.status:
        try:
            task.status = TaskStatus(req.status)
        except Exception:
            task.status = TaskStatus.completed if req.status == "completed" else TaskStatus.pending
            
        if req.status == "completed":
            task.completed_at = datetime.utcnow()
            
    if req.score is not None:
        task.score = req.score
        # Check if adaptive update is needed
        if task.topic:
            adapt_roadmap(db, student.id, task.roadmap_id, task.topic, req.score)
            
    if req.notes is not None:
        task.notes = req.notes
        
    db.commit()
    db.refresh(task)
    return {
        "id": task.id,
        "status": task.status.value if hasattr(task.status, "value") else str(task.status),
        "score": task.score,
        "completed_at": task.completed_at
    }

@router.get("/tasks/today", response_model=List[TaskResponse])
def get_today_tasks(
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
    
    if not roadmap:
        return []
        
    # Calculate day number based on start_date
    delta_days = (datetime.utcnow() - roadmap.start_date).days + 1
    current_day = max(1, min(delta_days, roadmap.total_days))
    
    tasks = db.query(RoadmapTask).filter(
        RoadmapTask.roadmap_id == roadmap.id,
        RoadmapTask.day_number == current_day
    ).all()
    
    # If no tasks for that exact day or already completed, return pending tasks
    if not tasks or all(t.status.value == "completed" or t.status == "completed" for t in tasks):
        pending_tasks = db.query(RoadmapTask).filter(
            RoadmapTask.roadmap_id == roadmap.id,
            RoadmapTask.status == TaskStatus.pending
        ).order_by(RoadmapTask.day_number.asc()).limit(5).all()
        if pending_tasks:
            tasks = pending_tasks

    return [TaskResponse(
        id=t.id,
        day_number=t.day_number,
        title=t.title,
        description=t.description,
        topic=t.topic,
        category=t.category,
        difficulty=t.difficulty.value if hasattr(t.difficulty, "value") else str(t.difficulty),
        estimated_minutes=t.estimated_minutes,
        status=t.status.value if hasattr(t.status, "value") else str(t.status),
        score=t.score,
        completed_at=t.completed_at
    ) for t in tasks]
