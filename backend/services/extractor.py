# backend/services/extractor.py

import re
import spacy
from pdfminer.high_level import extract_text as pdf_extract
import docx

# Load spaCy model (small English model is enough for skills extraction)
nlp = spacy.load("en_core_web_sm")

# Predefined skill keywords and normalization rules
SKILL_KEYWORDS = [
    "Python", "Java", "FastAPI", "Spring Boot", "Spring", "SQL", "MySQL",
    "PostgreSQL", "MongoDB", "Azure", "Git", "CI/CD", "NLP", "LLM",
    "REST", "REST API", "REST APIs", "Angular", "React"
]

SKILL_NORMALIZATION = {
    "spring boot": "Spring",
    "rest api": "REST",
    "rest apis": "REST",
    "mysql": "SQL",
    "postgresql": "SQL",
    "ci/cd": "CI/CD",
    "ng": "Angular",
    "reactjs": "React"
}

SKILL_LOOKUP = {keyword.lower(): SKILL_NORMALIZATION.get(keyword.lower(), keyword) for keyword in SKILL_KEYWORDS}
SKILL_LOOKUP.update(SKILL_NORMALIZATION)

async def extract_text(file):
    if file is None:
        return ""

    file_name = file.filename.lower()
    file.file.seek(0)

    if file_name.endswith(".pdf"):
        content = pdf_extract(file.file)

    elif file_name.endswith(".docx"):
        doc = docx.Document(file.file)
        content = "\n".join([para.text for para in doc.paragraphs])

    else:
        content = file.read().decode("utf-8", errors="ignore")

    return content


def normalize_skill(skill: str) -> str:
    return SKILL_LOOKUP.get(skill.strip().lower(), skill.strip())


def extract_skill_dict(text: str) -> dict:
    if not text:
        return {}

    skill_counts = {}
    for keyword in SKILL_KEYWORDS:
        pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
        matches = pattern.findall(text)
        if matches:
            normalized = normalize_skill(keyword)
            skill_counts[normalized] = skill_counts.get(normalized, 0) + len(matches)

    return skill_counts


async def extract_skills(resume_text: str):
    """
    Extract skills from resume text using regex + spaCy keyword matching.
    """
    if not resume_text:
        return []

    skills_found = set(extract_skill_dict(resume_text).keys())

    doc = nlp(resume_text)
    for chunk in doc.noun_chunks:
        token = chunk.text.strip()
        normalized = normalize_skill(token)
        if normalized in SKILL_LOOKUP.values():
            skills_found.add(normalized)

    return list(skills_found)
