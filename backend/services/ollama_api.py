# backend/services/ollama_api.py

import requests

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama2"   # change to the model you have pulled in Ollama

def get_llm_insights(resume_text: str, job_description: str) -> str:
    """
    Call Ollama locally to generate insights about how well the resume matches the job description.
    """

    prompt = f"""
    You are an AI Resume Analyzer.
    Compare the following resume with the job description.
    Highlight strengths, missing skills, and give a short summary of fit.

    Resume:
    {resume_text}

    Job Description:
    {job_description}
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        return f"Ollama API error: {str(e)}"
