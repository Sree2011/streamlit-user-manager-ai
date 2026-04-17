# backend/services/ollama_api.py
from ollama import chat
import os
from typing import Generator

def ollama_chat(prompt: str, model: str | None = "phi3") -> Generator[str, None, None]:
    model_name: str = os.getenv("OLLAMA_MODEL_NAME", model or "phi3")
    messages = [{"role": "user", "content": prompt}]

    try:
        response = chat(model=model_name, messages=messages, stream=True)
        for chunk in response:
            yield chunk['message']['content']
    except Exception as e:
        yield f"Ollama API error: {str(e)}"

def get_llm_insights(resume_text: str, job_description: str) -> Generator[str, None, None]:
    """
    Refined prompt to force a Markdown table and prevent resume regeneration.
    """
    prompt = f"""
    [SYSTEM: TECHNICAL ANALYSIS MODE]
    You are a data extraction tool. Your ONLY task is to compare skills.
    
    [RULES]
    1. NEVER repeat the candidate's name, objective, or education.
    2. NEVER rewrite the resume sentences.
    3. ONLY output a Markdown table.
    4. Start the response IMMEDIATELY with the table header.
    
    [OUTPUT EXAMPLE]
    | Skill in JD | Matched in Resume | Evidence/Insight |
    | :--- | :--- | :--- |
    | Java | Yes | 2+ years at Accenture, Spring Boot projects. |
    | React | Yes | Listed in technical stack. |

    [DATA]
    JOB DESCRIPTION:
    {job_description}

    RESUME:
    {resume_text}

    [EXECUTE]
    Start the table now:
    """
    return ollama_chat(prompt, "phi3")