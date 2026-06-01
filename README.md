# 📋 Decoupled Python Task Manager Application

[cite_start]A clean, responsive Kanban Board application built from scratch using pure Python[cite: 41, 80]. [cite_start]This project utilizes a completely decoupled system architecture consisting of a FastAPI backend service communicating with an interactive Streamlit UI web app[cite: 72, 80, 90].

## 🔗 Live Deployment Connections
* [cite_start]**Frontend Application Client:** [https://indpro-enauvdzvpm8xfqtzwjpazn.streamlit.app](https://indpro-enauvdzvpm8xfqtzwjpazn.streamlit.app) [cite: 343]
* [cite_start]**Backend API Sandbox Docs:** [https://jiban-taskmanager-api.onrender.com/docs](https://jiban-taskmanager-api.onrender.com/docs) [cite: 343]

## 🏗️ Architectural Layout & System Decisions
* [cite_start]**Backend Framework (FastAPI):** Selected to enforce automated data schema structures via Pydantic and provide immediate Swagger API testing interfaces (`/docs`)[cite: 72, 112].
* [cite_start]**Frontend UI (Streamlit):** Chosen to build a robust, secure presentation dashboard natively within Python, completely avoiding JavaScript complexity[cite: 80, 81, 87].
* [cite_start]**Database Pipeline (SQLAlchemy + SQLite):** Employs an agile Object-Relational Mapper interacting with local file storage (`task_manager.db`) to bypass database infrastructure overhead while ensuring user data isolation[cite: 73, 110, 150].
* [cite_start]**Security Layer:** Implements standard cryptographic password derivation via SHA-256 (`hashlib`) to avoid package compilation conflicts on modern Python 3.14 systems, operating alongside signed authorization bearer JWT tokens[cite: 74, 214, 234].

## 📋 Features Implemented
* [cite_start]**Authentication Flow:** Complete User Registration (`POST /register`) and Secure Login (`POST /login`) with state persistent sessions via `st.session_state`[cite: 37, 92, 96].
* [cite_start]**Task Management (CRUD):** Users can seamlessly Create, Read, Update, and Delete tasks unique to their own authenticated profile[cite: 38].
* [cite_start]**Kanban Board Stage Tracking:** Tasks are partitioned into three dedicated columns: **Todo**, **In Progress**, and **Done**[cite: 35, 97].
* [cite_start]**UX Considerations:** Explicitly handles visual loading states via `st.spinner()` and connection error states natively[cite: 42, 98].

## ⚖️ Assumptions & Structural Tradeoffs
* [cite_start]**Database File Management:** SQLite database persistence tracks information directly within the isolated web server instance[cite: 247, 248]. [cite_start]For a 3–4 hour delivery target, this alternative handles state transitions cleanly without provisioning cloud clusters[cite: 50, 56].
* [cite_start]**Decoupled Deployment:** Implemented as two completely separate applications talking securely via cross-origin web standard networks (configured via FastAPI CORS middleware) to satisfy mandatory deployment rules[cite: 45, 90, 320, 322].

## 🛠️ Local Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/INDPRO.git](https://github.com/YOUR_GITHUB_USERNAME/INDPRO.git)
   cd INDPRO

2.  **Set up virtual environment:**

python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

3. **Install dependencies:**

pip install -r requirements.txt

4. **Run the Backend:**

uvicorn backend.main:app --reload

5. **Run the Frontend (In a separate terminal):**

streamlit run frontend/app.py
