from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
import random
from typing import List, Optional
from app.database import get_db
from app.models.models import (
    User, Student, Question, QuestionOption, Test, TestQuestion, TestAnswer,
    Roadmap, RoadmapStatus, TestType, Difficulty, QuestionCategory
)
from app.schemas.schemas import (
    TestStartRequest, TestSubmitRequest, TestResultResponse, TopicPerformance,
    QuestionResponse, QuestionOptionResponse
)
from app.auth.dependencies import get_current_student
from app.services.roadmap import adapt_roadmap

router = APIRouter(prefix="/api/tests", tags=["Tests & Practice"])

@router.get("/questions", response_model=List[QuestionResponse])
def get_practice_questions(
    category: Optional[str] = None,
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(Question).filter(Question.is_active == True)
    if category:
        query = query.filter(Question.category == category)
    if topic:
        query = query.filter(Question.topic.ilike(f"%{topic}%"))
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
        
    questions = query.limit(limit).all()
    res = []
    for q in questions:
        opts = [QuestionOptionResponse(
            id=o.id,
            option_text=o.option_text,
            option_order=o.option_order
        ) for o in sorted(q.options, key=lambda x: x.option_order)]
        res.append(QuestionResponse(
            id=q.id,
            question_text=q.question_text,
            category=q.category.value if hasattr(q.category, "value") else str(q.category),
            topic=q.topic,
            difficulty=q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty),
            options=opts
        ))
    return res

@router.post("/start")
def start_test(
    req: TestStartRequest,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    query = db.query(Question).filter(Question.is_active == True)
    if req.category:
        query = query.filter(Question.category == req.category)
    if req.topic:
        query = query.filter(Question.topic.ilike(f"%{req.topic}%"))
    if req.company_id:
        # Prefer company-specific or general questions
        pass
        
    all_q = query.all()
    if not all_q:
        # Fallback to any active questions
        all_q = db.query(Question).filter(Question.is_active == True).all()
        
    if not all_q:
        raise HTTPException(status_code=400, detail="No questions available for this test configuration")
        
    selected = random.sample(all_q, min(len(all_q), req.num_questions))
    
    test = Test(
        student_id=student.id,
        company_id=req.company_id,
        role_id=req.role_id,
        test_type=TestType(req.test_type) if req.test_type in [e.value for e in TestType] else TestType.topic,
        topic=req.topic or (req.category if req.category else "Comprehensive"),
        category=req.category,
        duration_minutes=req.duration_minutes,
        total_questions=len(selected),
        started_at=datetime.utcnow()
    )
    db.add(test)
    db.flush()
    
    for idx, q in enumerate(selected):
        tq = TestQuestion(
            test_id=test.id,
            question_id=q.id,
            question_order=idx + 1
        )
        db.add(tq)
        
    db.commit()
    db.refresh(test)
    
    # Format questions to return (excluding correct flag)
    questions_data = []
    for q in selected:
        opts = [{"id": o.id, "option_text": o.option_text, "option_order": o.option_order} 
                for o in sorted(q.options, key=lambda x: x.option_order)]
        questions_data.append({
            "id": q.id,
            "question_text": q.question_text,
            "category": q.category.value if hasattr(q.category, "value") else str(q.category),
            "topic": q.topic,
            "difficulty": q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty),
            "options": opts
        })
        
    return {
        "test_id": test.id,
        "duration_minutes": test.duration_minutes,
        "total_questions": len(selected),
        "questions": questions_data
    }

