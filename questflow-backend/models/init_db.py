"""
Initializes questflow.db and seeds all 5 SDLC models end-to-end:
Waterfall, Agile, V-Model, Spiral, Iterative.
Also creates audit_history, audit_file_details, and ml_benchmarks tables.
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "questflow.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


_migrated = False


def get_connection():
    global _migrated
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Auto-initialize schema & seed models on fresh environments (CI/CD, Docker, clean checkout)
    try:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        if 'templates' not in tables or 'sdlc_rules' not in tables:
            with open(SCHEMA_PATH) as f:
                conn.executescript(f.read())
            conn.commit()
            cur = conn.cursor()
            _seed_all_models_cur(cur)
            conn.commit()
    except Exception:
        pass

    if not _migrated:
        try:
            cols = {row["name"] for row in conn.execute("PRAGMA table_info(audit_history)").fetchall()}
            if cols:
                migrations = [
                    ("version_tag", "TEXT DEFAULT 'v1.0'"),
                    ("loc_count", "INTEGER DEFAULT 0"),
                    ("assertions_count", "INTEGER DEFAULT 0"),
                    ("phases_json", "TEXT DEFAULT '[]'"),
                    ("sdlc_telemetry_json", "TEXT DEFAULT '{}'"),
                ]
                for col_name, col_def in migrations:
                    if col_name not in cols:
                        conn.execute(f"ALTER TABLE audit_history ADD COLUMN {col_name} {col_def}")
                conn.commit()
                _migrated = True
        except Exception:
            pass
    return conn


def init_schema():
    conn = get_connection()
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database schema successfully initialized.")


def seed_model(cur, sdlc_model, tech_stack, folder_structure, rules_and_quests):
    """
    seeds a single SDLC model with its template, rules, and chained quest steps.
    rules_and_quests is a list of tuples:
    (phase_name, required_item, weightage, quest_message)
    """
    cur.execute("SELECT COUNT(*) FROM templates WHERE sdlc_model = ?", (sdlc_model,))
    if cur.fetchone()[0] > 0:
        print(f"Model '{sdlc_model}' already exists in templates, updating rules & steps...")
        # Clean existing rules and quest steps to allow fresh seed
        cur.execute("SELECT id FROM sdlc_rules WHERE sdlc_model = ?", (sdlc_model,))
        rule_ids = [row[0] for row in cur.fetchall()]
        if rule_ids:
            cur.execute(f"DELETE FROM quest_steps WHERE rule_id IN ({','.join(['?']*len(rule_ids))})", rule_ids)
            cur.execute("DELETE FROM sdlc_rules WHERE sdlc_model = ?", (sdlc_model,))
        cur.execute("DELETE FROM templates WHERE sdlc_model = ?", (sdlc_model,))

    # Insert template
    cur.execute(
        "INSERT INTO templates (sdlc_model, tech_stack, folder_structure) VALUES (?, ?, ?)",
        (sdlc_model, tech_stack, json.dumps(folder_structure)),
    )

    prev_step_id = None
    for step_order, (phase, item, weight, message) in enumerate(rules_and_quests, start=1):
        cur.execute(
            "INSERT INTO sdlc_rules (sdlc_model, phase_name, required_item, weightage) VALUES (?, ?, ?, ?)",
            (sdlc_model, phase, item, weight),
        )
        rule_id = cur.lastrowid

        cur.execute(
            "INSERT INTO quest_steps (rule_id, quest_message, step_order, prerequisite_step_id) VALUES (?, ?, ?, ?)",
            (rule_id, message, step_order, prev_step_id),
        )
        prev_step_id = cur.lastrowid

    print(f"Model '{sdlc_model}' seeded with {len(rules_and_quests)} rules and sequential quests.")


def _seed_all_models_cur(cur):
    # 1. WATERFALL (Python Web)
    waterfall_structure = {
        "1_Requirements": ["SRS.md", "user_stories.md"],
        "2_Design": ["architecture.png", "schema.sql"],
        "3_Source": ["app.py", "routes/", "models/"],
        "4_Testing": ["unit_tests/", "test_matrix.md"],
        "5_DevOps": ["Dockerfile", ".github/workflows/"],
        "README.md": None,
        ".gitignore": None,
    }
    waterfall_items = [
        ("Requirements", "1_Requirements/SRS.md", 20, "Draft your formal Software Requirements Specification in 1_Requirements/SRS.md"),
        ("Requirements", "1_Requirements/user_stories.md", 10, "Define acceptance criteria and user stories in 1_Requirements/user_stories.md"),
        ("Design", "2_Design/architecture.png", 15, "Generate your high-level system architecture blueprint in 2_Design/architecture.png"),
        ("Design", "2_Design/schema.sql", 10, "Establish relational database DDL tables in 2_Design/schema.sql"),
        ("Source", "3_Source/", 15, "Begin production application development under 3_Source/"),
        ("Testing", "4_Testing/unit_tests/", 15, "Write automated regression & unit test suites in 4_Testing/unit_tests/"),
        ("Testing", "4_Testing/test_matrix.md", 5, "Document edge cases & pass/fail coverage criteria in 4_Testing/test_matrix.md"),
        ("DevOps", "5_DevOps/Dockerfile", 5, "Containerize application environment using 5_DevOps/Dockerfile"),
        ("DevOps", "5_DevOps/.github/workflows/", 5, "Configure continuous integration pipelines in 5_DevOps/.github/workflows/"),
    ]
    seed_model(cur, "Waterfall", "Python Web", waterfall_structure, waterfall_items)

    # 2. AGILE / SCRUM (MERN Stack)
    agile_structure = {
        "docs": ["backlog.md", "sprint_board.json", "wireframes/", "api_contract.json"],
        "src": ["components/", "api/", "utils/"],
        "tests": ["unit/", "integration/"],
        "Dockerfile": None,
        "docker-compose.yml": None,
        "package.json": None,
        "README.md": None,
    }
    agile_items = [
        ("Backlog", "docs/backlog.md", 15, "Formulate product backlog epics & prioritized user stories in docs/backlog.md"),
        ("Backlog", "docs/sprint_board.json", 10, "Configure initial sprint board & work-in-progress limits in docs/sprint_board.json"),
        ("Design", "docs/wireframes/", 10, "Design UI wireframes & user journey mockups under docs/wireframes/"),
        ("Design", "docs/api_contract.json", 10, "Establish REST/GraphQL schema contracts in docs/api_contract.json"),
        ("Source", "src/components/", 20, "Develop interactive UI components in src/components/"),
        ("Source", "src/api/", 15, "Implement backend endpoints & service handlers in src/api/"),
        ("Testing", "tests/unit/", 10, "Write automated component unit tests under tests/unit/"),
        ("Testing", "tests/integration/", 10, "Validate end-to-end integration flows under tests/integration/"),
        ("DevOps", "Dockerfile", 5, "Standardize multi-stage container build in Dockerfile"),
        ("DevOps", "docker-compose.yml", 5, "Orchestrate multi-container stack in docker-compose.yml"),
    ]
    seed_model(cur, "Agile", "MERN Stack", agile_structure, agile_items)

    # 3. V-MODEL (High-Assurance / Critical Systems)
    vmodel_structure = {
        "1_Requirements": ["SRS.md"],
        "2_Design": ["system_design.md"],
        "3_Source": ["main.py", "core/"],
        "4_Validation": ["acceptance_test_plan.md", "integration_tests/", "unit_tests/"],
        "ci_pipeline.yml": None,
        "README.md": None,
    }
    vmodel_items = [
        ("Requirements", "1_Requirements/SRS.md", 15, "Formalize IEEE 830 functional specifications in 1_Requirements/SRS.md"),
        ("Validation", "4_Validation/acceptance_test_plan.md", 15, "Directly pair SRS with user acceptance test plan in 4_Validation/acceptance_test_plan.md"),
        ("Design", "2_Design/system_design.md", 15, "Specify subsystem interfaces & communication protocols in 2_Design/system_design.md"),
        ("Validation", "4_Validation/integration_tests/", 15, "Pair system design with interface verification in 4_Validation/integration_tests/"),
        ("Source", "3_Source/", 20, "Implement concrete algorithmic software units in 3_Source/"),
        ("Validation", "4_Validation/unit_tests/", 20, "Ensure 100% statement and branch coverage in 4_Validation/unit_tests/"),
    ]
    seed_model(cur, "V-Model", "Critical Systems", vmodel_structure, vmodel_items)

    # 4. SPIRAL (Risk-Driven / Prototype R&D)
    spiral_structure = {
        "1_Objectives": ["mission_statement.md", "risk_log.md"],
        "2_Prototype": ["spike_evaluation.md", "poc_source/"],
        "3_Engineering": ["production_src/", "test_bench/"],
        "4_Evaluation": ["stakeholder_signoff.md"],
        "README.md": None,
    }
    spiral_items = [
        ("Objectives", "1_Objectives/mission_statement.md", 10, "Define core objectives & operational constraints in 1_Objectives/mission_statement.md"),
        ("Objectives", "1_Objectives/risk_log.md", 15, "Quantify technical & architectural risk vectors in 1_Objectives/risk_log.md"),
        ("Prototype", "2_Prototype/spike_evaluation.md", 15, "Document technology spike benchmarks in 2_Prototype/spike_evaluation.md"),
        ("Prototype", "2_Prototype/poc_source/", 20, "Build minimum viable prototype proof-of-concept under 2_Prototype/poc_source/"),
        ("Engineering", "3_Engineering/production_src/", 20, "Scale prototype into hardened production code under 3_Engineering/production_src/"),
        ("Engineering", "3_Engineering/test_bench/", 10, "Run stress & performance test suites in 3_Engineering/test_bench/"),
        ("Evaluation", "4_Evaluation/stakeholder_signoff.md", 10, "Formalize spiral review & signoff for next iteration in 4_Evaluation/stakeholder_signoff.md"),
    ]
    seed_model(cur, "Spiral", "R&D Prototype", spiral_structure, spiral_items)

    # 5. ITERATIVE (Enterprise Java Spring / Modular Growth)
    iterative_structure = {
        "1_Inception": ["charter.md", "minimal_viable_spec.md"],
        "2_Elaboration": ["domain_model.png", "api_spec.yaml"],
        "3_Construction": ["src/", "tests/"],
        "4_Transition": ["performance_audit.md"],
        "pom.xml": None,
        "README.md": None,
    }
    iterative_items = [
        ("Inception", "1_Inception/charter.md", 10, "Document project business case and scope in 1_Inception/charter.md"),
        ("Inception", "1_Inception/minimal_viable_spec.md", 15, "Draft minimal baseline specification in 1_Inception/minimal_viable_spec.md"),
        ("Elaboration", "2_Elaboration/domain_model.png", 10, "Model architectural domain entities in 2_Elaboration/domain_model.png"),
        ("Elaboration", "2_Elaboration/api_spec.yaml", 15, "Define OpenAPI service contracts in 2_Elaboration/api_spec.yaml"),
        ("Construction", "3_Construction/src/", 25, "Implement module features iteratively in 3_Construction/src/"),
        ("Construction", "3_Construction/tests/", 15, "Maintain regression test suites in 3_Construction/tests/"),
        ("Transition", "4_Transition/performance_audit.md", 10, "Execute release performance benchmarks in 4_Transition/performance_audit.md"),
    ]
    seed_model(cur, "Iterative", "Java Spring", iterative_structure, iterative_items)


def seed_all_models():
    conn = get_connection()
    cur = conn.cursor()
    _seed_all_models_cur(cur)
    conn.commit()
    conn.close()
    print("All 5 SDLC Models successfully seeded into QuestFlow database!")


if __name__ == "__main__":
    init_schema()
    seed_all_models()
