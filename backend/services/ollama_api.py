# backend/services/ollama_api.py
from ollama import chat
import os

def ollama_chat(prompt: str, model: str | None = None) -> str:
    """
    Call Ollama using the Python client.
    Reads model name from environment variable unless overridden.
    """
    model_name = model or os.getenv("OLLAMA_MODEL_NAME", "llama2")

    messages = [
        {"role": "user", "content": prompt}
    ]

    try:
        response = chat(model=model_name, messages=messages)
        content = getattr(response.message, "content", None)
        return content.strip() if content else "No response content from Ollama."
    except Exception as e:
        return f"Ollama API error: {str(e)}"



def get_llm_insights(resume_text: str, job_description: str) -> str:
    """
    Generate insights comparing resume with job description.
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

    return ollama_chat(prompt, "llama2")
