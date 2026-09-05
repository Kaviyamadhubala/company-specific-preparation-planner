"""
Company Recommendation Engine.

Calculates a match score between a student profile and each company
using multiple weighted factors. All weights are configurable via DB.
"""
from typing import List, Dict
from sqlalchemy.orm import Session

from app.models import Student, StudentSkill, Company, CompanyRole, CompanySkill, Skill, Test
from app.services.readiness import calculate_readiness

# Default recommendation weights
DEFAULT_REC_WEIGHTS = {
    "skill_match": 40.0,
    "role_match": 20.0,
    "eligibility": 15.0,
    "academic": 10.0,
    "performance": 15.0,
}


def calculate_company_match(
    db: Session,
    student_id: int,
    company: Company,
) -> dict:
    """Calculate the match score between a student and a specific company."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return {"company_id": company.id, "score": 0.0}

    company_roles = db.query(CompanyRole).filter(
        CompanyRole.company_id == company.id,
        CompanyRole.is_active == True,
    ).all()

    if not company_roles:
        return {
            "company_id": company.id,
            "company_name": company.name,
            "readiness_score": 0.0,
            "skill_match": 0.0,
            "is_eligible": False,
            "reason": "No active roles for this company.",
        }

    # Find the best matching role for this student
    best_score = 0.0
    best_role_id = None
    best_readiness = None

    for cr in company_roles:
        try:
            readiness = calculate_readiness(db, student_id, company.id, cr.id)
            if readiness["overall_score"] > best_score:
                best_score = readiness["overall_score"]
                best_role_id = cr.id
                best_readiness = readiness
        except Exception:
            continue

    if best_readiness is None:
        return {
            "company_id": company.id,
            "company_name": company.name,
            "logo_color": company.logo_color,
            "logo_initials": company.logo_initials,
            "industry": company.industry,
            "difficulty": company.difficulty.value if hasattr(company.difficulty, 'value') else company.difficulty,
            "readiness_score": 0.0,
            "skill_match": 0.0,
            "is_eligible": True,
            "reason": "Not enough skill data to calculate match.",
        }

    # Eligibility factor
    is_eligible = best_readiness["is_eligible"]
    eligibility_score = 100.0 if is_eligible else 40.0

    # Academic score based on CGPA (normalized to 0-100)
    academic_score = min((student.cgpa or 6.0) / 10.0 * 100, 100.0)

    # Performance score: average of recent test scores
    recent_tests = (
        db.query(Test)
        .filter(Test.student_id == student_id, Test.submitted_at.isnot(None))
        .order_by(Test.submitted_at.desc())
        .limit(5)
        .all()
    )
    perf_score = sum(t.total_score or 0 for t in recent_tests) / len(recent_tests) if recent_tests else 50.0

    # Role match: does student's preferred role match company roles?
    role_match = 50.0
    if student.preferred_role:
        for cr in company_roles:
            role = cr.role
            if role and student.preferred_role.lower() in role.name.lower():
                role_match = 90.0
                break

    weights = DEFAULT_REC_WEIGHTS
    total_w = sum(weights.values())

    overall = (
        (best_score * weights["skill_match"]) +
        (role_match * weights["role_match"]) +
        (eligibility_score * weights["eligibility"]) +
        (academic_score * weights["academic"]) +
        (perf_score * weights["performance"])
    ) / total_w

    overall = round(min(overall, 100.0), 1)

    # Build reason string
    weak_areas = best_readiness.get("top_weak_areas", [])
    if weak_areas:
        reason = f"Strong in most areas. Focus on: {', '.join(weak_areas)}."
    elif overall >= 80:
        reason = "Excellent match! Your skills align well with this company."
    elif overall >= 60:
        reason = "Good match. Minor improvements needed in some areas."
    else:
        reason = "More preparation needed before applying to this company."

    return {
        "company_id": company.id,
        "company_name": company.name,
        "logo_color": company.logo_color,
        "logo_initials": company.logo_initials,
        "industry": company.industry,
        "difficulty": company.difficulty.value if hasattr(company.difficulty, 'value') else str(company.difficulty),
        "readiness_score": overall,
        "skill_match": round(best_score, 1),
        "is_eligible": is_eligible,
        "reason": reason,
    }


def get_recommended_companies(db: Session, student_id: int, limit: int = 5) -> List[dict]:
    """Return top matching companies for a student, sorted by match score."""
    companies = db.query(Company).filter(Company.is_active == True).all()

    results = []
    for company in companies:
        match = calculate_company_match(db, student_id, company)
        results.append(match)

    results.sort(key=lambda x: x["readiness_score"], reverse=True)
    return results[:limit]
