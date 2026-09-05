from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Student, UserRole
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse, StudentProfileResponse
from app.auth.jwt import verify_password, get_password_hash, create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    
    user = User(
        email=req.email.lower(),
        password_hash=get_password_hash(req.password),
        role=UserRole.student,
        is_active=True
    )
    db.add(user)
    db.flush()
    
    student = Student(
        user_id=user.id,
        full_name=req.full_name,
        college=req.college,
        degree=req.degree,
        branch=req.branch,
        graduation_year=req.graduation_year,
        cgpa=req.cgpa,
        phone=req.phone,
        location=req.location,
        daily_hours=2.0,
        profile_completed=bool(req.college and req.degree and req.cgpa)
    )
    db.add(student)
    db.commit()
    db.refresh(user)
    db.refresh(student)
    
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role.value,
        user_id=user.id,
        student_id=student.id
    )

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated"
        )
        
    student_id = None
    if user.role == UserRole.student and user.student:
        student_id = user.student.id
        
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role.value,
        user_id=user.id,
        student_id=student_id
    )

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value,
        "student_id": current_user.student.id if current_user.student else None
    }
