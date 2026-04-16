# backend/services/matcher.py

import re

def calculate_match(skills, job_description: str) -> float:
    """
    Compare extracted resume skills with job description.
    Returns a match score (0–100).
    """

    if not skills or not job_description:
        return 0.0

    # Normalize job description text
    jd_text = job_description.lower()

    matched = 0
    for skill in skills:
        if re.search(rf"\b{skill.lower()}\b", jd_text):
            matched += 1

    # Calculate percentage overlap
    score = (matched / len(skills)) * 100 if skills else 0.0
    return round(score, 2)
