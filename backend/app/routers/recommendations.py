from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import User, Student, Resource, Skill
from app.auth.dependencies import get_current_student
from app.services.recommendation import get_recommended_companies

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

@router.get("/companies")
def recommend_companies(
    limit: int = 5,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    return get_recommended_companies(db, student.id, limit)

@router.get("/resources")
def get_resources(
    topic: Optional[str] = None,
    skill_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Resource)
    if topic:
        query = query.filter(Resource.topic.ilike(f"%{topic}%"))
    if skill_id:
        query = query.filter(Resource.skill_id == skill_id)
        
    resources = query.all()
    return [{
        "id": r.id,
        "topic": r.topic,
        "title": r.title,
        "resource_type": r.resource_type.value if hasattr(r.resource_type, "value") else str(r.resource_type),
        "url": r.url,
        "description": r.description,
        "is_free": r.is_free
    } for r in resources]