@router.post("/{test_id}/submit", response_model=TestResultResponse)
def submit_test(
    test_id: int,
    req: TestSubmitRequest,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    test = db.query(Test).filter(Test.id == test_id, Test.student_id == student.id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
        
    correct_count = 0
    wrong_count = 0
    topic_map = {} # topic -> {correct, total}
    
    for ans in req.answers:
        q = db.query(Question).filter(Question.id == ans.question_id).first()
        if not q:
            continue
            
        topic = q.topic or (q.category.value if hasattr(q.category, "value") else str(q.category))
        if topic not in topic_map:
            topic_map[topic] = {"correct": 0, "total": 0}
        topic_map[topic]["total"] += 1
        
        is_correct = False
        if ans.selected_option_id:
            opt = db.query(QuestionOption).filter(
                QuestionOption.id == ans.selected_option_id,
                QuestionOption.question_id == q.id
            ).first()
            if opt and opt.is_correct:
                is_correct = True
                
        if is_correct:
            correct_count += 1
            topic_map[topic]["correct"] += 1
        else:
            wrong_count += 1
            
        ta = TestAnswer(
            test_id=test.id,
            question_id=q.id,
            selected_option_id=ans.selected_option_id,
            is_correct=is_correct,
            time_taken_seconds=ans.time_taken_seconds
        )
        db.add(ta)
        
    total_answered = len(req.answers)
    score_pct = round((correct_count / total_answered * 100) if total_answered > 0 else 0.0, 1)
    
    test.submitted_at = datetime.utcnow()
    test.total_score = score_pct
    test.accuracy = score_pct
    test.correct_count = correct_count
    test.wrong_count = wrong_count
    
    time_taken_min = round(
        (test.submitted_at - test.started_at).total_seconds() / 60.0, 1
    ) if test.started_at else 0.0
    
    # Topic breakdown
    topic_perf = []
    weak_areas = []
    for t_name, stats in topic_map.items():
        t_score = round((stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0.0, 1)
        topic_perf.append(TopicPerformance(
            topic=t_name,
            correct=stats["correct"],
            total=stats["total"],
            score=t_score
        ))
        if t_score < 60:
            weak_areas.append(t_name)
            
    # Check if student has active roadmap and trigger adaptation
    roadmap_adapted = False
    active_roadmap = db.query(Roadmap).filter(
        Roadmap.student_id == student.id,
        Roadmap.status == RoadmapStatus.active
    ).order_by(Roadmap.id.desc()).first()
    
    if active_roadmap and test.topic:
        adapt_res = adapt_roadmap(db, student.id, active_roadmap.id, test.topic, score_pct)
        roadmap_adapted = adapt_res.get("adapted", False)
        
    db.commit()
    db.refresh(test)
    
    return TestResultResponse(
        test_id=test.id,
        total_score=test.total_score,
        accuracy=test.accuracy,
        correct_count=test.correct_count,
        wrong_count=test.wrong_count,
        total_questions=test.total_questions or total_answered,
        time_taken_minutes=time_taken_min,
        topic_performance=topic_perf,
        weak_areas=weak_areas,
        roadmap_adapted=roadmap_adapted
    )

@router.get("/{test_id}/results")
def get_test_results(
    test_id: int,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    test = db.query(Test).filter(Test.id == test_id, Test.student_id == student.id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
        
    answers = db.query(TestAnswer).filter(TestAnswer.test_id == test.id).all()
    review = []
    for a in answers:
        q = a.question
        correct_opt = next((o for o in q.options if o.is_correct), None)
        review.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "category": q.category.value if hasattr(q.category, "value") else str(q.category),
            "topic": q.topic,
            "selected_option_id": a.selected_option_id,
            "selected_option_text": a.selected_option.option_text if a.selected_option else "Unanswered",
            "correct_option_id": correct_opt.id if correct_opt else None,
            "correct_option_text": correct_opt.option_text if correct_opt else None,
            "is_correct": a.is_correct,
            "explanation": q.explanation
        })
        
    return {
        "test_id": test.id,
        "score": test.total_score,
        "accuracy": test.accuracy,
        "correct_count": test.correct_count,
        "wrong_count": test.wrong_count,
        "review": review
    }

@router.get("/history")
def get_test_history(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    tests = db.query(Test).filter(
        Test.student_id == student.id,
        Test.submitted_at.isnot(None)
    ).order_by(Test.submitted_at.desc()).all()
    
    return [{
        "id": t.id,
        "topic": t.topic,
        "score": t.total_score,
        "accuracy": t.accuracy,
        "total_questions": t.total_questions,
        "date": t.submitted_at
    } for t in tests]
