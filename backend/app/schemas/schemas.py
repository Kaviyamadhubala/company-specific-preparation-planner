"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
import re


# ─────────────────────────────────────────────
# Auth Schemas
# ─────────────────────────────────────────────

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None
    phone: Optional[str] = None
    location: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("cgpa")
    @classmethod
    def cgpa_range(cls, v):
        if v is not None and not (0 <= v <= 10):
            raise ValueError("CGPA must be between 0 and 10")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    student_id: Optional[int] = None


# ─────────────────────────────────────────────
# Student Schemas
# ─────────────────────────────────────────────

class StudentProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    daily_hours: Optional[float] = None
    preferred_role: Optional[str] = None
    preferred_location: Optional[str] = None
    bio: Optional[str] = None


class StudentProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    college: Optional[str]
    degree: Optional[str]
    branch: Optional[str]
    graduation_year: Optional[int]
    cgpa: Optional[float]
    phone: Optional[str]
    location: Optional[str]
    daily_hours: float
    preferred_role: Optional[str]
    preferred_location: Optional[str]
    bio: Optional[str]
    profile_completed: bool
    email: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Skill Schemas
# ─────────────────────────────────────────────

class SkillResponse(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str]
    icon: Optional[str]

    class Config:
        from_attributes = True


class StudentSkillUpdate(BaseModel):
    skill_id: int
    level: int  # 0-5

    @field_validator("level")
    @classmethod
    def level_range(cls, v):
        if not (0 <= v <= 5):
            raise ValueError("Level must be 0-5")
        return v


class StudentSkillResponse(BaseModel):
    id: int
    skill_id: int
    skill_name: str
    skill_category: str
    level: int
    level_label: str

    class Config:
        from_attributes = True


class BulkSkillUpdate(BaseModel):
    skills: List[StudentSkillUpdate]


# ─────────────────────────────────────────────
# Company Schemas
# ─────────────────────────────────────────────

class CompanyCreate(BaseModel):
    name: str
    logo_color: Optional[str] = "#6366f1"
    logo_initials: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    difficulty: Optional[str] = "medium"
    min_cgpa: Optional[float] = 6.0
    eligibility_notes: Optional[str] = None
    website: Optional[str] = None


class CompanyUpdate(CompanyCreate):
    name: Optional[str] = None


class RoundSkillInfo(BaseModel):
    skill_id: int
    skill_name: str
    importance: int

    class Config:
        from_attributes = True


class RecruitmentRoundResponse(BaseModel):
    id: int
    round_number: int
    name: str
    description: Optional[str]
    difficulty: str
    estimated_days: int
    tips: Optional[str]
    skills: List[RoundSkillInfo] = []

    class Config:
        from_attributes = True


class CompanySkillResponse(BaseModel):
    skill_id: int
    skill_name: str
    skill_category: str
    required_level: int
    required_level_label: str
    weight: float

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class CompanyRoleResponse(BaseModel):
    id: int
    role_id: int
    role_name: str
    notes: Optional[str]
    skills: List[CompanySkillResponse] = []

    class Config:
        from_attributes = True


class CompanyResponse(BaseModel):
    id: int
    name: str
    logo_color: str
    logo_initials: Optional[str]
    description: Optional[str]
    industry: Optional[str]
    difficulty: str
    min_cgpa: float
    eligibility_notes: Optional[str]
    website: Optional[str]
    is_active: bool
    roles: List[CompanyRoleResponse] = []
    rounds: List[RecruitmentRoundResponse] = []

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    id: int
    name: str
    logo_color: str
    logo_initials: Optional[str]
    description: Optional[str]
    industry: Optional[str]
    difficulty: str
    min_cgpa: float
    role_count: int = 0

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Skill Gap + Readiness Schemas
# ─────────────────────────────────────────────

class SkillGapItem(BaseModel):
    skill_id: int
    skill_name: str
    skill_category: str
    student_level: int
    required_level: int
    gap: int
    status: str  # ready, needs_improvement, major_gap, not_started
    percentage: float
    weight: float


class ReadinessBreakdown(BaseModel):
    category: str
    score: float
    weight: float
    weighted_score: float


class ReadinessResponse(BaseModel):
    student_id: int
    company_id: int
    company_role_id: int
    overall_score: float
    breakdown: List[ReadinessBreakdown]
    skill_gaps: List[SkillGapItem]
    top_weak_areas: List[str]
    is_eligible: bool
    eligibility_note: str


# ─────────────────────────────────────────────
# Roadmap Schemas
# ─────────────────────────────────────────────

class RoadmapGenerateRequest(BaseModel):
    company_id: int
    company_role_id: int
    total_days: int = 30
    daily_hours: float = 2.0
    exam_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: int
    day_number: int
    title: str
    description: Optional[str]
    topic: Optional[str]
    category: Optional[str]
    difficulty: str
    estimated_minutes: int
    status: str
    score: Optional[float]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class WeekResponse(BaseModel):
    id: int
    week_number: int
    theme: str
    focus_areas: Optional[str]
    tasks: List[TaskResponse] = []

    class Config:
        from_attributes = True


class RoadmapResponse(BaseModel):
    id: int
    student_id: int
    company_id: int
    company_role_id: int
    company_name: str
    role_name: str
    start_date: datetime
    end_date: Optional[datetime]
    total_days: int
    daily_hours: float
    status: str
    completion_pct: float
    weeks: List[WeekResponse] = []

    class Config:
        from_attributes = True


