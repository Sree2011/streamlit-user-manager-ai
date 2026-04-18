import ollama
import json
import re
from typing import List, Dict, AsyncGenerator


# -------------------------------
# 0. Text Cleaning
# -------------------------------
def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing extra whitespaces and normalizing line breaks.
    """
    if not text:
        return ""
    # Replace multiple whitespaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


# -------------------------------
# 1. Prompt Generator
# -------------------------------
def build_prompt(resume_text: str, job_description: str) -> str:
    # Clean and truncate inputs to fit within model context limits
    resume_text = clean_text(resume_text)
    job_description = clean_text(job_description)
    resume_text = resume_text[:2000] if len(resume_text) > 2000 else resume_text
    job_description = job_description[:1000] if len(job_description) > 1000 else job_description
    
    return f"""
You are a STRICT JSON generator.

### OUTPUT RULES (MANDATORY)
- Output ONLY valid JSON.
- NO markdown, NO explanations, NO extra text.
- Must be parseable using json.loads().
- Do NOT include trailing commas.
- Use double quotes for all JSON keys and string values.

### JSON FORMAT (EXACT)
[
  {{
    "skill_in_jd": "string",
    "matched_in_resume": "Yes or No",
    "evidence": "string"
  }}
]

### EXTRACTION RULES
- Extract ONLY technical skills (languages, frameworks, tools, concepts).
- Ignore soft skills.
- Normalize:
  - Spring Boot → Spring
  - MySQL → SQL
  - REST API → REST
- If missing → "matched_in_resume": "No"
- Evidence must come ONLY from resume or "Not found".

### INPUT
JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

### TASK
Generate JSON array now.
"""


# -------------------------------
# 2. Call Ollama (Blocking)
# -------------------------------
def call_ollama(prompt: str, model: str = "phi3") -> str:
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0,
                "top_p": 0.9,
                "repeat_penalty": 1.2,
            }
        )
        return response["message"]["content"]
    except Exception as e:
        # If Ollama fails, return a default JSON response
        print(f"Ollama error: {e}")
        return '[{"skill_in_jd": "Error", "matched_in_resume": "No", "evidence": "Ollama service unavailable"}]' 


# -------------------------------
# 3. Call Ollama (Streaming)
# -------------------------------
async def stream_ollama(prompt: str, model: str = "phi3") -> AsyncGenerator[str, None]:
    """
    Async generator that yields chunks of text from Ollama.
    """
    stream = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        options={
            "temperature": 0,
            "top_p": 0.9,
            "repeat_penalty": 1.2,
        }
    )
    for chunk in stream:
        if "message" in chunk and "content" in chunk["message"]:
            yield chunk["message"]["content"]


# -------------------------------
# 4. Safe JSON Parsing
# -------------------------------
def extract_json(text: str) -> List[Dict]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            # Try fixing single quotes to double quotes
            fixed_text = text.replace("'", '"')
            return json.loads(fixed_text)
        except json.JSONDecodeError:
            try:
                match = re.search(r"\[\s*{.*?}\s*\]", text, re.DOTALL)
                if match:
                    fixed_match = match.group().replace("'", '"')
                    return json.loads(fixed_match)
            except json.JSONDecodeError:
                pass
            raise ValueError("Failed to extract valid JSON from model output.")


# -------------------------------
# 5. Convert JSON → Markdown Table
# -------------------------------
def json_to_markdown(data: List[Dict]) -> str:
    table = "| Skill in JD | Matched in Resume | Evidence/Insight |\n"
    table += "| :--- | :--- | :--- |\n"
    for item in data:
        table += f"| {item.get('skill_in_jd','')} | {item.get('matched_in_resume','')} | {item.get('evidence','')} |\n"
    return table


# -------------------------------
# 6. Compute Match Score
# -------------------------------
def compute_match_score(data: List[Dict]) -> Dict:
    total = len(data)
    matched = sum(1 for d in data if d.get("matched_in_resume") == "Yes")
    missing_skills = [d.get("skill_in_jd") for d in data if d.get("matched_in_resume") == "No"]
    score = (matched / total) * 100 if total > 0 else 0
    return {"match_percentage": round(score, 2), "missing_skills": missing_skills}


# -------------------------------
# 7. Main Pipeline Function (Blocking)
# -------------------------------
def match_job(resume_text: str, job_description: str) -> Dict:
    prompt = build_prompt(resume_text, job_description)
    raw_output = call_ollama(prompt)
    parsed_json = extract_json(raw_output)
    markdown_table = json_to_markdown(parsed_json)
    score_data = compute_match_score(parsed_json)
    return {
        "table": markdown_table,
        "match_percentage": score_data["match_percentage"],
        "missing_skills": score_data["missing_skills"],
        "raw_json": parsed_json
    }


# -------------------------------
# 8. Streaming Pipeline Function
# -------------------------------
async def stream_resume_analysis(resume_text: str, job_description: str):
    prompt = build_prompt(resume_text, job_description)

    # Ollama streaming call
    stream = ollama.chat(
        model="phi3",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        options={"temperature": 0, "top_p": 0.9, "repeat_penalty": 1.2}
    )

    # Yield chunks incrementally
    for chunk in stream:
        if "message" in chunk and "content" in chunk["message"]:
            yield chunk["message"]["content"]
