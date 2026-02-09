# ChatSQL

Offline Natural Language → SQL assistant (RAG + Local LLM)

ChatSQL is a production-ready, offline, and secure Text-to-SQL system that lets users query structured databases in plain English. It uses Retrieval-Augmented Generation (RAG) to make the LLM schema-aware and runs models locally via Ollama so no application data is sent to the cloud.

---

Table of contents
- [Why ChatSQL](#why-chatsql)
- [Key features](#key-features)
- [Architecture overview](#architecture-overview)
- [Tech stack](#tech-stack)
- [Accessibility](#accessibility)
- [Prerequisites](#prerequisites)
- [Quickstart — Installation & Run](#quickstart--installation--run)
- [Project layout](#project-layout)
- [Security model](#security-model)
- [Example usage](#example-usage)
- [Troubleshooting & tips](#troubleshooting--tips)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Why ChatSQL

Traditional Text-to-SQL systems often:
- Depend on cloud APIs
- Expose full database schemas to the model
- Allow unsafe SQL execution

ChatSQL addresses those concerns by being:
- Fully offline and local-first
- Schema-aware via RAG so the model only sees relevant schema fragments
- Secure by default: read-only SQL generation only

---

## Key features

- 100% offline execution using Ollama + a local LLM (e.g., Mistral).
- RAG-based schema retrieval (FAISS) so the model gets only pertinent schema context.
- Secure SQL generation:
  - Only `SELECT` queries are allowed.
  - Write/DDL operations (INSERT, UPDATE, DELETE, DROP, etc.) are blocked by the SQL validator.
- Modern web UI that shows generated SQL and results in a table.
- Local-first: SQLite database and local FAISS index.

---

## Architecture overview

User → Web UI (HTML/JS) → FastAPI backend → RAG pipeline (FAISS) → LLM via Ollama → SQL validator → SQLite → Query results displayed

---

## Tech stack

- Backend: Python (FastAPI)
- LLM runtime: Ollama (local), Mistral recommended
- RAG engine: FAISS
- Database: SQLite
- Frontend: HTML, CSS, JavaScript
- Server: Uvicorn

---

## Accessibility

We aim for an accessible UI. Notes for contributors and users:

- Semantic headings: use appropriate `<h1>`–`<h6>` to preserve outline.
- Keyboard navigation:
  - Primary controls should be reachable via Tab.
  - Ensure visible focus styles for interactive elements.
- ARIA:
  - Provide `aria-label` or `aria-labelledby` for non-text controls.
  - Use `role="status"` for dynamic status messages (e.g., "Generating SQL...").
- Color contrast:
  - Ensure foreground/background contrast meets WCAG AA (4.5:1 for normal text).
  - Prefer system fonts and avoid relying on color alone to convey state.
- Screen reader testing:
  - Test common flows (ask question → review SQL → view results) with NVDA/VoiceOver.
- Responsive layout:
  - UI should remain usable on narrow screens; ensure tables are scrollable and labelled.

If you want, I can add a short accessibility checklist or Lighthouse scoring commands to the repo.

---

## Prerequisites

- Python 3.9 or newer: https://www.python.org/downloads/
- Ollama: https://ollama.com/ (used to run local models)
- A local LLM (Mistral recommended). Model download size: ~4GB. Ensure a stable connection when pulling the model.

---

## Quickstart — Installation & Run

Commands assume a POSIX shell (macOS / Linux). Windows equivalents are provided.

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

## Project layout

High-level structure (names and purpose)

```
backend/
  main.py               # FastAPI entry point
  core/                 # App configuration
  services/             # RAG, SQL generation, DB execution
  utils/                # Schema extraction & SQL validation

frontend/
  index.html            # UI
  app.js                # Frontend logic
  style.css             # Styling

data/
  sample.db             # SQLite DB (example)
  faiss_index/          # FAISS vector index for schema

requirements.txt
README.md
```

Adjust paths above if your repo structure differs.

---

## Security model

- ✅ Read-only database access
- ❌ No write operations allowed through the generated queries
- ❌ No cloud calls (models run locally)
- ❌ Schema is **not** fully exposed to the model — only retrieved fragments are sent

This design makes ChatSQL appropriate for:
- Internal company databases
- Privacy-sensitive local analytics
- Demos and offline use-cases

---

## Example usage

User question (natural language):
> Give me product details

Generated SQL (example):
```sql
SELECT name, category, price FROM products;
```

Example result (tabular):
| name | category | price |
|------|----------|-------|
| A    | Tech     | 500   |
| B    | Home     | 120   |

---

## Troubleshooting & tips

- Ollama model not found:
  - Ensure `ollama` CLI is installed and the model was pulled:
  ```bash
  ollama list
  ollama pull mistral
  ```
- FAISS or setup errors:
  - Re-run the setup script:
  ```bash
  python -m backend.utils.setup_sample_db
  ```
  - Check the script logs and ensure `data/faiss_index/` exists.
- Uvicorn errors:
  - Confirm Python venv is active and dependencies installed.
  - Run without `--reload` to reduce resource usage in production.
- Debugging SQL validator:
  - Validator should reject non-SELECT queries. If a valid SELECT is rejected, check logs for the specific validation rule message.

---

## Contributing

Contributions are welcome. Suggested workflow:
1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Add tests where appropriate
4. Open a Pull Request describing the change and motivation

Please follow these guidelines:
- Keep accessibility in mind for UI changes
- Add or update tests for backend logic (RAG, validator)
- Keep secrets out of commits (no plaintext DB credentials, tokens, or model keys)

---

## License

Specify your project license here (e.g., MIT). Example:
```
MIT License
Copyright (c) 2026 Kavirasu
```

(Replace with the actual license you want to use.)

---

## Contact

If you have questions or want help integrating this into your environment, open an issue in this repo or contact the maintainer.

--
