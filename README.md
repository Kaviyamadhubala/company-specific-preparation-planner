# Company-Specific Preparation Planner

A modern, full-stack student placement-preparation web platform designed to analyze target company recruitment processes, compute mathematically verified skill gaps, generate adaptive day-by-day preparation roadmaps, and conduct interactive AI mock interviews.

---

## 1. Project Overview & Architecture

### Concept Flow
```
Student Profile
      ↓
Select Target Company + Role
      ↓
Analyze Company Recruitment Process (5 Rounds Timeline)
      ↓
Identify Required Skills & Proficiency Cutoffs
      ↓
Compare Student Skills (0: Not Started → 5: Expert)
      ↓
Skill Gap Analysis (Ready, Needs Improvement, Major Gap, Not Started)
      ↓
Weighted Company Readiness Score (Configurable Weights)
      ↓
Personalized Day-by-Day Preparation Roadmap
      ↓
Daily Action Tasks & Progress Checklist
      ↓
Timed Practice & Company Mock Tests
      ↓
Adaptive Roadmap Updates (Automatic revision or fast-track)
      ↓
Interactive AI Mock Interview (Scorecard & Feedback)
      ↓
Resume Analysis & Targeted Portfolio Project Recommendations
```

### Clean Architecture

```
prep-planner/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entry point & CORS
│   │   ├── database.py              # SQLite / PostgreSQL SQLAlchemy engine & SessionLocal
│   │   ├── models/                  # 25 relational database models
│   │   │   ├── models.py
│   │   │   └── __init__.py
│   │   ├── schemas/                 # Pydantic request/response validation
│   │   │   ├── schemas.py
│   │   │   └── __init__.py
│   │   ├── auth/                    # Direct bcrypt hashing & JWT token handling
│   │   │   ├── jwt.py
│   │   │   ├── dependencies.py
│   │   │   └── __init__.py
│   │   ├── services/                # Core Business Logic & Algorithms
│   │   │   ├── readiness.py         # Weighted Readiness Score Engine
│   │   │   ├── roadmap.py           # Personalized & Adaptive Roadmap Generator
│   │   │   ├── recommendation.py   # Multi-Factor Company Recommendation Engine
│   │   │   ├── ai_service.py        # Gemini AI + graceful rule-based fallback
│   │   │   ├── resume_parser.py     # PDF & text skill extraction & matching
│   │   │   └── __init__.py
│   │   └── routers/                 # REST API endpoints (12 router modules)
│   │       ├── auth.py
│   │       ├── students.py
│   │       ├── companies.py
│   │       ├── readiness.py
│   │       ├── roadmap.py
│   │       ├── tests.py
│   │       ├── mock_interview.py
│   │       ├── resume.py
│   │       ├── projects.py
│   │       ├── progress.py
│   │       ├── recommendations.py
│   │       ├── admin.py
│   │       └── __init__.py
│   ├── requirements.txt
│   ├── seed.py                      # Realistic data seeder (10 companies, 70+ questions)
│   └── .env                         # Environment variables
└── frontend/
    ├── src/
    │   ├── components/              # Common UI widgets & Recharts
    │   │   ├── common/              # Navbar, Sidebar, SkillBadge, ReadinessCard, RoundTimeline
    │   │   └── charts/              # WeeklyProgressChart, RadarChart, SkillGapBarChart
    │   ├── context/                 # AuthContext for session management
    │   ├── layouts/                 # StudentLayout & AdminLayout
    │   ├── pages/                   # Application views
    │   │   ├── LandingPage.jsx
    │   │   ├── LoginPage.jsx
    │   │   ├── RegisterPage.jsx
    │   │   ├── student/             # Student Dashboard, Roadmap, Tasks, Tests, AI Interview, etc.
    │   │   └── admin/               # Admin Stats, Company Manager, Question Bank, Scoring Weights
    │   ├── services/api.js          # Axios client with JWT bearer interceptors
    │   ├── App.jsx                  # React Router v6 route configuration
    │   ├── main.jsx
    │   └── index.css                # Tailwind base & custom scrollbars
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

---

## 2. Technology Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy ORM, SQLite (production upgradeable to PostgreSQL)
- **Security**: JWT (python-jose) with direct `bcrypt` password hashing
- **AI Integration**: Google Gemini API (`gemini-1.5-flash`) with full zero-crash fallback
- **File Parsing**: `PyMuPDF` (fitz) for PDF resume text and skill extraction
- **Frontend**: React 18, Vite, React Router v6, Tailwind CSS, Recharts, Lucide Icons, Axios

---

## 3. Core Engine Algorithms

### A. Skill Gap & Company Readiness Algorithm (`readiness.py`)
No random percentages are generated. Every score is mathematically derived:

1. **Individual Skill Match**:
   $$\text{Skill Percentage} = \min\left(\frac{\text{Student Level}}{\text{Required Level}}, 1.0\right) \times 100$$
   - Gap $= \text{Required Level} - \text{Student Level}$
   - Gap $\le 0 \implies \text{"Ready"}$
   - Gap $= 1 \implies \text{"Needs Improvement"}$
   - Gap $\ge 2 \implies \text{"Major Gap"}$
   - Student Level $= 0 \implies \text{"Not Started"}$

2. **Weighted Readiness Score**:
   Configured and stored in the database (`readiness_weights` table), editable by Admin:
   - Technical Skills: **35%**
   - DSA: **20%**
   - Aptitude & Reasoning: **15%**
   - CS Core Fundamentals (DBMS/OS/Networks): **10%**
   - Communication & Soft Skills: **10%**
   - Interview Preparation: **10%**

   $$\text{Readiness Score} = \sum \left(\frac{\text{Category Score} \times \text{Weight}}{\text{Total Weight}}\right)$$

### B. Personalized Roadmap Generation Engine (`roadmap.py`)
- Takes student's available duration (e.g. 30 days) and daily study hours (e.g. 2.5 hrs).
- Computes skill gap severity descending: largest gaps receive proportionally more preparation days.
- Sequences topics according to prerequisite ordering: Technical Basics &rarr; OOP &rarr; DSA &rarr; SQL &rarr; DBMS &rarr; System Design &rarr; Interview Practice.
- Reserves the final 20% of the schedule for mock tests and interview preparation.
- Generates Day-by-Day tasks with estimated minutes and target difficulty.

### C. Adaptive Roadmap Adjustment Engine (`roadmap.py`)
Triggered automatically upon practice test submission:
- **Score < 60%**: System detects low mastery. Automatically inserts 3 prerequisite revision tasks into upcoming days and alerts the student.
- **Score > 85%**: System detects mastery. Automatically skips redundant introductory tasks, advances to harder problems, and bumps the student's tracked skill proficiency level $+1$.

### D. Multi-Factor Company Recommendation Engine (`recommendation.py`)
Evaluates candidate compatibility across all recruiters:
$$\text{Match Score} = (0.40 \times \text{Skill Match}) + (0.20 \times \text{Role Match}) + (0.15 \times \text{Eligibility}) + (0.10 \times \text{Academic CGPA}) + (0.15 \times \text{Past Test Performance})$$

---

## 4. Setup & Running Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### Backend Setup
1. Open a terminal in `backend/`:
   ```bash
   cd prep-planner/backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize and seed the database:
   ```bash
   python seed.py
   ```
   *This automatically creates tables, seeds 10 companies with 5 recruitment rounds each, 15 skills, 70+ verified practice questions, projects, resources, and an active demo roadmap.*

4. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *Backend Swagger Docs will be available at: http://127.0.0.1:8000/docs*

### Frontend Setup
1. Open a terminal in `frontend/`:
   ```bash
   cd prep-planner/frontend
   ```
2. Install Node packages:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
4. Access the web app at: **http://localhost:5173**

---

## 5. Sample Login Credentials

| Role | Email | Password | Pre-loaded Data |
|---|---|---|---|
| **Student** | `student@example.com` | `Student@123` | Alex Johnson, B.Tech CSE (8.4 CGPA), Active TCS Roadmap, Tracked Skills |
| **Admin** | `admin@prepplanner.com` | `Admin@123` | Full access to Company CRUD, Question Bank, and Scoring Weights |

*(One-click quick login buttons are also provided directly on the Login page).*

---

## 6. API Documentation Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register student profile & obtain JWT |
| `POST` | `/api/auth/login` | Authenticate student or admin |
| `GET` | `/api/companies` | List all companies with difficulty & role counts |
| `GET` | `/api/companies/{id}` | Detailed company info, roles, and 5-round timeline |
| `GET` | `/api/readiness/{c_id}/{r_id}` | Compute real-time weighted readiness score & skill gaps |
| `GET` | `/api/readiness/compare/all` | Cross-company readiness comparison matrix |
| `POST` | `/api/roadmap/generate` | Generate personalized day-by-day roadmap |
| `GET` | `/api/roadmap/current` | Retrieve active roadmap with week & day tasks |
| `PUT` | `/api/roadmap/tasks/{id}` | Update task status / score |
| `POST` | `/api/tests/start` | Launch timed practice or company mock assessment |
| `POST` | `/api/tests/{id}/submit` | Submit answers, calculate score, trigger adaptive engine |
| `POST` | `/api/interviews/start` | Initialize AI mock interview conversation |
| `POST` | `/api/interviews/{id}/message` | Send answer & receive dynamic follow-up |
| `POST` | `/api/interviews/{id}/end` | Generate scorecard & improvement suggestions |
| `POST` | `/api/resume/analyze` | Parse PDF resume & match skills against company |
| `GET` | `/api/projects/recommendations` | Get targeted projects to plug active skill gaps |
| `GET` | `/api/admin/stats` | Admin metrics & student monitoring |
| `PUT` | `/api/admin/weights` | Update readiness formula weights |
