"""
Readiness Score Engine — Core calculation logic.

Calculates a weighted readiness score from actual student skill levels
vs company-required skill levels. No random values — all derived from data.
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.models import (
    Student, StudentSkill, Company, CompanyRole, CompanySkill,
    ReadinessWeight, Skill
)

# Default weights (used if DB not seeded yet)
DEFAULT_WEIGHTS: Dict[str, float] = {
    "technical": 35.0,
    "dsa": 20.0,
    "aptitude": 15.0,
    "cs_fundamentals": 10.0,
    "communication": 10.0,
    "interview": 10.0,
}

LEVEL_LABELS = {
    0: "Not Started",
    1: "Beginner",
    2: "Basic",
    3: "Intermediate",
    4: "Advanced",
    5: "Expert",
}


def get_gap_status(student_level: int, required_level: int) -> str:
    if student_level == 0 and required_level > 0:
        return "not_started"
    gap = required_level - student_level
    if gap <= 0:
        return "ready"
    elif gap == 1:
        return "needs_improvement"
    else:
        return "major_gap"


def get_skill_percentage(student_level: int, required_level: int) -> float:
    if required_level == 0:
        return 100.0
    return min(student_level / required_level, 1.0) * 100


def get_weights(db: Session) -> Dict[str, float]:
    weights_rows = db.query(ReadinessWeight).all()
    if weights_rows:
        return {row.category: row.weight_pct for row in weights_rows}
    return DEFAULT_WEIGHTS


def calculate_readiness(
    db: Session,
    student_id: int,
    company_id: int,
    company_role_id: int,
) -> dict:
    """
    Main readiness calculation function.

    Returns:
        overall_score (float): 0-100
        breakdown (list): per-category weighted scores
        skill_gaps (list): per-skill gap details
        top_weak_areas (list): top weak skill names
        is_eligible (bool): meets CGPA requirement
    """
    # Fetch student skills as a dict: skill_id -> level
    student_skills_rows = (
        db.query(StudentSkill)
        .filter(StudentSkill.student_id == student_id)
        .all()
    )
    student_skill_map: Dict[int, int] = {
        ss.skill_id: ss.level for ss in student_skills_rows
    }

    # Fetch company role required skills
    company_skill_rows = (
        db.query(CompanySkill)
        .filter(CompanySkill.company_role_id == company_role_id)
        .all()
    )

    if not company_skill_rows:
        return {
            "overall_score": 0.0,
            "breakdown": [],
            "skill_gaps": [],
            "top_weak_areas": [],
            "is_eligible": True,
            "eligibility_note": "No skill requirements defined for this role.",
        }

    weights = get_weights(db)

    # Build per-skill gap data
    skill_gaps = []
    category_scores: Dict[str, List[float]] = {cat: [] for cat in weights}

    for cs in company_skill_rows:
        skill = db.query(Skill).filter(Skill.id == cs.skill_id).first()
        if not skill:
            continue

        student_level = student_skill_map.get(cs.skill_id, 0)
        required_level = cs.required_level
        gap = required_level - student_level
        status = get_gap_status(student_level, required_level)
        pct = get_skill_percentage(student_level, required_level)

        skill_gaps.append({
            "skill_id": cs.skill_id,
            "skill_name": skill.name,
            "skill_category": skill.category,
            "student_level": student_level,
            "student_level_label": LEVEL_LABELS.get(student_level, "Unknown"),
            "required_level": required_level,
            "required_level_label": LEVEL_LABELS.get(required_level, "Unknown"),
            "gap": gap,
            "status": status,
            "percentage": round(pct, 1),
            "weight": cs.weight,
        })

        # Accumulate score into the correct category
        cat = skill.category if skill.category in category_scores else "technical"
        category_scores[cat].append(pct)

    # Calculate per-category scores
    breakdown = []
    total_weight = sum(weights.values()) or 100.0

    for cat, weight in weights.items():
        scores = category_scores.get(cat, [])
        cat_score = sum(scores) / len(scores) if scores else 50.0  # neutral if no data
        weighted = (cat_score * weight) / total_weight
        breakdown.append({
            "category": cat,
            "score": round(cat_score, 1),
            "weight": weight,
            "weighted_score": round(weighted, 2),
        })

    overall_score = sum(b["weighted_score"] for b in breakdown)
    overall_score = round(min(overall_score, 100.0), 1)

    # Top weak areas: skills sorted by % ascending
    sorted_gaps = sorted(skill_gaps, key=lambda x: x["percentage"])
    top_weak_areas = [g["skill_name"] for g in sorted_gaps if g["status"] in ("major_gap", "not_started")][:3]
    if not top_weak_areas:
        top_weak_areas = [g["skill_name"] for g in sorted_gaps[:3]]

    # Eligibility check
    student = db.query(Student).filter(Student.id == student_id).first()
    company = db.query(Company).filter(Company.id == company_id).first()
    is_eligible = True
    eligibility_note = "You meet the basic eligibility criteria."
    if student and company and student.cgpa is not None:
        if student.cgpa < company.min_cgpa:
            is_eligible = False
            eligibility_note = f"Your CGPA ({student.cgpa}) is below the minimum required ({company.min_cgpa}). Some companies may still consider you."

    return {
        "student_id": student_id,
        "company_id": company_id,
        "company_role_id": company_role_id,
        "overall_score": overall_score,
        "breakdown": breakdown,
        "skill_gaps": skill_gaps,
        "top_weak_areas": top_weak_areas,
        "is_eligible": is_eligible,
        "eligibility_note": eligibility_note,
    }
