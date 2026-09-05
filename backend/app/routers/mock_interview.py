from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.database import get_db
from app.models.models import (
    User, Student, Company, Role, MockInterview, InterviewMessage
)
from app.schemas.schemas import (
    InterviewStartRequest, InterviewMessageRequest, InterviewResponse,
    InterviewEndResponse, InterviewMessageResponse
)
from app.auth.dependencies import get_current_student
from app.services.ai_service import ai_service, INTERVIEW_FLOW

router = APIRouter(prefix="/api/interviews", tags=["Mock Interview"])

@router.post("/start")
def start_interview(
    req: InterviewStartRequest,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    company = db.query(Company).filter(Company.id == req.company_id).first() if req.company_id else None
    role = db.query(Role).filter(Role.id == req.role_id).first() if req.role_id else None
    
    interview = MockInterview(
        student_id=student.id,
        company_id=req.company_id,
        role_id=req.role_id,
        interview_type=req.interview_type,
        started_at=datetime.utcnow(),
        ai_mode=ai_service.is_ai_mode()
    )
    db.add(interview)
    db.flush()
    
    company_name = company.name if company else "our engineering team"
    role_name = role.name if role else "Software Engineer"
    
    first_msg_text = (
        f"Hello {student.full_name}! Welcome to your technical mock interview for the {role_name} role at {company_name}. "
        f"I will be evaluating your technical skills, clarity, and communication today. "
        f"To kick things off: Could you please tell me about yourself and your background in computer science?"
    )
    
    first_msg = InterviewMessage(
        interview_id=interview.id,
        role="ai",
        content=first_msg_text
    )
    db.add(first_msg)
    db.commit()
    db.refresh(interview)
    
    return {
        "interview_id": interview.id,
        "ai_message": first_msg_text,
        "is_completed": False
    }

@router.post("/{interview_id}/message")
def send_interview_message(
    interview_id: int,
    req: InterviewMessageRequest,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    interview = db.query(MockInterview).filter(
        MockInterview.id == interview_id,
        MockInterview.student_id == student.id
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview.is_completed:
        raise HTTPException(status_code=400, detail="Interview is already completed")
        
    # Save student response
    student_msg = InterviewMessage(
        interview_id=interview.id,
        role="student",
        content=req.content
    )
    db.add(student_msg)
    db.flush()
    
    # Check total student messages so far
    all_msgs = db.query(InterviewMessage).filter(InterviewMessage.interview_id == interview.id).all()
    student_count = len([m for m in all_msgs if m.role == "student"])
    
    company_name = interview.company.name if interview.company else None
    role_name = interview.role.name if interview.role else None
    
    # Determine phase based on message count
    phase_idx = min(student_count, len(INTERVIEW_FLOW) - 1)
    phase = INTERVIEW_FLOW[phase_idx]
    
    history = [{"role": m.role, "content": m.content} for m in all_msgs]
    
    if student_count >= 6:
        # Wrap up interview
        ai_reply = (
            "Thank you for sharing your thoughts and technical answers! That concludes our mock interview session today. "
            "Please click the 'Finish & Get Detailed Evaluation' button above to review your score, strengths, and actionable feedback."
        )
        is_done = True
    else:
        ai_reply = ai_service.generate_interview_question(
            phase=phase,
            company=company_name,
            role=role_name,
            weak_topics=["DSA", "System Design"],
            conversation_history=history,
            interview_type=interview.interview_type
        )
        is_done = False
        
    ai_msg = InterviewMessage(
        interview_id=interview.id,
        role="ai",
        content=ai_reply
    )
    db.add(ai_msg)
    db.commit()
    
    return {
        "interview_id": interview.id,
        "ai_message": ai_reply,
        "is_completed": is_done
    }

@router.post("/{interview_id}/end", response_model=InterviewEndResponse)
def end_interview(
    interview_id: int,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    interview = db.query(MockInterview).filter(
        MockInterview.id == interview_id,
        MockInterview.student_id == student.id
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
        
    all_msgs = db.query(InterviewMessage).filter(
        InterviewMessage.interview_id == interview.id
    ).order_by(InterviewMessage.created_at.asc()).all()
    
    company_name = interview.company.name if interview.company else None
    role_name = interview.role.name if interview.role else None
    
    history = [{"role": m.role, "content": m.content} for m in all_msgs]
    eval_res = ai_service.evaluate_interview(company_name, role_name, history)
    
    interview.is_completed = True
    interview.ended_at = datetime.utcnow()
    interview.tech_score = eval_res.get("tech_score", 75.0)
    interview.comm_score = eval_res.get("comm_score", 75.0)
    interview.relevance_score = eval_res.get("relevance_score", 75.0)
    interview.overall_score = eval_res.get("overall_score", 75.0)
    interview.feedback = eval_res.get("feedback", "Good performance overall.")
    interview.suggestions = eval_res.get("suggestions", "Keep practicing core concepts.")
    
    db.commit()
    db.refresh(interview)
    
    return InterviewEndResponse(
        interview_id=interview.id,
        tech_score=interview.tech_score,
        comm_score=interview.comm_score,
        relevance_score=interview.relevance_score,
        overall_score=interview.overall_score,
        feedback=interview.feedback,
        suggestions=interview.suggestions,
        messages=[InterviewMessageResponse(
            role=m.role,
            content=m.content,
            created_at=m.created_at
        ) for m in all_msgs]
    )

@router.get("/{interview_id}")
def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    interview = db.query(MockInterview).filter(
        MockInterview.id == interview_id,
        MockInterview.student_id == student.id
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
        
    msgs = db.query(InterviewMessage).filter(
        InterviewMessage.interview_id == interview.id
    ).order_by(InterviewMessage.created_at.asc()).all()
    
    return {
        "id": interview.id,
        "company_name": interview.company.name if interview.company else None,
        "role_name": interview.role.name if interview.role else None,
        "is_completed": interview.is_completed,
        "overall_score": interview.overall_score,
        "tech_score": interview.tech_score,
        "comm_score": interview.comm_score,
        "feedback": interview.feedback,
        "suggestions": interview.suggestions,
        "messages": [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in msgs]
    }
