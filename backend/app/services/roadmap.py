"""
Personalized Roadmap Generation Engine.

Generates a day-by-day preparation roadmap based on:
  - Student's skill gaps (sorted by severity)
  - Company role required skills
  - Available study time (days × daily_hours)
  - Prerequisite topic ordering

Adaptive updates are also handled here.
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.models import (
    Student, StudentSkill, CompanySkill, Skill,
    Roadmap, RoadmapWeek, RoadmapTask,
    Company, CompanyRole, RoadmapStatus,
    Difficulty, Notification, NotificationType, Test, StudentSkill
)
from app.services.readiness import calculate_readiness, get_gap_status

# ─────────────────────────────────────────────
# Topic prerequisite ordering (lower index = earlier)
# ─────────────────────────────────────────────
TOPIC_ORDER = {
    "technical": 1,
    "oop": 2,
    "dsa": 3,
    "sql": 4,
    "dbms": 5,
    "cs_fundamentals": 6,
    "aptitude": 7,
    "communication": 8,
    "interview": 9,
}

TOPIC_SYLLABI: Dict[str, List[str]] = {
    "Java": ["Classes & Objects", "Inheritance", "Polymorphism", "Abstraction", "Interfaces", "Collections", "Exception Handling", "Generics", "Practice Problems"],
    "Python": ["Syntax & Basics", "OOP in Python", "List/Dict/Set", "File I/O", "Libraries", "Practice Problems"],
    "DSA": ["Arrays", "Strings", "Linked Lists", "Stacks & Queues", "Trees", "Graphs", "Searching", "Sorting", "Hashing", "Two Pointers", "Practice Problems"],
    "SQL": ["SELECT & WHERE", "JOINs", "GROUP BY & HAVING", "Subqueries", "Indexes", "Transactions", "Practice Problems"],
    "DBMS": ["ER Diagrams", "Normalization (1NF-3NF)", "Transactions & ACID", "Concurrency Control", "Indexing", "Practice Problems"],
    "Operating Systems": ["Processes & Threads", "Scheduling", "Memory Management", "Deadlocks", "File Systems", "Practice Problems"],
    "Computer Networks": ["OSI Model", "TCP/IP", "HTTP/HTTPS", "DNS & DHCP", "Routing", "Practice Problems"],
    "OOP": ["Encapsulation", "Inheritance", "Polymorphism", "Abstraction", "Design Patterns", "SOLID Principles", "Practice Problems"],
    "Aptitude": ["Number Systems", "Percentages & Ratios", "Time & Work", "Probability", "Logical Reasoning", "Verbal Ability", "Mock Aptitude Test"],
    "Communication": ["Verbal Communication", "Written Communication", "Presentation Skills", "Group Discussion Tips", "Email Etiquette"],
    "Interview Prep": ["Technical Question Patterns", "Behavioral Questions (STAR)", "Project Walkthrough", "Resume Discussion", "HR Questions", "Mock Interview"],
    "React": ["JSX & Components", "Props & State", "Hooks (useState, useEffect)", "Context API", "React Router", "Practice Project"],
    "Spring Boot": ["Spring Core & IoC", "Spring MVC", "REST APIs", "Spring Data JPA", "Spring Security", "Practice Project"],
    "Data Analysis": ["Numpy & Pandas", "Data Visualization", "Statistics Basics", "SQL for Analytics", "Practice Project"],
}

DIFFICULTY_ORDER = [Difficulty.easy, Difficulty.medium, Difficulty.hard]


def days_for_topic(gap_severity: int, total_hours: float, num_topics: int) -> int:
    """Calculate days to allocate for a topic based on gap severity."""
    base_proportion = gap_severity / max(num_topics, 1)
    return max(1, round(base_proportion))


def get_topic_tasks(skill_name: str, day_offset: int, difficulty: Difficulty) -> List[dict]:
    """Generate daily tasks for a given skill/topic."""
    syllabus = TOPIC_SYLLABI.get(skill_name, [f"Study {skill_name}", f"Practice {skill_name}", "Review & Revise"])
    tasks = []
    for i, subtopic in enumerate(syllabus):
        tasks.append({
            "title": f"{skill_name}: {subtopic}",
            "description": f"Study and practice {subtopic} for {skill_name}.",
            "topic": skill_name,
            "category": "study",
            "difficulty": difficulty.value,
            "estimated_minutes": 60,
        })
    return tasks


def generate_roadmap(
    db: Session,
    student_id: int,
    company_id: int,
    company_role_id: int,
    total_days: int = 30,
    daily_hours: float = 2.0,
    exam_date: Optional[datetime] = None,
) -> Roadmap:
    """
    Generate a personalized preparation roadmap.

    Algorithm:
    1. Compute skill gaps (sorted by severity DESC)
    2. Allocate days proportional to gap
    3. Assign subtopics to specific days
    4. Insert revision + mock test slots
    5. Add interview prep in final week
    """

    # Remove existing active roadmap for this student + company role
    existing = (
        db.query(Roadmap)
        .filter(
            Roadmap.student_id == student_id,
            Roadmap.company_role_id == company_role_id,
            Roadmap.status == RoadmapStatus.active,
        )
        .first()
    )
    if existing:
        existing.status = RoadmapStatus.paused
        db.commit()

    # Compute readiness to get skill gaps
    readiness = calculate_readiness(db, student_id, company_id, company_role_id)
    skill_gaps = readiness["skill_gaps"]

    # Filter to skills that need work, sort by gap severity DESC
    gaps_to_address = [g for g in skill_gaps if g["gap"] > 0]
    gaps_to_address.sort(key=lambda x: (-x["gap"], x["skill_name"]))

    # Also include low-readiness skills (< 70%)
    low_ready = [g for g in skill_gaps if g["gap"] <= 0 and g["percentage"] < 70]
    gaps_to_address.extend(low_ready)

    # Reserve last 20% of days for interview + revision
    interview_days = max(3, int(total_days * 0.20))
    prep_days = total_days - interview_days

    # Allocate days per skill proportionally
    if not gaps_to_address:
        # All ready — mock interviews + review
        gaps_to_address = skill_gaps[:3]

    total_gap_score = sum(max(g["gap"], 1) for g in gaps_to_address)
    day_allocation: Dict[str, int] = {}
    for g in gaps_to_address:
        proportion = max(g["gap"], 1) / total_gap_score
        allocated = max(1, round(proportion * prep_days))
        day_allocation[g["skill_name"]] = allocated

    # Build flat task list
    all_tasks: List[dict] = []
    current_day = 1

    for gap in gaps_to_address:
        skill_name = gap["skill_name"]
        days = day_allocation.get(skill_name, 1)
        gap_val = gap["gap"]

        if gap_val >= 2:
            diff = Difficulty.easy
        elif gap_val == 1:
            diff = Difficulty.medium
        else:
            diff = Difficulty.medium

        syllabus = TOPIC_SYLLABI.get(skill_name, [f"Study {skill_name}", "Practice Problems", "Revision"])

        # Distribute syllabus across allocated days
        tasks_per_day = max(1, round(len(syllabus) / days))
        syllabus_idx = 0

        for d in range(days):
            if current_day > prep_days:
                break
            day_tasks = []
            for _ in range(tasks_per_day):
                if syllabus_idx < len(syllabus):
                    subtopic = syllabus[syllabus_idx]
                    syllabus_idx += 1
                    day_tasks.append({
                        "day_number": current_day,
                        "title": f"{skill_name}: {subtopic}",
                        "description": f"Study and practice: {subtopic}",
                        "topic": skill_name,
                        "category": gap["skill_category"],
                        "difficulty": diff.value,
                        "estimated_minutes": int(daily_hours * 60 / max(tasks_per_day, 1)),
                    })

            if not day_tasks:
                day_tasks.append({
                    "day_number": current_day,
                    "title": f"{skill_name}: Practice & Revision",
                    "description": f"Revise and practice {skill_name} concepts.",
                    "topic": skill_name,
                    "category": gap["skill_category"],
                    "difficulty": "medium",
                    "estimated_minutes": int(daily_hours * 60),
                })

            all_tasks.extend(day_tasks)
            current_day += 1

    # Every 7th day (or Sunday) → mock test
    for day in range(7, prep_days + 1, 7):
        # Check if there's already a task for this day
        existing_days = {t["day_number"] for t in all_tasks}
        if day not in existing_days:
            all_tasks.append({
                "day_number": day,
                "title": "Weekly Mock Test",
                "description": "Take a timed mock test covering topics studied this week.",
                "topic": "Mock Test",
                "category": "assessment",
                "difficulty": "medium",
                "estimated_minutes": 60,
            })

    # Interview prep — last N days
    interview_topics = [
        "Resume & Project Walkthrough",
        "Behavioral & STAR Questions",
        "Technical Interview Questions",
        "HR Questions Practice",
        "Full Mock Interview",
        "Final Revision & Confidence Building",
    ]
    for i, topic in enumerate(interview_topics):
        day_n = prep_days + i + 1
        if day_n <= total_days:
            all_tasks.append({
                "day_number": day_n,
                "title": f"Interview Prep: {topic}",
                "description": f"Focus on {topic} for your upcoming interviews.",
                "topic": "Interview Prep",
                "category": "interview",
                "difficulty": "medium",
                "estimated_minutes": int(daily_hours * 60),
            })

    # Sort all tasks by day
    all_tasks.sort(key=lambda x: x["day_number"])

    # Group into weeks
    weeks_data: Dict[int, List[dict]] = {}
    for task in all_tasks:
        week_num = (task["day_number"] - 1) // 7 + 1
        weeks_data.setdefault(week_num, []).append(task)

    week_themes = [
        g["skill_name"] for g in gaps_to_address[:4]
    ] + ["Interview Preparation", "Final Revision"]

    # Create DB objects
    start_date = datetime.utcnow()
    end_date = exam_date or (start_date + timedelta(days=total_days))

    roadmap = Roadmap(
        student_id=student_id,
        company_id=company_id,
        company_role_id=company_role_id,
        start_date=start_date,
        end_date=end_date,
        total_days=total_days,
        daily_hours=daily_hours,
        status=RoadmapStatus.active,
    )
    db.add(roadmap)
    db.flush()  # get roadmap.id

    for week_num, week_tasks in sorted(weeks_data.items()):
        theme_idx = week_num - 1
        theme = week_themes[theme_idx] if theme_idx < len(week_themes) else "Revision & Practice"
        focus = list({t["topic"] for t in week_tasks})

        week = RoadmapWeek(
            roadmap_id=roadmap.id,
            week_number=week_num,
            theme=theme,
            focus_areas=json.dumps(focus),
        )
        db.add(week)
        db.flush()

        for task_data in week_tasks:
            task = RoadmapTask(
                roadmap_id=roadmap.id,
                week_id=week.id,
                day_number=task_data["day_number"],
                title=task_data["title"],
                description=task_data.get("description"),
                topic=task_data.get("topic"),
                category=task_data.get("category"),
                difficulty=task_data.get("difficulty", "medium"),
                estimated_minutes=task_data.get("estimated_minutes", 60),
            )
            db.add(task)

    db.commit()
    db.refresh(roadmap)
    return roadmap


def adapt_roadmap(
    db: Session,
    student_id: int,
    roadmap_id: int,
    topic: str,
    score: float,
    skill_id: Optional[int] = None,
) -> dict:
    """
    Adapt the roadmap based on test performance.

    If score < 60%: Add revision tasks for the topic.
    If score > 85%: Skip remaining basic tasks, advance to harder content.
    """
    roadmap = db.query(Roadmap).filter(
        Roadmap.id == roadmap_id,
        Roadmap.student_id == student_id,
    ).first()

    if not roadmap:
        return {"adapted": False, "message": "Roadmap not found"}

    # Find the last completed day
    completed_tasks = [t for t in roadmap.tasks if t.status == "completed"]
    last_day = max((t.day_number for t in completed_tasks), default=0)
    next_day = last_day + 1

    adapted = False
    message = ""

    if score < 60:
        # Add prerequisite revision tasks
        revision_tasks = [
            f"{topic}: Fundamentals Revision",
            f"{topic}: Practice Problems (Easy)",
            f"{topic}: Concept Review Quiz",
        ]
        for i, title in enumerate(revision_tasks):
            new_task = RoadmapTask(
                roadmap_id=roadmap.id,
                day_number=next_day + i,
                title=title,
                description=f"Additional revision added due to low test score ({score:.0f}%).",
                topic=topic,
                category="revision",
                difficulty="easy",
                estimated_minutes=45,
            )
            db.add(new_task)

        # Notify student
        student_notif = Notification(
            student_id=student_id,
            notification_type=NotificationType.low_score,
            title=f"Additional {topic} Practice Added",
            message=f"Your {topic} test score was {score:.0f}%. We've added revision tasks to strengthen your foundation.",
        )
        db.add(student_notif)
        adapted = True
        message = f"Added 3 revision tasks for {topic} due to score {score:.0f}%"

    elif score > 85:
        # Skip remaining easy tasks on this topic and fast-track
        easy_pending = [
            t for t in roadmap.tasks
            if t.topic == topic
            and t.status == "pending"
            and t.difficulty == "easy"
            and t.day_number > last_day
        ]
        for t in easy_pending[:2]:  # skip up to 2 easy tasks
            t.status = "skipped"

        # Update skill level if skill_id provided
        if skill_id:
            student_skill = db.query(StudentSkill).filter(
                StudentSkill.student_id == student_id,
                StudentSkill.skill_id == skill_id,
            ).first()
            if student_skill and student_skill.level < 5:
                student_skill.level = min(student_skill.level + 1, 5)

        student_notif = Notification(
            student_id=student_id,
            notification_type=NotificationType.milestone,
            title=f"Great work on {topic}!",
            message=f"Your {topic} test score was {score:.0f}%. You've been fast-tracked to advanced content.",
        )
        db.add(student_notif)
        adapted = True
        message = f"Fast-tracked {topic}: skipped easy tasks, advanced to harder content."

    db.commit()
    return {"adapted": adapted, "message": message}


def get_completion_percentage(roadmap: Roadmap) -> float:
    tasks = roadmap.tasks
    if not tasks:
        return 0.0
    completed = sum(1 for t in tasks if t.status == "completed")
    return round(completed / len(tasks) * 100, 1)
