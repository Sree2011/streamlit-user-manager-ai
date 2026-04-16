# backend/main.py

from fastapi import FastAPI
from backend import routes

# --- FastAPI setup ---
app = FastAPI(
    title="AI Resume Analyzer",
    description="Analyze resumes and match them with job descriptions using NLP + Ollama",
    version="0.2.0"
)

# Include routes from routes.py
app.include_router(routes.router)

@app.get("/")
def root():
    return {"message": "AI Resume Analyzer is running"}


# --- Streamlit UI ---
# Run separately with: streamlit run backend/main.py
try:
    import streamlit as st
    from backend.services import extractor, matcher, ollama_api

    def run_ui():
        st.title("📄 AI Resume Analyzer")

        st.sidebar.header("Upload Resume")
        uploaded_file = st.sidebar.file_uploader("Choose a resume (PDF/DOCX)", type=["pdf", "docx", "txt"])

        job_description = st.text_area("Paste Job Description", height=200)

        if uploaded_file and st.button("Analyze Resume"):
            # Extract text
            resume_text = st.session_state.get("resume_text", None)
            if not resume_text:
                resume_text = extractor.extract_text(uploaded_file)
                st.session_state["resume_text"] = resume_text

            st.subheader("Resume Text")
            st.write(resume_text[:1000] + "...")  # show preview

            # Extract skills
            skills = extractor.extract_skills(resume_text)
            st.subheader("Extracted Skills")
            st.write(skills)

            # Match score
            if job_description:
                score = matcher.calculate_match(skills, job_description)
                st.subheader("Match Score")
                st.write(f"{score}%")

                # Ollama insights
                insights = ollama_api.get_llm_insights(resume_text, job_description)
                st.subheader("LLM Insights")
                st.write(insights)

    # Only run Streamlit if executed directly
    if __name__ == "__main__":
        run_ui()

except ImportError:
    # Streamlit not installed or not running in UI mode
    pass
