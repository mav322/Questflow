-- QuestFlow Database Schema // Relational SDLC Governance & AI Repository Intelligence

CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sdlc_model TEXT NOT NULL,          -- Waterfall, Agile, V-Model, Spiral, Iterative
    tech_stack TEXT NOT NULL,          -- Python Web, MERN, Java Spring, DevOps Microservices
    folder_structure TEXT NOT NULL     -- JSON string of the folder/file structure
);

CREATE TABLE IF NOT EXISTS sdlc_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sdlc_model TEXT NOT NULL,          -- which model this rule belongs to
    phase_name TEXT NOT NULL,          -- Requirements, Design, Source, Testing, DevOps
    required_item TEXT NOT NULL,       -- e.g. docs/SRS.md, src/, Dockerfile
    weightage INTEGER NOT NULL         -- contribution to compliance score (0-100 sum)
);

CREATE TABLE IF NOT EXISTS quest_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER NOT NULL,
    quest_message TEXT NOT NULL,       -- human-readable "next task"
    step_order INTEGER NOT NULL,
    prerequisite_step_id INTEGER,      -- nullable, FK to quest_steps.id (DAG dependency)
    FOREIGN KEY (rule_id) REFERENCES sdlc_rules(id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_step_id) REFERENCES quest_steps(id) ON DELETE SET NULL
);

-- Audit History: Stores real repository audit runs, version evolution, and SDLC metrics
CREATE TABLE IF NOT EXISTS audit_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_name TEXT NOT NULL,
    version_tag TEXT DEFAULT 'v1.0',
    sdlc_model TEXT NOT NULL,
    compliance_score INTEGER NOT NULL,
    ai_quality_score INTEGER NOT NULL,
    composite_score INTEGER NOT NULL,
    total_files INTEGER NOT NULL,
    missing_count INTEGER NOT NULL,
    loc_count INTEGER DEFAULT 0,
    assertions_count INTEGER DEFAULT 0,
    phases_json TEXT DEFAULT '[]',
    sdlc_telemetry_json TEXT DEFAULT '{}',
    scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    summary_notes TEXT
);

-- Per-File Audit Intelligence: Records individual file ML predictions, authenticity and quality
CREATE TABLE IF NOT EXISTS audit_file_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    predicted_phase TEXT,
    ml_confidence REAL DEFAULT 0.0,
    authenticity_score REAL DEFAULT 0.0,
    is_matched_rule BOOLEAN DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (audit_id) REFERENCES audit_history(id) ON DELETE CASCADE
);

-- ML Model Benchmarks: Stores machine learning classification metrics and evaluation history
CREATE TABLE IF NOT EXISTS ml_benchmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    version TEXT NOT NULL,
    accuracy REAL NOT NULL,
    macro_f1 REAL NOT NULL,
    trained_samples_count INTEGER NOT NULL,
    trained_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metrics_json TEXT
);
