# QuestFlow // Epics, User Stories & Acceptance Criteria Matrix
**Document Version:** 2.1.0  
**SDLC Track:** Formal Requirements & Agile Acceptance Gating  
**Author:** WayPoint Engineering Team  

---

## 1.0 Epic Overview & Personas

### Personas:
- **Alex (Lead Engineer / Code Reviewer):** Needs deterministic SDLC compliance metrics and automated pull request verification gates before merging code.
- **Priya (Junior Developer / Student):** Needs clear, prerequisite-ordered quest guidance ("what deliverable to build next") without getting overwhelmed by chaotic repository structures.
- **Marcus (QA / DevOps Lead):** Needs AST-level structural integrity verification to detect empty stub files, zero-assertion unit tests, and missing containerization directives.

---

## 2.0 User Stories & Acceptance Criteria (Gherkin Syntax)

### US-101: Recursive Repository Ingestion & Subfolder Traversal
- **As a** developer uploading a complex mono-repo with separate frontend and backend directories,
- **I want** QuestFlow to recursively scan all subfolders and capture files at arbitrary folder depths,
- **So that** my repository architecture is evaluated accurately without demanding flattened root folders.

#### Acceptance Criteria:
- **Given** a directory containing nested subdirectories (e.g., `questflow-backend/`, `questflow-frontend/`, `tests/`),
- **When** the user drags and drops the parent directory or selects it via the file browser,
- **Then** the FileSystemEntry reader must traverse all directories recursively and register all non-ignored deliverables in memory.
- **And** `.git`, `node_modules`, and `__pycache__` directories must be automatically excluded.

---

### US-102: Deterministic SDLC Compliance Gate Calculation
- **As a** code auditor,
- **I want** repository deliverables to be evaluated against weighted SDLC rules,
- **So that** compliance is scored deterministically on a normalized 0–100% scale.

#### Acceptance Criteria:
- **Given** an active SDLC model configuration (Waterfall, Agile, V-Model, Spiral, Iterative),
- **When** the compliance engine evaluates the file inventory,
- **Then** earned weight must equal the sum of weights of all satisfied milestone rules.
- **And** the compliance score must equal `round((earned_weight / total_weight) * 100)`.

---

### US-103: Topological DAG Prerequisite Quest Guidance
- **As a** developer navigating a development lifecycle,
- **I want** the system to surface only the first unmet milestone whose prerequisites are fulfilled,
- **So that** development progresses logically and phase gates cannot be skipped prematurely.

#### Acceptance Criteria:
- **Given** an incomplete repository where Step 1 (Requirements) is unfulfilled,
- **When** the user requests the next quest task,
- **Then** the system must recommend Step 1 and prevent jumping forward to Step 3 (Source Code).
- **Given** Step 1 is verified as satisfied,
- **When** the user evaluates the repository again,
- **Then** Step 2 must be unlocked and presented as the active quest.

---

### US-104: AST-Powered Code Health & Stub Detection
- **As a** software quality lead,
- **I want** Python AST parsing and token analysis to count executable lines, functions, and unit test assertions,
- **So that** empty placeholder stubs (e.g., `def task(): pass`) or zero-assertion tests are penalized.

#### Acceptance Criteria:
- **Given** a source file containing empty functions with only `pass` statements,
- **When** the AST parser processes the syntax tree,
- **Then** `stubs` count must increment and the authenticity score must flag the file as `STUB / DUMMY`.
- **Given** a test suite containing automated assertion statements (`assert`, `assertEqual`),
- **When** the AST parser processes the code,
- **Then** `test_assertions` count must reflect the true assertion volume and boost quality metrics.

---

### US-105: Multi-Stage Containerization & CI/CD Pipeline
- **As a** DevOps engineer,
- **I want** production Dockerfiles and GitHub Actions workflows,
- **So that** QuestFlow can be containerized, tested, and audited continuously upon every git commit.

#### Acceptance Criteria:
- **Given** the repository root or DevOps folder,
- **When** inspected by the DevOps compliance gate,
- **Then** standard containerization files (`Dockerfile`, `docker-compose.yml`) and CI workflows (`.github/workflows/ci.yml`) must be validated.
