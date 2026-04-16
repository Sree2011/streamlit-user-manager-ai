Here’s a solid **README.md** draft you can drop straight into your repo. It’s tailored for your setup (FastAPI, Ollama, GitHub Actions, no Docker):

---

# AI Resume Analyzer

An AI-powered tool to analyze resumes and match them with job descriptions.  
Built with **FastAPI**, **spaCy**, and **Ollama LLMs**, deployed with **GitHub Actions CI/CD**.

---

## 🚀 Features
- Upload resumes (PDF/DOCX) and extract text
- Skill extraction using regex + spaCy
- Job description input for comparison
- Match score calculation (skills overlap + LLM insights)
- REST API endpoints with Swagger docs
- CI/CD pipeline via GitHub Actions

---

## 📂 Project Structure
```
ai-resume-analyzer/
│
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── routes.py            # API endpoints
│   ├── models.py            # Pydantic models
│   ├── services/
│   │   ├── extractor.py     # Skill extraction logic
│   │   ├── matcher.py       # Job‑resume matching logic
│   │   └── ollama_api.py    # Ollama LLM integration
│   └── utils.py             # Helper functions
│
├── tests/                   # Unit tests
├── requirements.txt         # Dependencies
├── .github/workflows/ci.yml # GitHub Actions pipeline
├── README.md                # Project overview
└── docs/                    # API docs + diagrams
```

---

## ⚙️ Installation
```bash
# Clone repo
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn backend.main:app --reload
```

---

## 🔗 API Endpoints
- `POST /upload_resume` → Upload resume file
- `POST /analyze_resume` → Extract skills
- `POST /match_job` → Compare resume with job description

Swagger docs available at:  
`http://localhost:8000/docs`

---

## 🤖 Ollama Integration
This project uses **Ollama** for LLM-based insights.  
Make sure Ollama is installed and running locally:

```bash
ollama run llama2
```

Configure `ollama_api.py` to call the local Ollama server.

---

## ✅ CI/CD
GitHub Actions pipeline runs:
- Install dependencies
- Lint code
- Run tests

Workflow file: `.github/workflows/ci.yml`

---

## 📌 Future Work
- Add a simple UI (Streamlit/React)
- Expand skill extraction with advanced NLP
- Store results in PostgreSQL/MongoDB
- Deploy on Azure App Service

---