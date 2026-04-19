# backend/services/matcher.py

import re


def calculate_match(skills, job_description: str) -> float:
    """
    Compare extracted resume skills with job description.
    Returns a match score (0–100).
    """

    if not skills or not job_description:
        return 0.0

    jd_text = job_description.lower()
    matched = 0
    for skill in skills:
        if re.search(rf"\b{re.escape(skill.lower())}\b", jd_text):
            matched += 1

    score = (matched / len(skills)) * 100 if skills else 0.0
    return round(score, 2)


def build_skill_dict(skills):
    skill_counts = {}
    for skill in skills or []:
        normalized = skill.strip()
        if normalized:
            skill_counts[normalized] = skill_counts.get(normalized, 0) + 1
    return skill_counts


def compare_skill_dicts(resume_skill_dict: dict, jd_skill_dict: dict) -> dict:
    resume_only = [skill for skill in resume_skill_dict if skill not in jd_skill_dict]
    jd_only = [skill for skill in jd_skill_dict if skill not in resume_skill_dict]
    common_skills = {
        skill: {
            "resume_count": resume_skill_dict[skill],
            "jd_count": jd_skill_dict[skill]
        }
        for skill in resume_skill_dict
        if skill in jd_skill_dict
    }

    resume_match = (len(common_skills) / len(resume_skill_dict) * 100) if resume_skill_dict else 0.0
    jd_coverage = (len(common_skills) / len(jd_skill_dict) * 100) if jd_skill_dict else 0.0
    overall_score = round((resume_match + jd_coverage) / 2, 2)

    return {
        "common_skills": common_skills,
        "resume_only": resume_only,
        "jd_only": jd_only,
        "resume_match_percentage": round(resume_match, 2),
        "jd_coverage_percentage": round(jd_coverage, 2),
        "match_score": overall_score,
    }
