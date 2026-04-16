# ai_resume_analyser/backend/api_main.py

from fastapi import FastAPI

from backend import routes

app = FastAPI(
    title="AI Resume Analyzer API",
    description="Backend API for resume analysis and job matching",
    version="1.0.0"
)

# Include all routes
app.include_router(routes.router)

@app.get("/")
def root():
    return {"message": "AI Resume Analyzer API is running"}
