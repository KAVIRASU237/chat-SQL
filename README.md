# ChatSQL

Offline Natural Language → SQL assistant (RAG + Local LLM)

ChatSQL is a production-ready, offline, and secure Text-to-SQL system that lets users query and manage structured databases in plain English. It uses Retrieval-Augmented Generation (RAG) to make the LLM schema-aware and runs models locally via Ollama so no application data is sent to the cloud.

---

## 🚀 Key Features

- **100% Offline Execution**: Uses Ollama + local LLMs (e.g., Mistral) for privacy and speed.
- **Smart RAG-based Schema Retrieval**: FAISS-powered retrieval context so the model only sees pertinent schema fragments.
- **🔥 NEW: Smart Auto Re-indexing**: Automatically detects schema changes (CREATE/ALTER/DROP) using MD5 hashing and re-indexes without manual intervention.
- **🛡️ Secure Admin Portal**:
    - **Password Protected**: Secure admin login using Argon2 hashing and JWT tokens.
    - **Full CRUD Support**: Admins can use natural language to `INSERT`, `UPDATE`, or `DELETE` records.
    - **Raw SQL Terminal**: Direct, unfiltered SQL execution for power users.
    - **Structure Discovery**: Ask AI to *"Describe table X"* to see full column details, types, and constraints.
    - **Action Logging**: Every administrative action is logged for security auditing.
- **🛡️ Safe User Mode**:
    - **Read-Only**: Regular users are restricted to `SELECT` queries only.
    - **SQL Validation**: Multi-layer protection blocks all destructive DML/DDL commands.
- **Intelligent Data Visualization**: 
    - Automatically generates **Bar and Line charts** based on query results.
    - Uses heuristics to identify categorical X-axes and numeric Y-axes.
    - Renders high-quality PNGs directly in the chat interface via Base64 encoding.
- **Intelligent Insights**: AI-generated non-technical summaries for every query result or database action.

---

## 🛠️ Architecture Overview

User/Admin → Premium Web UI → FastAPI Backend → Smart RAG Pipeline (FAISS + Hash Tracking) → Local LLM (Ollama) → SQL Validator (User-only) → SQLite → Result Visualization (Tables/Graphs)

---

## 💻 Tech Stack

- **Backend**: Python (FastAPI)
- **Security**: Argon2 (Password Hashing), JWT (Session Management)
- **LLM Runtime**: Ollama (local), Mistral recommended
- **RAG Engine**: FAISS with MD5-based Hash Tracking
- **Database**: SQLite (Data isolation between App and Admin credentials)
- **Frontend**: Vanila HTML, CSS (Premium Design Tokens), JavaScript
- **Visualization**: Matplotlib, Pandas

---

## 📊 Data Visualization

ChatSQL includes a built-in `GraphGeneratorService` that turns raw data into visual insights:

- **Auto-plotting**: If a query returns numeric data, the system automatically attempts to generate a relevant chart.
- **Smart Axis Detection**: It identifies labels (strings/dates) for the X-axis and values (integers/floats) for the Y-axis.
- **Responsive Charts**: Charts are generated as 10x6 PNGs and resized dynamically for web and mobile.

---

## 🏗️ Project Layout

```
backend/
  main.py               # FastAPI Entry Point
  services/
    rag_service.py      # Smart RAG with Hash Tracking
    sql_generator.py    # Multi-role SQL generation (Admin/User)
    db_executor.py      # Transaction-aware SQL execution
    auth_service.py     # Argon2 & JWT Security
    admin_service.py    # Admin DB & Audit Logging
  routers/
    admin.py            # Admin API Endpoints
  utils/
    schema_extractor.py # Database Metadata Crawler
    sql_validator.py    # Security Policy Enforcer

frontend/
  index.html            # User Home Page
  admin_login.html      # Secure Admin Portal
  admin_dashboard.html  # Premium Admin Console
  style.css             # Unified Design System
  app.js                # Core JS Logic

data/
  sample.db             # Application Data
  admin.db              # Isolated Admin Credentials & Logs
```

---

## 🔐 Security Model

- **Admin Isolation**: Admin credentials and audit logs are stored in a separate database from user data.
- **Role-Based Access**: JWT-based enforcement ensures only authenticated admins can perform write operations.
- **Offline First**: Zero cloud calls. All models and data remain on your local machine.
- **Automatic Sync**: Schema changes are detected via hashing to ensure the AI always has the latest "truth."

---

## 📝 Example Usage

### User Query
> *"Show me all products priced over 100"*

### Admin Command
> *"Update the price of 'Laptop' to 1500"*
> **AI Insight**: *"The product price has been successfully updated to 1500 for 'Laptop'."*

### Structure Discovery (Admin)
> *"Describe the products table"*
> **Result**: Returns a table with `cid`, `name`, `type`, `notnull`, etc.

---

## 🚀 Quickstart

1. **Install Ollama**: [ollama.com](https://ollama.com/)
2. **Pull Model**: `ollama pull mistral`
3. **Install Deps**: `pip install -r requirements.txt`
4. **Run Server**: `uvicorn backend.main:app --reload`
5. **Login**: Visit `/static/admin_login.html` (Default: `admin` / `admin123`)

or 

1. Clone the repository
```bash
git clone https://github.com/KAVIRASU237/chat-SQL.git
cd chat-SQL
```

2. Create and activate a virtual environment
- macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
- Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Install Python dependencies
```bash
pip install -r requirements.txt
```

4. Install Ollama and pull the local model
- Install Ollama: https://ollama.com/
- Pull the model (Mistral is recommended):
```bash
ollama pull mistral
```
Note: the model download is ~4 GB.

5. Initialize the sample database and FAISS index
```bash
python -m backend.utils.setup_sample_db
```
This creates:
- a sample SQLite database (data/sample.db)
- a FAISS index with schema embeddings

6. Start the backend server
- Recommended (direct uvicorn):
```bash
uvicorn backend.main:app --reload
```
- Alternative (module form):
```bash
python -m uvicorn backend.main:app --reload
```

7. Open the application
Visit: http://localhost:8000
---

## ⚖️ License

MIT License
Copyright (c) 2026 Kavir
