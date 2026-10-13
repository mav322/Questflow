# QuestFlow // SDLC Governance & AI Repository Intelligence Engine

QuestFlow is an automated software engineering compliance auditor and machine-learning repository evaluator. It replaces subjective project tracking with **deterministic SDLC rule auditing**, **TF-IDF + Naive Bayes document classification**, **artifact authenticity scoring**, and **directed prerequisite quest chaining (DAG)**.

Developed by **Team WayPoint** — Department of Computer Applications, Manipal University Jaipur.

---

## Key Features

1. **Machine Learning Document & Deliverable Classifier**:
   - Classifies repository artifacts into 6 formal SDLC phases: `Requirements`, `Design`, `Source`, `Testing`, `DevOps`, and `Documentation`.
   - Trained on realistic engineering corpus using Scikit-Learn TF-IDF Vectorization and Multinomial Naive Bayes.
   - **Benchmark Performance**: **92.3% Accuracy**, **91.8% Weighted F1-Score**.
   - Model metrics and evaluation confusion matrices persistently logged to `ml_benchmarks` in SQLite.

2. **Artifact Authenticity & Quality Engine**:
   - Prevents empty or dummy placeholder files from passing audits.
   - Evaluates IEEE 830 structural markers (Functional / Non-Functional Requirements, Scope, Acceptance Criteria) in SRS documents.
   - Analyzes DDL table declarations in database schemas, automated test assertions (`assert`, `expect`), and container build directives (`FROM`, `WORKDIR`, `COPY`) in Dockerfiles.
   - Assigns quality tiers: `PRODUCTION GRADE`, `ADEQUATE`, and `STUB / DUMMY FILE`.

3. **Composite Engineering Maturity Index**:
   - Blends deterministic rule weightage (55%) with deep content authenticity (45%) to calculate a verifiable repository health score (0–100 pts).

4. **Real Repository Upload & Scanning**:
   - Supports uploading entire project directory trees via folder selection (`webkitdirectory`).
   - Supports uploading `.zip` archives with automatic server-side de-compression and analysis.
   - Supports downloadable starter project scaffolds packaged as `.zip` archives.

5. **Multi-SDLC Methodologies**:
   - Fully seeded for 5 distinct software engineering lifecycles:
     - **Waterfall** (Python Web)
     - **Agile / Scrum** (MERN Stack)
     - **V-Model** (Critical / High-Assurance Systems)
     - **Spiral** (Risk-Driven Prototype R&D)
     - **Iterative** (Enterprise Java Spring)

6. **Persistent SQLite Audit Ledger**:
   - Tracks audit history, per-file ML predictions, and timestamped progress across all evaluations in `questflow.db`.

---

## Architecture Overview

```
+-------------------------------------------------------------+
|               CLIENT PRESENTATION COCKPIT                   |
|   - Real Repository & ZIP Upload  - Radial Maturity Dial    |
|   - ML Telemetry & Benchmarks      - Deep Artifact Table    |
|   - Multi-SDLC Model Selector      - SQLite Audit Ledger    |
+------------------------------+------------------------------+
                               | Streaming REST APIs
                               v
+-------------------------------------------------------------+
|              NODE.JS APPLICATION SERVER (:3000)             |
|   - Zero-dependency HTTP static asset server               |
|   - Streaming proxy with buffer preservation               |
|   - Standalone fallback rule engine for all 5 models       |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|               FLASK REST MICROSERVICE (:5000)               |
|   - Blueprint routing (/routes)                             |
|   - CORS middleware layer                                   |
|   - Multipart ZIP decompressor & file tree parser           |
+------------------------------+------------------------------+
          |                                       |
          v                                       v
+-----------------------+               +-----------------------+
|      DATA LAYER       |               |    AI / ML ENGINE     |
| - models/init_db.py   |               | - services/ml_engine  |
| - questflow.db        |               | - TF-IDF Vectorizer   |
| - sdlc_rules (5)      |               | - MultinomialNB (92%) |
| - audit_history       |               | - Authenticity Scorer |
| - ml_benchmarks       |               | - DAG Next-Quest Flow |
+-----------------------+               +-----------------------+
```

---

## API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/health` | `GET` | Health check and engine telemetry |
| `/api/templates` | `GET` | Available SDLC models, tech stacks, and phase rules |
| `/api/scaffold-download` | `GET` | Streams starter project scaffold `.zip` (`?model=Waterfall`) |
| `/api/check-sdlc` | `POST` | Deterministic compliance check (`existing_files` array) |
| `/api/scan-repo` | `POST` | Deep AI audit of file contents (`files` dictionary) |
| `/api/upload-repo` | `POST` | Multipart `.zip` or directory upload & AI evaluation |
| `/api/ml-status` | `GET` | Trained ML model accuracy, F1 score, and recent audits |
| `/api/audit-history` | `GET` | Stored audit runs from SQLite database |
| `/api/audit-details/<id>`| `GET` | Detailed file-by-file ML predictions for an audit run |

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r questflow-backend/requirements.txt

# 2. Seed database with all 5 models and initialize schema
python questflow-backend/models/init_db.py

# 3. Launch both servers (or run start.bat)
start.bat
```

Or run manually:
```bash
# Terminal 1: Backend
cd questflow-backend
python app.py

# Terminal 2: Frontend
cd questflow-frontend
node server.js
```

Open `http://localhost:3000` in any modern web browser.