class TaskUpdateRequest(BaseModel):
    status: Optional[str] = None
    score: Optional[float] = None
    notes: Optional[str] = None


# ─────────────────────────────────────────────
# Test / Question Schemas
# ─────────────────────────────────────────────

class QuestionOptionResponse(BaseModel):
    id: int
    option_text: str
    option_order: int

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    category: str
    topic: Optional[str]
    difficulty: str
    options: List[QuestionOptionResponse] = []

    class Config:
        from_attributes = True


class QuestionWithAnswerResponse(QuestionResponse):
    explanation: Optional[str]
    correct_option_id: int


class TestStartRequest(BaseModel):
    company_id: Optional[int] = None
    role_id: Optional[int] = None
    test_type: str = "topic"
    topic: Optional[str] = None
    category: Optional[str] = None
    num_questions: int = 20
    duration_minutes: int = 30


class TestAnswerSubmit(BaseModel):
    question_id: int
    selected_option_id: Optional[int] = None
    time_taken_seconds: int = 0


class TestSubmitRequest(BaseModel):
    answers: List[TestAnswerSubmit]


class TopicPerformance(BaseModel):
    topic: str
    correct: int
    total: int
    score: float


class TestResultResponse(BaseModel):
    test_id: int
    total_score: float
    accuracy: float
    correct_count: int
    wrong_count: int
    total_questions: int
    time_taken_minutes: float
    topic_performance: List[TopicPerformance]
    weak_areas: List[str]
    roadmap_adapted: bool


# ─────────────────────────────────────────────
# Mock Interview Schemas
# ─────────────────────────────────────────────

class InterviewStartRequest(BaseModel):
    company_id: Optional[int] = None
    role_id: Optional[int] = None
    interview_type: str = "technical"  # technical, hr, full


class InterviewMessageRequest(BaseModel):
    content: str


class InterviewMessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class InterviewResponse(BaseModel):
    interview_id: int
    ai_message: str
    is_completed: bool = False


class InterviewEndResponse(BaseModel):
    interview_id: int
    tech_score: Optional[float]
    comm_score: Optional[float]
    relevance_score: Optional[float]
    overall_score: Optional[float]
    feedback: Optional[str]
    suggestions: Optional[str]
    messages: List[InterviewMessageResponse]


# ─────────────────────────────────────────────
# Resume Schemas
# ─────────────────────────────────────────────

class ResumeSkillMatch(BaseModel):
    skill_name: str
    found_in_resume: bool
    required_by_company: bool
    status: str  # matched, missing, extra


class ResumeAnalysisResponse(BaseModel):
    extracted_skills: List[str]
    extracted_languages: List[str]
    extracted_projects: List[str]
    extracted_certifications: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    match_score: float
    recommendations: List[str]


# ─────────────────────────────────────────────
# Progress + Analytics Schemas
# ─────────────────────────────────────────────

class ProgressResponse(BaseModel):
    roadmap_completion_pct: float
    practice_avg_score: float
    mock_interview_avg_score: float
    total_study_hours: float
    tasks_completed: int
    tasks_total: int
    tests_taken: int
    skills_improved: int
    current_roadmap_id: Optional[int]
    current_company: Optional[str]
    current_role: Optional[str]
    readiness_score: float


class WeeklyProgressItem(BaseModel):
    week: str
    tasks_completed: int
    avg_score: float
    study_hours: float


class SkillProgressItem(BaseModel):
    skill_name: str
    initial_level: int
    current_level: int
    improvement: int


# ─────────────────────────────────────────────
# Notification Schemas
# ─────────────────────────────────────────────

class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Recommendation Schemas
# ─────────────────────────────────────────────

class CompanyReadinessItem(BaseModel):
    company_id: int
    company_name: str
    logo_color: str
    logo_initials: Optional[str]
    industry: Optional[str]
    difficulty: str
    readiness_score: float
    skill_match: float
    is_eligible: bool
    reason: str


class MultiCompanyComparisonResponse(BaseModel):
    companies: List[CompanyReadinessItem]
    best_match: Optional[str]
    recommendation_summary: str


# ─────────────────────────────────────────────
# Project Schemas
# ─────────────────────────────────────────────

class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    skills_covered: Optional[str]
    difficulty: str
    duration_days: int
    why_it_helps: Optional[str]
    technologies: Optional[str]

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Admin Schemas
# ─────────────────────────────────────────────

class AdminStatsResponse(BaseModel):
    total_students: int
    total_companies: int
    total_questions: int
    active_roadmaps: int
    completed_tests: int
    avg_readiness: float


class QuestionCreate(BaseModel):
    question_text: str
    category: str
    topic: Optional[str] = None
    difficulty: str = "medium"
    explanation: Optional[str] = None
    company_id: Optional[int] = None
    role_id: Optional[int] = None
    options: List[dict]  # [{option_text: str, is_correct: bool}]


class ReadinessWeightUpdate(BaseModel):
    category: str
    weight_pct: float
    description: Optional[str] = None


class CompanyRoleCreate(BaseModel):
    company_id: int
    role_id: int
    notes: Optional[str] = None
    skills: List[dict]  # [{skill_id, required_level, weight}]


class RecruitmentRoundCreate(BaseModel):
    company_id: int
    round_number: int
    name: str
    description: Optional[str] = None
    difficulty: str = "medium"
    estimated_days: int = 3
    tips: Optional[str] = None
    skill_ids: List[int] = []
