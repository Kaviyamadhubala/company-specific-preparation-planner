"""Resume text extraction and skill matching service."""
import re
from typing import List, Tuple

# Common programming languages to look for in resumes
PROGRAMMING_LANGUAGES = [
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go",
    "rust", "kotlin", "swift", "ruby", "php", "scala", "r", "matlab",
    "html", "css", "sql", "bash", "shell"
]

TECH_SKILLS = [
    "react", "angular", "vue", "node.js", "nodejs", "express", "django",
    "flask", "fastapi", "spring", "spring boot", "hibernate", "docker",
    "kubernetes", "aws", "azure", "gcp", "git", "github", "linux",
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "rest api", "graphql", "microservices", "ci/cd", "jenkins",
    "machine learning", "deep learning", "tensorflow", "pytorch",
    "pandas", "numpy", "scikit-learn", "hadoop", "spark"
]

CS_CONCEPTS = [
    "data structures", "algorithms", "oop", "object oriented",
    "dbms", "database", "operating systems", "computer networks",
    "system design", "dsa", "design patterns", "solid principles"
]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from PDF bytes using pypdf."""
    try:
        import io
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        return ""


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Decode plain text files."""
    try:
        return file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def extract_skills_from_text(text: str) -> dict:
    """
    Parse resume text and extract skill information.
    Returns dict with programming_languages, tech_skills, cs_concepts, 
    projects (headings found), certifications.
    """
    text_lower = text.lower()

    # Extract programming languages
    found_languages = [lang for lang in PROGRAMMING_LANGUAGES if lang in text_lower]

    # Extract tech skills
    found_tech = [skill for skill in TECH_SKILLS if skill in text_lower]

    # Extract CS concepts
    found_cs = [concept for concept in CS_CONCEPTS if concept in text_lower]

    # Heuristic: find project section
    project_pattern = r"(?:projects?|project experience)\s*\n(.*?)(?=\n[A-Z]|\Z)"
    project_matches = re.findall(project_pattern, text, re.IGNORECASE | re.DOTALL)
    projects = []
    if project_matches:
        lines = project_matches[0].strip().split("\n")
        for line in lines:
            line = line.strip()
            if len(line) > 10 and not line.startswith("•") and not line.startswith("-"):
                projects.append(line[:80])
            if len(projects) >= 5:
                break

    # Heuristic: certifications
    cert_pattern = r"(?:certification|certified|certificate)[^\n]*"
    certs = re.findall(cert_pattern, text, re.IGNORECASE)
    certifications = list(set(c.strip()[:80] for c in certs))[:5]

    # Combine all found skills into a unified list
    all_skills = list(set(found_languages + found_tech + found_cs))

    return {
        "programming_languages": found_languages,
        "tech_skills": found_tech,
        "cs_concepts": found_cs,
        "all_skills": all_skills,
        "projects": projects,
        "certifications": certifications,
    }


def compare_with_company_requirements(
    extracted_skills: List[str],
    required_skills: List[str],
) -> dict:
    """
    Compare extracted resume skills against company requirements.
    
    Returns matched, missing skills and a match score.
    """
    extracted_lower = {s.lower() for s in extracted_skills}
    required_lower = {s.lower(): s for s in required_skills}

    matched = []
    missing = []

    for req_lower, req_original in required_lower.items():
        found = any(req_lower in ext or ext in req_lower for ext in extracted_lower)
        if found:
            matched.append(req_original)
        else:
            missing.append(req_original)

    match_score = (len(matched) / len(required_skills) * 100) if required_skills else 0.0

    recommendations = []
    if missing:
        for skill in missing[:3]:
            recommendations.append(f"Add projects or experience demonstrating {skill}.")
    if match_score >= 80:
        recommendations.append("Your resume aligns well with the role requirements.")
    elif match_score >= 50:
        recommendations.append("Focus on adding missing skills through projects or certifications.")
    else:
        recommendations.append("Consider building 1-2 targeted projects to cover the skill gaps.")

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_score": round(match_score, 1),
        "recommendations": recommendations,
    }
