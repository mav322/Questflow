# QuestFlow // SDLC Governance & AI Repository Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-20.x-green.svg?logo=node.js&logoColor=white)](https://nodejs.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-TF--IDF%20%2B%20MultinomialNB-orange.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()

> **Transform chaotic codebases into verified engineering achievements.**  
> QuestFlow audits repository structures against formal software engineering models, scores compliance deterministically (0–100%), performs AST syntax health analysis, and dispatches prerequisite-chained developer quests using topological DAG traversal.

---

## ⚡ Key Architectural Capabilities

- **📁 Recursive Ingestion & Multi-Depth Traversal:** Drag-and-drop or upload repositories with complex subfolder hierarchies (`questflow-backend/`, `questflow-frontend/`, `tests/`) without demanding artificial flat structures.
- **🧠 AI Artifact Quality & Authenticity Scoring:** Uses Scikit-Learn TF-IDF vectorization and Multinomial Naive Bayes to classify deliverables into formal lifecycle phases (*Requirements, Design, Source, Testing, DevOps*).
- **🛡️ AST-Level Code Health Parser:** Analyzes Python and JavaScript ASTs to measure executable lines of code (LOC), functions, classes, and automated assertions while penalizing empty stub/placeholder functions (`pass`).
- **🔗 Topological DAG Prerequisite Quest Engine:** Prevents developers from skipping design or specification phases. Unlocks milestones sequentially based on verified dependency graphs.
- **📊 Multi-SDLC Paradigm Engine:** Out-of-the-box support for **Waterfall** (Python Web), **Agile / Scrum** (MERN Stack), **V-Model** (Critical Systems), **Spiral** (R&D Prototype), and **Iterative** (Enterprise Java Spring).
- **⚡ Technical Radar Cockpit:** Interactive WebGL2 canvas background with live radial telemetry gauges and real-time compliance score counter.

---

## 🏗️ System Architecture

```text
[ Developer Browser / Client Cockpit ]
           │
           │ HTTP / WebGL2 UI (Port 3000)
           ▼
[ Node.js Reverse Proxy & Asset Server ]
           │
           │ Proxy /api/* (Port 5000)
           ▼
[ Flask Intelligence Microservice ]
   ├── AST Structural Syntax Engine (LOC, Classes, Assertions, Stubs)
   ├── TF-IDF + Naive Bayes Classifier (Benchmark Acc: 92.3% | F1: 91.8%)
   ├── SDLC Compliance Evaluator (Deterministic 0-100% Gating)
   └── Topological DAG Prerequisite Resolver
           │
           ▼
[ SQLite Persistence Engine (`questflow.db`) ]
   ├── `sdlc_rules` (Rule Catalog & Weights)
   ├── `quest_steps` (Chained Prerequisite Quests)
   └── `audit_history` (Audit Run Telemetry & Per-File Logs)
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.12+**
- **Node.js 18+** / **npm 9+**

### 1. Quick Launch (Windows)
Double-click `start.bat` in the repository root, or run:
```cmd
start.bat
```
This automatically boots the Flask ML service on port 5000, starts the Node server on port 3000, and opens `http://localhost:3000` in your default browser.

### 2. Manual Setup

**Backend (Flask):**
```bash
cd questflow-backend
pip install -r requirements.txt
python models/init_db.py  # Seed schema and all 5 SDLC models
python app.py
```

**Frontend (Node.js):**
```bash
cd questflow-frontend
npm install
node server.js
```
Open **`http://localhost:3000`**.

### 3. Docker Deployment
```bash
docker compose up --build
```

---

## 🧪 Automated Testing

Execute the automated test suite verifying compliance calculations, AST parsing, and API endpoints:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📋 Repository Deliverables Checklist

- [x] **Requirements:** `docs/SRS.md` (IEEE 830 Specification) & `docs/user_stories.md`
- [x] **Design:** `docs/architecture.png` & `questflow-backend/models/schema.sql`
- [x] **Source Code:** Full Flask microservice & vanilla JS/WebGL2 cockpit
- [x] **Testing:** Automated `unittest` test suites & `docs/test_matrix.md`
- [x] **DevOps:** Multi-stage `Dockerfile`, `docker-compose.yml`, and GitHub Actions CI workflow

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
