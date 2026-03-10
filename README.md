# User Manager + AI Assistant

A Streamlit application that integrates **MySQL (via SQLAlchemy)** with **Ollama LLM** to enable natural‑language interaction with a user database.  
You can add users through structured CRUD operations or simply type instructions like *“Add a frontend developer named Arjun”* and the AI will insert them automatically.

---

## ✨ Features
- **Database Integration**: MySQL backend with SQLAlchemy ORM.  
- **CRUD Operations**: Add and list users directly from the UI.  
- **AI Assistant**: Ollama provides natural‑language reasoning and suggestions.  
- **Auto‑Creation**: Users can be added automatically from free‑form text prompts.  
- **Streamlit UI**: Simple, interactive interface for managing users and querying the AI.

---

## 🛠️ Tech Stack
- **Python 3.11+**  
- **Streamlit** for UI  
- **SQLAlchemy** + **PyMySQL** for database access  
- **Ollama** for LLM integration  

---

## 🚀 Getting Started

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/user-manager-ai.git
   cd user-manager-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up `.env` (local only, never commit)**
   ```env
   # Database configuration (example placeholders)
   DB_USER=appuser
   DB_PASSWORD=your_password_here
   DB_NAME=mydb
   DB_HOST=localhost
   ```

4. **Run the app**
   ```bash
   streamlit run main.py
   ```

---

## 📸 Demo
- Add a sample user with one click.  
- Ask Ollama questions like:  
  - *“Summarize the current team.”*  
  - *“Add a backend developer named Priya.”*  

---

## 📂 Project Structure
```
.
├── main.py                # Streamlit app
├── user_manager/
│   ├── models.py          # SQLAlchemy models
│   ├── crud.py            # CRUD functions
├── ai_assistant/
│   ├── ollama_client.py   # Ollama integration
└── requirements.txt
```

---

## 📌 Future Enhancements
- Add more fields (email, skills, projects).  
- Richer AI‑driven insights (team composition, role recommendations).  
- Deployment to cloud with environment variable secrets.  

---