"""SQLAlchemy ORM models for the Prep Planner application."""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
import enum

from app.database import Base


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────

class UserRole(str, enum.Enum):
    student = "student"
    admin = "admin"


class SkillLevel(str, enum.Enum):
    not_started = "not_started"  # 0
    beginner = "beginner"        # 1
    basic = "basic"              # 2
    intermediate = "intermediate"  # 3
    advanced = "advanced"        # 4
    expert = "expert"            # 5


class GapStatus(str, enum.Enum):
    ready = "ready"
    needs_improvement = "needs_improvement"
    major_gap = "major_gap"
    not_started = "not_started"


class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    skipped = "skipped"


class RoadmapStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    paused = "paused"


class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QuestionCategory(str, enum.Enum):
    aptitude = "aptitude"
    logical_reasoning = "logical_reasoning"
    verbal_ability = "verbal_ability"
    programming = "programming"
    dsa = "dsa"
    oop = "oop"
    dbms = "dbms"
    sql = "sql"
    operating_systems = "operating_systems"
    computer_networks = "computer_networks"
    technical = "technical"
    hr = "hr"


class TestType(str, enum.Enum):
    aptitude = "aptitude"
    technical = "technical"
    mock = "mock"
    topic = "topic"


class ResourceType(str, enum.Enum):
    documentation = "documentation"
    tutorial = "tutorial"
    video = "video"
    practice = "practice"
    article = "article"


class NotificationType(str, enum.Enum):
    task_reminder = "task_reminder"
    missed_task = "missed_task"
    low_score = "low_score"
    milestone = "milestone"
    company_update = "company_update"
    interview_reminder = "interview_reminder"
    general = "general"


# ─────────────────────────────────────────────
# Core Auth Models
# ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.student, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="user", uselist=False)


# ─────────────────────────────────────────────
# Student Profile
# ─────────────────────────────────────────────

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    college = Column(String(255))
    degree = Column(String(100))
    branch = Column(String(100))
    graduation_year = Column(Integer)
    cgpa = Column(Float)
    phone = Column(String(20))
    location = Column(String(100))
    daily_hours = Column(Float, default=2.0)
    preferred_role = Column(String(100))
    preferred_location = Column(String(100))
    bio = Column(Text)
    profile_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="student")
    skills = relationship("StudentSkill", back_populates="student")
    roadmaps = relationship("Roadmap", back_populates="student")
    tests = relationship("Test", back_populates="student")
    mock_interviews = relationship("MockInterview", back_populates="student")
    notifications = relationship("Notification", back_populates="student")
    projects = relationship("StudentProject", back_populates="student")


# ─────────────────────────────────────────────
# Skills
# ─────────────────────────────────────────────

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)  # technical, dsa, aptitude, cs_fundamentals, communication
    description = Column(Text)
    icon = Column(String(50))  # emoji or icon name

    student_skills = relationship("StudentSkill", back_populates="skill")
    company_skills = relationship("CompanySkill", back_populates="skill")
    resources = relationship("Resource", back_populates="skill")


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    level = Column(Integer, default=0)  # 0-5 maps to SkillLevel enum
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="skills")
    skill = relationship("Skill", back_populates="student_skills")


# ─────────────────────────────────────────────
# Companies + Roles
# ─────────────────────────────────────────────

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    logo_color = Column(String(7), default="#6366f1")  # hex color for logo bg
    logo_initials = Column(String(5))
    description = Column(Text)
    industry = Column(String(100))
    difficulty = Column(SAEnum(Difficulty), default=Difficulty.medium)
    min_cgpa = Column(Float, default=6.0)
    eligibility_notes = Column(Text)
    website = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles = relationship("CompanyRole", back_populates="company")
    rounds = relationship("RecruitmentRound", back_populates="company")
    questions = relationship("Question", back_populates="company")
    projects = relationship("Project", back_populates="company")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    company_roles = relationship("CompanyRole", back_populates="role")


class CompanyRole(Base):
    __tablename__ = "company_roles"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)

    company = relationship("Company", back_populates="roles")
    role = relationship("Role", back_populates="company_roles")
    skills = relationship("CompanySkill", back_populates="company_role")
    roadmaps = relationship("Roadmap", back_populates="company_role")


