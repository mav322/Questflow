# Software Requirements Specification (SRS)
## Project: QuestFlow // AI & SDLC Governance Platform
**Document Identifier:** IEEE-830-QUESTFLOW-v2.1  
**Version:** 2.1.0  
**Status:** Approved / Production Baseline  

---

## 1.0 Introduction & System Purpose

### 1.1 Purpose
The purpose of this Software Requirements Specification (SRS) document is to formalize the architectural, functional, and non-functional requirements for the QuestFlow SDLC Governance and Repository Intelligence Platform. QuestFlow is designed to replace informal, subjective code evaluations with automated, deterministic compliance auditing against rigorous software engineering standards.

### 1.2 Scope
QuestFlow provides an intelligent web console and microservice backend that ingests repository trees, executes Abstract Syntax Tree (AST) structural parsing, classifies deliverables using supervised TF-IDF + Multinomial Naive Bayes machine learning, computes phase-gated compliance scores (0–100%), and guides developers through topologically ordered prerequisite quest milestones (Directed Acyclic Graph).

### 1.3 Definitions, Acronyms, and Abbreviations
- **SDLC:** Software Development Life Cycle (Waterfall, Agile, V-Model, Spiral, Iterative).
- **AST:** Abstract Syntax Tree.
- **DAG:** Directed Acyclic Graph (prerequisite dependency network).
- **LOC:** Lines of Code (excluding whitespace and comment lines).
- **SRS:** Software Requirements Specification (IEEE 830 standard).
- **DDL:** Data Definition Language (SQL schema creation statements).

---

## 2.0 Overall Description

### 2.1 Product Perspective & Microservice Topology
QuestFlow is architected as a high-performance decoupled system:
1. **Presentation Layer:** Vanilla WebGL2 radar canvas, dynamic HUD telemetry gauges, and drag-and-drop ingestion cockpit.
2. **Reverse Proxy & Edge Server:** Node.js server running on port 3000, serving static assets and proxying requests.
3. **Intelligence & Analysis Engine:** Python 3.12 Flask REST microservice on port 5000 running Scikit-Learn pipelines and AST parsers.
4. **Relational Data Store:** SQLite 3 database (`questflow.db`) enforcing referential integrity for templates, rules, and audit runs.

### 2.2 User Characteristics
- **Software Engineers:** Upload local repositories or `.zip` archives to verify milestone completion.
- **Engineering Managers / Auditors:** Review compliance ledgers, code health metrics, and audit history.

---

## 3.0 Specific Functional Requirements

### 3.1 Module 1: Repository Ingestion & Recursive Directory Traversal
- **FR-101 (Subfolder Recursion):** The ingestion engine shall recursively traverse directory trees of arbitrary depth using the HTML5 `FileSystemEntry` API.
- **FR-102 (Artifact Sanitization):** The scanner shall automatically ignore extraneous directories (`node_modules`, `.git`, `__pycache__`, `.DS_Store`).
- **FR-103 (Archive Extraction):** The backend shall accept `.zip` archives via multipart/form-data, extract contents in-memory using `io.BytesIO`, and normalize paths.

### 3.2 Module 2: Deterministic SDLC Compliance Engine
- **FR-201 (Multi-SDLC Support):** The rule engine shall maintain rule definitions across 5 paradigms: Waterfall (Python Web), Agile (MERN), V-Model (Critical Systems), Spiral (R&D Prototype), and Iterative (Java Spring).
- **FR-202 (Smart Subfolder Matching):** Deliverables shall be validated via deep subfolder search and semantic aliasing, allowing source files in `questflow-backend/` or `questflow-frontend/` to satisfy implementation requirements.
- **FR-203 (Normalized Scoring):** Compliance score shall be calculated as `round((earned_weight / total_weight) * 100)`.

### 3.3 Module 3: Topological Prerequisite DAG Quests
- **FR-301 (Linear & Branching DAG):** Quest milestones shall maintain strict prerequisite chains (`prerequisite_step_id`), preventing developers from skipping design or specification phases.
- **FR-302 (Reactive Dispatch):** The active quest shall automatically advance to the next unmet milestone once prerequisites are satisfied.

### 3.4 Module 4: AST Syntax Analysis & AI Authenticity
- **FR-401 (AST Parsing):** The parser shall examine code syntax to count executable LOC, function declarations, class abstractions, and automated test assertions.
- **FR-402 (Stub / Dummy Penalty):** Files containing minimal placeholder content (< 10 words or bare `pass` statements) shall be flagged as `STUB / DUMMY` with low authenticity.
- **FR-403 (ML Phase Classification):** The TF-IDF + Naive Bayes pipeline shall classify deliverables into Requirements, Design, Source, Testing, or DevOps.

---

## 4.0 Non-Functional Requirements

### 4.1 Performance & Latency
- **NFR-101:** Repository ingestion and compliance calculation for repositories up to 500 files shall complete within 350 milliseconds.
- **NFR-102:** The WebGL radar scanner canvas shall maintain 60 FPS rendering under standard hardware.

### 4.2 Security & Data Privacy
- **NFR-201:** Repository files uploaded for audit shall be evaluated in-memory and persisted only as anonymized audit telemetry.
- **NFR-202:** SQL injection prevention via parameterized prepared statements across all SQLite queries.

### 4.3 Maintainability & Portability
- **NFR-301:** The backend shall provide containerized deployments via multi-stage Dockerfiles.
- **NFR-302:** The system shall support automated verification via comprehensive `unittest` test suites.
