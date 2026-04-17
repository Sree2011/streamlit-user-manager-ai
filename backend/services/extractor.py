# backend/services/extractor.py

import re
import spacy
from pdfminer.high_level import extract_text as pdf_extract
import docx

# Load spaCy model (small English model is enough for skills extraction)
nlp = spacy.load("en_core_web_sm")

# Predefined skill keywords (expand as needed)
SKILL_KEYWORDS = [
    "Python", "Java", "FastAPI", "Spring Boot", "SQL", "MySQL",
    "PostgreSQL", "MongoDB", "Azure", "Git", "CI/CD", "NLP", "LLM"
]

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



async def extract_skills(resume_text: str):
    """
    Extract skills from resume text using regex + spaCy keyword matching.
    """
    skills_found = set()

    # Regex keyword search
    for skill in SKILL_KEYWORDS:
        if re.search(rf"\b{skill}\b", resume_text, re.IGNORECASE):
            skills_found.add(skill)

    # spaCy entity recognition (basic noun chunks)
    doc = nlp(resume_text)
    for chunk in doc.noun_chunks:
        token = chunk.text.strip()
        if token in SKILL_KEYWORDS:
            skills_found.add(token)

    return list(skills_found)