class CompanySkill(Base):
    __tablename__ = "company_skills"

    id = Column(Integer, primary_key=True, index=True)
    company_role_id = Column(Integer, ForeignKey("company_roles.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    required_level = Column(Integer, nullable=False)  # 1-5
    weight = Column(Float, default=1.0)  # importance weight

    company_role = relationship("CompanyRole", back_populates="skills")
    skill = relationship("Skill", back_populates="company_skills")


# ─────────────────────────────────────────────
# Recruitment Rounds
# ─────────────────────────────────────────────

class RecruitmentRound(Base):
    __tablename__ = "recruitment_rounds"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    difficulty = Column(SAEnum(Difficulty), default=Difficulty.medium)
    estimated_days = Column(Integer, default=3)
    tips = Column(Text)

    company = relationship("Company", back_populates="rounds")
    skills = relationship("RoundSkill", back_populates="round")


class RoundSkill(Base):
    __tablename__ = "round_skills"

    id = Column(Integer, primary_key=True, index=True)
    round_id = Column(Integer, ForeignKey("recruitment_rounds.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    importance = Column(Integer, default=3)  # 1-5

    round = relationship("RecruitmentRound", back_populates="skills")
    skill = relationship("Skill")


# ─────────────────────────────────────────────
# Roadmap
# ─────────────────────────────────────────────

class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company_role_id = Column(Integer, ForeignKey("company_roles.id"), nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    total_days = Column(Integer, default=30)
    daily_hours = Column(Float, default=2.0)
    status = Column(SAEnum(RoadmapStatus), default=RoadmapStatus.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="roadmaps")
    company = relationship("Company")
    company_role = relationship("CompanyRole", back_populates="roadmaps")
    weeks = relationship("RoadmapWeek", back_populates="roadmap", cascade="all, delete-orphan")
    tasks = relationship("RoadmapTask", back_populates="roadmap", cascade="all, delete-orphan")


class RoadmapWeek(Base):
    __tablename__ = "roadmap_weeks"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    theme = Column(String(255))
    focus_areas = Column(Text)  # JSON list of topics

    roadmap = relationship("Roadmap", back_populates="weeks")
    tasks = relationship("RoadmapTask", back_populates="week")


class RoadmapTask(Base):
    __tablename__ = "roadmap_tasks"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    week_id = Column(Integer, ForeignKey("roadmap_weeks.id"), nullable=True)
    day_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    topic = Column(String(100))
    category = Column(String(50))
    difficulty = Column(SAEnum(Difficulty), default=Difficulty.medium)
    estimated_minutes = Column(Integer, default=60)
    status = Column(SAEnum(TaskStatus), default=TaskStatus.pending)
    score = Column(Float, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    roadmap = relationship("Roadmap", back_populates="tasks")
    week = relationship("RoadmapWeek", back_populates="tasks")


# ─────────────────────────────────────────────
# Questions and Tests
# ─────────────────────────────────────────────

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    category = Column(SAEnum(QuestionCategory), nullable=False)
    topic = Column(String(100))
    difficulty = Column(SAEnum(Difficulty), default=Difficulty.medium)
    explanation = Column(Text)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="questions")
    role = relationship("Role")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")


class QuestionOption(Base):
    __tablename__ = "question_options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    option_order = Column(Integer, default=0)

    question = relationship("Question", back_populates="options")


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    test_type = Column(SAEnum(TestType), default=TestType.topic)
    topic = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)
    duration_minutes = Column(Integer, default=30)
    started_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    total_score = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    correct_count = Column(Integer, default=0)
    wrong_count = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)

    student = relationship("Student", back_populates="tests")
    company = relationship("Company")
    role = relationship("Role")
    questions = relationship("TestQuestion", back_populates="test", cascade="all, delete-orphan")
    answers = relationship("TestAnswer", back_populates="test", cascade="all, delete-orphan")


class TestQuestion(Base):
    __tablename__ = "test_questions"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    question_order = Column(Integer, default=0)

    test = relationship("Test", back_populates="questions")
    question = relationship("Question")


class TestAnswer(Base):
    __tablename__ = "test_answers"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option_id = Column(Integer, ForeignKey("question_options.id"), nullable=True)
    is_correct = Column(Boolean, default=False)
    time_taken_seconds = Column(Integer, default=0)

    test = relationship("Test", back_populates="answers")
    question = relationship("Question")
    selected_option = relationship("QuestionOption")


# ─────────────────────────────────────────────
# Mock Interviews
# ─────────────────────────────────────────────

class MockInterview(Base):
    __tablename__ = "mock_interviews"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    interview_type = Column(String(50), default="technical")  # technical, hr, full
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    tech_score = Column(Float, nullable=True)
    comm_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    suggestions = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    ai_mode = Column(Boolean, default=True)

    student = relationship("Student", back_populates="mock_interviews")
    company = relationship("Company")
    role = relationship("Role")
    messages = relationship("InterviewMessage", back_populates="interview", cascade="all, delete-orphan")


class InterviewMessage(Base):
    __tablename__ = "interview_messages"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("mock_interviews.id"), nullable=False)
    role = Column(String(10), nullable=False)  # "ai" or "student"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    interview = relationship("MockInterview", back_populates="messages")


# ─────────────────────────────────────────────
# Projects + Resources
# ─────────────────────────────────────────────

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    skills_covered = Column(Text)  # JSON list
    difficulty = Column(SAEnum(Difficulty), default=Difficulty.medium)
    duration_days = Column(Integer, default=7)
    why_it_helps = Column(Text)
    technologies = Column(Text)  # JSON list
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    github_template = Column(String(255), nullable=True)

    company = relationship("Company", back_populates="projects")
    role = relationship("Role")
    student_projects = relationship("StudentProject", back_populates="project")


class StudentProject(Base):
    __tablename__ = "student_projects"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    status = Column(String(20), default="recommended")  # recommended, in_progress, completed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="projects")
    project = relationship("Project", back_populates="student_projects")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    resource_type = Column(SAEnum(ResourceType), default=ResourceType.tutorial)
    url = Column(String(500))
    description = Column(Text)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    is_free = Column(Boolean, default=True)

    skill = relationship("Skill", back_populates="resources")


# ─────────────────────────────────────────────
# Notifications + Config
# ─────────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    notification_type = Column(SAEnum(NotificationType), default=NotificationType.general)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="notifications")


class ReadinessWeight(Base):
    __tablename__ = "readiness_weights"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), unique=True, nullable=False)
    weight_pct = Column(Float, nullable=False)  # sums to 100
    description = Column(String(255))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
