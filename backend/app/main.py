"""
Company-Specific Preparation Planner — FastAPI Backend
Main application entry point.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from app.database import engine, Base

# Import all models so they register with SQLAlchemy
import app.models.models  # noqa: F401

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Company-Specific Preparation Planner API",
    description="Personalized placement preparation platform for students",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
cors_origins_env = os.getenv("CORS_ORIGINS", "")
origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()] if cors_origins_env else ["http://localhost:5173", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from app.routers import auth, students, companies, readiness, roadmap, tests, mock_interview, resume, projects, progress, recommendations, admin

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(companies.router)
app.include_router(readiness.router)
app.include_router(roadmap.router)
app.include_router(tests.router)
app.include_router(mock_interview.router)
app.include_router(resume.router)
app.include_router(projects.router)
app.include_router(progress.router)
app.include_router(recommendations.router)
app.include_router(admin.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Company-Specific Preparation Planner API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok"}
