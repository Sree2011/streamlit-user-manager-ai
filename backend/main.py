# backend/main.py

from fastapi import FastAPI
from backend import routes

# Create FastAPI app
app = FastAPI(
    title="AI Resume Analyzer",
    description="Analyze resumes and match them with job descriptions using NLP + Ollama",
    version="0.1.0"
)

# Include routes from routes.py
app.include_router(routes.router)

# Root endpoint (health check)
@app.get("/")
def root():
    return {"message": "AI Resume Analyzer is running"}
