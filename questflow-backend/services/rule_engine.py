"""
Rule engine: compliance scoring, DAG prerequisite quest ordering,
model-specific SDLC methodology governance, and multi-version lifecycle analysis.
"""
import json
import os
import re
from models.init_db import get_connection


def get_rules_for_model(sdlc_model):
    conn = get_connection()
    rules = conn.execute(
        "SELECT * FROM sdlc_rules WHERE LOWER(sdlc_model) = LOWER(?) ORDER BY id ASC", (sdlc_model,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rules]


def _normalize_path(p):
    return p.replace('\\', '/').strip('/')


def _strip_root_wrapper(norm_path):
    """Strips a top-level wrapper folder (e.g. 'questflow-master/docs/SRS.md' -> 'docs/SRS.md') if not a standard phase dir."""
    parts = norm_path.split('/')
    if len(parts) > 1 and not parts[0].lower().startswith(('1_', '2_', '3_', '4_', '5_', 'src', 'docs', 'tests', '.github')):
        return '/'.join(parts[1:])
    return norm_path


def is_item_present(required_item, existing_set, existing_files_list, files_dict=None, phase_name=None):
    """
    Checks if a required rule deliverable is satisfied by the repository files.
    Supports deep subfolder scanning while preserving strict semantic identity per SDLC model
    so that different SDLC models evaluate their unique methodology artifacts accurately.
    """
    clean_req = _normalize_path(required_item)
    req_lower = clean_req.lower()
    base_req = os.path.basename(req_lower)

    # 1. Exact direct matches in set
    if required_item in existing_set or clean_req in existing_set or req_lower in existing_set:
        return True

    norm_files = [_normalize_path(f) for f in existing_files_list if _normalize_path(f)]

    # 2. Exact path or suffix match across subfolders
    for f in norm_files:
        f_lower = f.lower()
        stripped = _strip_root_wrapper(f_lower)
        if f_lower == req_lower or f_lower.endswith('/' + req_lower):
            return True
        if stripped == req_lower or stripped.endswith('/' + req_lower):
            return True

    # 3. Explicit directory rule match (e.g. '3_Source/', '4_Testing/unit_tests/', 'docs/wireframes/')
    if required_item.endswith('/'):
        folder_token = req_lower + '/'
        for f in norm_files:
            f_lower = f.lower()
            stripped = _strip_root_wrapper(f_lower)
            if (
                f_lower == req_lower
                or f_lower.startswith(folder_token)
                or f'/{folder_token}' in f_lower
                or stripped.startswith(folder_token)
                or f'/{folder_token}' in stripped
            ):
                return True

    # =========================================================================
    # 4. Deliverable-Specific Subfolder Matching (No False Cross-Model Bleed)
    # =========================================================================

    # --- WATERFALL & V-MODEL: Formal SRS (1_Requirements/SRS.md) ---
    if base_req == 'srs.md':
        for f in norm_files:
            base = os.path.basename(f.lower())
            if base in ('srs.md', 'srs.txt', 'srs.docx', 'srs.pdf', 'specification.md', 'software_requirements.md') or 'project_report' in base:
                return True
        return False

    # --- WATERFALL: User Stories (1_Requirements/user_stories.md) ---
    if base_req == 'user_stories.md':
        for f in norm_files:
            base = os.path.basename(f.lower())
            if base in ('user_stories.md', 'user_stories.txt', 'user_stories.json', 'stories.md'):
                return True
        return False

    # --- AGILE: Product Backlog (docs/backlog.md) ---
    if base_req == 'backlog.md':
        for f in norm_files:
            base = os.path.basename(f.lower())
            if base in ('backlog.md', 'product_backlog.md', 'backlog.json', 'sprint_backlog.md'):
                return True
        return False

    # --- AGILE: Sprint Board (docs/sprint_board.json) ---
    if base_req == 'sprint_board.json':
        for f in norm_files:
            base = os.path.basename(f.lower())
            if base in ('sprint_board.json', 'sprint_board.md', 'sprint.json', 'kanban_board.json'):
                return True
        return False

    # --- AGILE: UI Wireframes (docs/wireframes/) ---
    if 'wireframes' in req_lower:
        for f in norm_files:
            f_lower = f.lower()
            base = os.path.basename(f_lower)
            if 'wireframe' in f_lower or 'mockup' in base or 'figma' in base:
                return True
        return False

    # --- AGILE: API Contract (docs/api_contract.json) ---
    if base_req == 'api_contract.json':
        for f in norm_files:
            base = os.path.basename(f.lower())
            if base in ('api_contract.json', 'api_contract.yaml', 'swagger.json', 'openapi.json', 'postman_collection.json'):
                return True
        return False

    # --- WATERFALL: System Architecture Diagram (2_Design/architecture.png) ---
    if base_req == 'architecture.png':
        for f in norm_files:
            base = os.path.basename(f.lower())
            if any(base.startswith(prefix) for prefix in ('architecture.', 'system_architecture.', 'architecture_diagram.', 'arch_diagram.')):
                return True
        return False

    # --- WATERFALL: Relational Database Schema (2_Design/schema.sql) ---
    if base_req == 'schema.sql':
        for f in norm_files:
            f_lower = f.lower()
            base = os.path.basename(f_lower)
            if base == 'schema.sql' or (f_lower.endswith('.sql') and any(k in base for k in ('schema', 'init', 'tables', 'migration', 'db'))):
                return True
            if base in ('schema.prisma', 'models.py'):
                return True
        if files_dict:
            for f, content in files_dict.items():
                if f.lower().endswith('.sql') and 'create table' in (content or '').lower():
                    return True
        return False

    # --- V-MODEL: System Design Document (2_Design/system_design.md) ---
    if base_req == 'system_design.md':
        for f in norm_files:
            base = os.path.basename(f.lower())
            if base in ('system_design.md', 'sds.md', 'high_level_design.md', 'low_level_design.md', 'architecture_design.md'):
                return True
        return False

    # --- V-MODEL: Acceptance Test Plan (4_Validation/acceptance_test_plan.md) ---
    if base_req == 'acceptance_test_plan.md':
        for f in norm_files:
            base = os.path.basename(f.lower())
            if base in ('acceptance_test_plan.md', 'uat_plan.md', 'acceptance_tests.md', 'validation_plan.md'):
                return True
        return False

    # --- WATERFALL: Test Matrix (4_Testing/test_matrix.md) ---
    if base_req == 'test_matrix.md':
        for f in norm_files:
            base = os.path.basename(f.lower())
            if base in ('test_matrix.md', 'qa_matrix.md', 'test_report.md', 'test_cases.md'):
                return True
        return False

    # --- SPIRAL: Objectives & Risk Artifacts ---
    if base_req == 'mission_statement.md':
        return any(os.path.basename(f.lower()) in ('mission_statement.md', 'objectives.md', 'system_objectives.md') for f in norm_files)

    if base_req == 'risk_log.md':
        return any(os.path.basename(f.lower()) in ('risk_log.md', 'risk_register.md', 'risk_matrix.md', 'risk_analysis.md') for f in norm_files)

    if base_req == 'spike_evaluation.md':
        return any(os.path.basename(f.lower()) in ('spike_evaluation.md', 'spike_benchmark.md', 'prototype_eval.md') for f in norm_files)

    if 'poc_source' in req_lower:
        return any('poc_source/' in f.lower() or 'prototype/' in f.lower() or 'poc/' in f.lower() for f in norm_files)

    if base_req == 'stakeholder_signoff.md':
        return any(os.path.basename(f.lower()) in ('stakeholder_signoff.md', 'signoff.md', 'iteration_review.md') for f in norm_files)

    # --- ITERATIVE (RUP): Inception, Elaboration & Transition Artifacts ---
    if base_req == 'charter.md':
        return any(os.path.basename(f.lower()) in ('charter.md', 'project_charter.md', 'vision.md') for f in norm_files)

    if base_req == 'minimal_viable_spec.md':
        return any(os.path.basename(f.lower()) in ('minimal_viable_spec.md', 'mvp_spec.md', 'baseline_spec.md') for f in norm_files)

    if base_req == 'domain_model.png':
        return any(os.path.basename(f.lower()).startswith(('domain_model.', 'class_diagram.', 'er_diagram.')) for f in norm_files)

    if base_req == 'api_spec.yaml':
        return any(os.path.basename(f.lower()) in ('api_spec.yaml', 'api_spec.yml', 'openapi.yaml', 'openapi.yml', 'swagger.yaml') for f in norm_files)

    if base_req == 'performance_audit.md':
        return any(os.path.basename(f.lower()) in ('performance_audit.md', 'benchmark_report.md', 'load_test_report.md') for f in norm_files)

    # --- SOURCE CODE DIRECTORIES (Subfolder-Aware) ---
    if any(k in req_lower for k in ('3_source', 'src/components', 'src/api', 'production_src', '3_construction/src')):
        if 'components' in req_lower:
            for f in norm_files:
                f_lower = f.lower()
                if any(k in f_lower for k in ('components/', 'frontend/', 'views/', 'pages/')) and f_lower.endswith(('.js', '.jsx', '.ts', '.tsx', '.vue', '.html', '.css')):
                    return True
            return False
        elif 'api' in req_lower:
            for f in norm_files:
                f_lower = f.lower()
                if any(k in f_lower for k in ('api/', 'routes/', 'controllers/', 'backend/', 'services/')) and f_lower.endswith(('.py', '.js', '.ts', '.java', '.go')):
                    return True
            return False
        else:
            source_exts = ('.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rb', '.rs', '.cpp', '.c', '.cs')
            for f in norm_files:
                f_lower = f.lower()
                base = os.path.basename(f_lower)
                if any(ign in f_lower for ign in ('node_modules/', '/.git/', '__pycache__/')):
                    continue
                if f_lower.endswith(source_exts) and not any(t in base for t in ('test_', '_test', '.test.', '.spec.', 'generate_report')):
                    return True
            return False

    # --- TESTING SUITES (Distinguishing Unit vs Integration Tests) ---
    if any(k in req_lower for k in ('unit_tests', 'tests/unit', '3_construction/tests', 'test_bench')):
        for f in norm_files:
            f_lower = f.lower()
            base = os.path.basename(f_lower)
            if any(k in f_lower for k in ('unit_tests/', 'tests/unit/', 'test_bench/')):
                return True
            if any(t in base for t in ('test_rule', 'test_ml', 'test_unit', '.test.', '.spec.')) or (base.startswith('test_') and 'api' not in base and 'integration' not in base):
                return True
        return False

    if any(k in req_lower for k in ('integration_tests', 'tests/integration')):
        for f in norm_files:
            f_lower = f.lower()
            base = os.path.basename(f_lower)
            if any(k in f_lower for k in ('integration_tests/', 'tests/integration/')):
                return True
            if any(t in base for t in ('test_api', 'test_integration', 'integration_test', 'e2e')):
                return True
        return False

    # --- DEVOPS & CI/CD ---
    if base_req == 'dockerfile':
        return any(os.path.basename(f.lower()) in ('dockerfile', 'containerfile') or os.path.basename(f.lower()).startswith('dockerfile.') for f in norm_files)

    if base_req == 'docker-compose.yml':
        return any(os.path.basename(f.lower()) in ('docker-compose.yml', 'docker-compose.yaml', 'compose.yml', 'compose.yaml') for f in norm_files)

    if 'workflows' in req_lower or 'ci_pipeline' in req_lower:
        for f in norm_files:
            f_lower = f.lower()
            if '.github/workflows/' in f_lower or any(os.path.basename(f_lower) == k for k in ('ci.yml', 'ci.yaml', 'ci_pipeline.yml', '.gitlab-ci.yml', 'jenkinsfile')):
                return True
        return False

    return False


def calculate_compliance(sdlc_model, existing_files, files_dict=None):
    """
    Evaluates deliverable presence for the selected SDLC model.
    Returns: (raw_compliance_score 0-100, list of missing rule dicts, list of satisfied item paths)
    """
    rules = get_rules_for_model(sdlc_model)
    if not rules:
        return 0, [], []

    total_weight = sum(r["weightage"] for r in rules)
    earned_weight = 0
    missing = []
    satisfied_items = []

    existing_set = set(_normalize_path(f) for f in existing_files)

    for rule in rules:
        if is_item_present(rule["required_item"], existing_set, existing_files, files_dict=files_dict, phase_name=rule["phase_name"]):
            earned_weight += rule["weightage"]
            satisfied_items.append(rule["required_item"])
        else:
            missing.append(rule)

    score = round((earned_weight / total_weight) * 100) if total_weight else 0
    return score, missing, satisfied_items


def detect_embedded_versions(existing_files, files_dict=None):
    """
    Detects if the uploaded repository directory contains multiple version subfolders
    (e.g., v1/, v2/, v3/ or repo/v1/, repo/v2/ or sprint_1/, sprint_2/).
    Returns a sorted list of (version_label, sub_files_list, sub_files_dict).
    """
    version_pattern = re.compile(r'^(v\d+(?:\.\d+)*|version[_\-]?\d+|sprint[_\-]?\d+|iteration[_\-]?\d+|release[_\-]?\d+)$', re.IGNORECASE)
    buckets = {}

    for f in existing_files:
        norm = _normalize_path(f)
        parts = norm.split('/')
        if len(parts) > 1 and version_pattern.match(parts[0]):
            v_key = parts[0]
            sub_path = '/'.join(parts[1:])
            buckets.setdefault(v_key, []).append((f, sub_path))
        elif len(parts) > 2 and version_pattern.match(parts[1]):
            v_key = parts[1]
            sub_path = '/'.join(parts[2:])
            buckets.setdefault(v_key, []).append((f, sub_path))

    if len(buckets) < 2:
        return []

    def _sort_key(label):
        nums = [int(n) for n in re.findall(r'\d+', label)]
        return nums if nums else [0]

    sorted_versions = []
    for v_label in sorted(buckets.keys(), key=_sort_key):
        pairs = buckets[v_label]
        sub_list = [sub for _, sub in pairs]
        sub_dict = {sub: (files_dict.get(orig, "") if files_dict else "") for orig, sub in pairs}
        sorted_versions.append((v_label, sub_list, sub_dict))

    return sorted_versions


def get_repo_version_history(repo_name, sdlc_model):
    """
    Fetches historical version audits for the given repository from SQLite,
    ordered chronologically from oldest version to newest.
    """
    if not repo_name:
        return []
    try:
        conn = get_connection()
        rows = conn.execute(
            """
            SELECT id, repo_name, version_tag, sdlc_model, compliance_score,
                   ai_quality_score, composite_score, total_files, missing_count,
                   loc_count, assertions_count, phases_json, scanned_at
            FROM audit_history
            WHERE LOWER(repo_name) = LOWER(?) AND LOWER(sdlc_model) = LOWER(?)
            ORDER BY id ASC
            """,
            (repo_name, sdlc_model)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


def evaluate_sdlc_methodology(
    sdlc_model,
    existing_files,
    files_dict=None,
    version_tag="v1.0",
    repo_name="Uploaded Project",
    ast_summary=None
):
    """
    Core SDLC Governance & Multi-Version Lifecycle Engine.
    Executes model-specific software engineering rules AND evaluates version-over-version
    progression (v1 -> v2 -> v3...) to verify whether the project actually follows
    the selected SDLC methodology.
    """
    rules = get_rules_for_model(sdlc_model)
    raw_compliance, missing_rules, satisfied_items = calculate_compliance(sdlc_model, existing_files, files_dict)
    satisfied_set = set(satisfied_items)

    # 1. Compute Phase-by-Phase Completion Breakdown in canonical order
    phase_order = []
    phase_stats = {}
    for r in rules:
        p = r["phase_name"]
        if p not in phase_stats:
            phase_order.append(p)
            phase_stats[p] = {"phase": p, "total_weight": 0, "earned_weight": 0, "total_items": 0, "completed_items": 0}
        phase_stats[p]["total_weight"] += r["weightage"]
        phase_stats[p]["total_items"] += 1
        if r["required_item"] in satisfied_set:
            phase_stats[p]["earned_weight"] += r["weightage"]
            phase_stats[p]["completed_items"] += 1

    phases_breakdown = []
    for p in phase_order:
        st = phase_stats[p]
        pct = round((st["earned_weight"] / st["total_weight"]) * 100) if st["total_weight"] else 0
        status = "COMPLETED" if pct == 100 else ("IN_PROGRESS" if pct > 0 else "LOCKED")
        phases_breakdown.append({
            "phase": p,
            "completion_pct": pct,
            "completed_items": st["completed_items"],
            "total_items": st["total_items"],
            "weight": st["total_weight"],
            "status": status
        })

    # 2. Build Multi-Version Timeline (Embedded subfolders OR DB history + current snapshot)
    embedded_versions = detect_embedded_versions(existing_files, files_dict)
    version_timeline = []

    if embedded_versions:
        for v_label, v_files, v_dict in embedded_versions:
            v_comp, v_miss, v_sat = calculate_compliance(sdlc_model, v_files, v_dict)
            v_active_phases = sorted({r["phase_name"] for r in rules if r["required_item"] in set(v_sat)})
            version_timeline.append({
                "version": v_label,
                "compliance_score": v_comp,
                "artifacts_verified": len(v_sat),
                "total_artifacts": len(rules),
                "active_phases": v_active_phases,
                "source": "embedded-subfolder"
            })
    else:
        db_history = get_repo_version_history(repo_name, sdlc_model)
        seen_versions = set()
        for row in db_history:
            v_tag = row.get("version_tag") or "v1.0"
            if v_tag.lower() == (version_tag or "v1.0").lower():
                continue  # Replace same version tag with current fresh run
            seen_versions.add(v_tag.lower())
            try:
                p_list = json.loads(row.get("phases_json") or "[]")
            except Exception:
                p_list = []
            version_timeline.append({
                "version": v_tag,
                "compliance_score": row["compliance_score"],
                "composite_score": row["composite_score"],
                "loc": row.get("loc_count", 0),
                "assertions": row.get("assertions_count", 0),
                "active_phases": p_list,
                "scanned_at": row.get("scanned_at"),
                "source": "history-ledger"
            })

        current_active_phases = [p["phase"] for p in phases_breakdown if p["completion_pct"] > 0]
        version_timeline.append({
            "version": version_tag or "v1.0",
            "compliance_score": raw_compliance,
            "loc": (ast_summary or {}).get("total_loc", 0),
            "assertions": (ast_summary or {}).get("total_assertions", 0),
            "active_phases": current_active_phases,
            "source": "current-scan"
        })

    # 3. Execute Model-Specific SDLC Governance Logic
    model_key = sdlc_model.lower()
    methodology_penalty = 0
    methodology_bonus = 0
    gate_status = "VERIFIED"
    methodology_name = sdlc_model
    sdlc_findings = []
    version_findings = []

    # -------------------------------------------------------------------------
    # MODEL 1: WATERFALL (Strict Sequential Phase-Gate Governance)
    # -------------------------------------------------------------------------
    if model_key == "waterfall":
        methodology_name = "Waterfall Sequential Phase-Gate Engine"
        # Check out-of-sequence phases: a later phase has artifacts while an earlier phase is < 100%
        out_of_order_violations = []
        for idx, p_info in enumerate(phases_breakdown):
            if p_info["completion_pct"] > 0:
                for prev_info in phases_breakdown[:idx]:
                    if prev_info["completion_pct"] < 100:
                        out_of_order_violations.append(f"{p_info['phase']} started before {prev_info['phase']} ({prev_info['completion_pct']}%) was sealed")

        if out_of_order_violations:
            unique_v = list(dict.fromkeys(out_of_order_violations))
            methodology_penalty += min(20, len(unique_v) * 8)
            gate_status = "PHASE-GATE VIOLATION"
            sdlc_findings.append(f"Waterfall Gate Violation (-{methodology_penalty} pts): {unique_v[0]}. Waterfall mandates 100% phase sign-off before next phase begins.")
        elif raw_compliance == 100:
            gate_status = "ALL 5 GATES SEALED"
            sdlc_findings.append("Waterfall Sequential Integrity Verified: All 5 linear phases (Requirements → Design → Source → Testing → DevOps) are 100% complete.")
        else:
            gate_status = "SEQUENTIAL IN-PROGRESS"
            sdlc_findings.append("Waterfall Phase Order Valid: Active deliverables follow strict top-down sequence.")

        # Multi-Version Waterfall check
        if len(version_timeline) >= 2:
            prev_v = version_timeline[-2]
            curr_v = version_timeline[-1]
            delta_comp = curr_v["compliance_score"] - prev_v["compliance_score"]
            if "Source" in prev_v.get("active_phases", []) and "Requirements" not in prev_v.get("active_phases", []):
                methodology_penalty += 12
                gate_status = "RETROACTIVE SPEC VIOLATION"
                version_findings.append(
                    f"Version History Violation ({prev_v['version']} → {curr_v['version']}): Source code existed in {prev_v['version']} before Requirements were defined (-12 pts)."
                )
            elif delta_comp >= 0:
                version_findings.append(
                    f"Waterfall Version Progression ({prev_v['version']} → {curr_v['version']}): Compliance advanced by +{delta_comp}% in forward phase order."
                )
            else:
                methodology_penalty += 10
                version_findings.append(
                    f"Version Regression Alert ({prev_v['version']} → {curr_v['version']}): Compliance dropped by {delta_comp}% (-10 pts)."
                )
        else:
            version_findings.append(
                f"Baseline Snapshot ({version_tag}): Upload subsequent versions (e.g. v1.1, v2.0) as phases complete to audit temporal phase-gate transitions."
            )

    # -------------------------------------------------------------------------
    # MODEL 2: AGILE / SCRUM (Sprint Velocity, Backlog & Working Software)
    # -------------------------------------------------------------------------
    elif model_key == "agile":
        methodology_name = "Agile / Scrum Sprint Velocity Engine"
        has_backlog = "docs/backlog.md" in satisfied_set
        has_board = "docs/sprint_board.json" in satisfied_set
        has_code = "src/components/" in satisfied_set and "src/api/" in satisfied_set
        has_tests = "tests/unit/" in satisfied_set and "tests/integration/" in satisfied_set

        if not has_backlog or not has_board:
            methodology_penalty += 10
            gate_status = "MISSING SPRINT BACKLOG"
            sdlc_findings.append("Agile Ceremony Deficit (-10 pts): Missing Product Backlog (docs/backlog.md) or Sprint Board (docs/sprint_board.json).")
        elif has_code and has_tests:
            methodology_bonus += 5
            gate_status = "SPRINT READY // CI ACTIVE"
            sdlc_findings.append("Agile Increment Verified (+5 pts): Working full-stack software paired with continuous unit & integration test suites.")

        if len(version_timeline) >= 2:
            prev_v = version_timeline[-2]
            curr_v = version_timeline[-1]
            delta_comp = curr_v["compliance_score"] - prev_v["compliance_score"]
            delta_loc = curr_v.get("loc", 0) - prev_v.get("loc", 0)
            methodology_bonus += 5
            version_findings.append(
                f"Sprint Velocity ({prev_v['version']} → {curr_v['version']}): +{delta_comp}% deliverable velocity, ΔLOC {delta_loc:+d} (+5 velocity bonus)."
            )
        else:
            version_findings.append(
                f"Sprint 1 Snapshot ({version_tag}): Agile thrives on iterative sprints. Upload Sprint 2 (v2.0) to measure sprint-over-sprint velocity."
            )

    # -------------------------------------------------------------------------
    # MODEL 3: V-MODEL (Strict Left-to-Right V-Wing Verification Pairing)
    # -------------------------------------------------------------------------
    elif model_key == "v-model":
        methodology_name = "V-Model Dual-Wing Verification & Validation Engine"
        v_pairs = [
            ("Requirements ↔ UAT", "1_Requirements/SRS.md", "4_Validation/acceptance_test_plan.md"),
            ("System Design ↔ Integration", "2_Design/system_design.md", "4_Validation/integration_tests/"),
            ("Source Code ↔ Unit Tests", "3_Source/", "4_Validation/unit_tests/"),
        ]
        paired_count = 0
        unbalanced_wings = []
        for label, left_item, right_item in v_pairs:
            l_ok = left_item in satisfied_set
            r_ok = right_item in satisfied_set
            if l_ok and r_ok:
                paired_count += 1
            elif l_ok != r_ok:
                missing_side = right_item if l_ok else left_item
                unbalanced_wings.append(f"{label} (missing {missing_side})")

        if unbalanced_wings:
            methodology_penalty += len(unbalanced_wings) * 8
            gate_status = f"V-WING IMBALANCE ({paired_count}/3 PAIRED)"
            sdlc_findings.append(
                f"V-Model Wing Asymmetry (-{methodology_penalty} pts): {len(unbalanced_wings)} specification/validation pair(s) unverified — {unbalanced_wings[0]}."
            )
        elif paired_count == 3:
            gate_status = "V-WINGS 100% SYMMETRIC"
            sdlc_findings.append("V-Model Verification Symmetry Confirmed: All 3 Left-Wing specifications are strictly paired with Right-Wing test suites.")
        else:
            gate_status = "AWAITING V-PAIRS"
            sdlc_findings.append(f"V-Model Pairing Status: {paired_count} of 3 V-Wing verification pairs completed.")

        if len(version_timeline) >= 2:
            prev_v = version_timeline[-2]
            curr_v = version_timeline[-1]
            version_findings.append(
                f"V-Model Traceability ({prev_v['version']} → {curr_v['version']}): Verification maturity progressed from {prev_v['compliance_score']}% to {curr_v['compliance_score']}%."
            )
        else:
            version_findings.append(f"V-Model Baseline ({version_tag}): Pair every specification in v1.0 with its validation test suite in v2.0.")

    # -------------------------------------------------------------------------
    # MODEL 4: SPIRAL (4-Quadrant Risk-Driven Loop Governance)
    # -------------------------------------------------------------------------
    elif model_key == "spiral":
        methodology_name = "Spiral Risk-Driven Quadrant Engine"
        has_risk_log = "1_Objectives/risk_log.md" in satisfied_set
        has_spike = "2_Prototype/spike_evaluation.md" in satisfied_set
        has_prod = "3_Engineering/production_src/" in satisfied_set

        if has_prod and (not has_risk_log or not has_spike):
            methodology_penalty += 15
            gate_status = "UNMITIGATED RISK BYPASS"
            sdlc_findings.append(
                "Spiral Risk Governance Violation (-15 pts): Production code built before Risk Log (1_Objectives/risk_log.md) and Prototype Spike (2_Prototype/spike_evaluation.md) were resolved."
            )
        elif has_risk_log and has_spike:
            gate_status = "RISK QUADRANTS VERIFIED"
            sdlc_findings.append("Spiral Risk Mitigation Verified: Technical risk vectors and prototype spikes documented prior to production scaling.")
        else:
            gate_status = "QUADRANT 1 INCOMPLETE"
            sdlc_findings.append("Spiral Lifecycle: Begin with Quadrant 1 (Mission Statement & Risk Log) before engineering.")

        if len(version_timeline) < 2 and raw_compliance < 100:
            version_findings.append(f"Spiral Loop 1 ({version_tag}): Spiral requires iterative risk loops (Loop 1 Prototype → Loop 2 Hardened Build).")
        elif len(version_timeline) >= 2:
            prev_v = version_timeline[-2]
            curr_v = version_timeline[-1]
            version_findings.append(f"Spiral Loop Evolution ({prev_v['version']} → {curr_v['version']}): Risk loop progressed from {prev_v['compliance_score']}% to {curr_v['compliance_score']}%.")

    # -------------------------------------------------------------------------
    # MODEL 5: ITERATIVE / RUP (Inception → Elaboration → Construction → Transition)
    # -------------------------------------------------------------------------
    elif model_key == "iterative":
        methodology_name = "Iterative RUP Phase Milestone Engine"
        inception_pct = next((p["completion_pct"] for p in phases_breakdown if p["phase"] == "Inception"), 0)
        elaboration_pct = next((p["completion_pct"] for p in phases_breakdown if p["phase"] == "Elaboration"), 0)
        construction_pct = next((p["completion_pct"] for p in phases_breakdown if p["phase"] == "Construction"), 0)

        if construction_pct > 0 and (inception_pct < 100 or elaboration_pct < 100):
            methodology_penalty += 12
            gate_status = "PREMATURE CONSTRUCTION"
            sdlc_findings.append(
                f"Iterative RUP Violation (-12 pts): Construction ({construction_pct}%) initiated before Inception ({inception_pct}%) and Elaboration ({elaboration_pct}%) baselines were established."
            )
        elif raw_compliance == 100:
            gate_status = "ALL 4 RUP CYCLES SEALED"
            sdlc_findings.append("Iterative RUP Lifecycle Verified: Inception, Elaboration, Construction, and Transition benchmarks complete.")
        else:
            gate_status = "ITERATION IN-PROGRESS"
            sdlc_findings.append(f"Iterative RUP Maturity: Inception {inception_pct}% | Elaboration {elaboration_pct}% | Construction {construction_pct}%.")

        if len(version_timeline) >= 2:
            prev_v = version_timeline[-2]
            curr_v = version_timeline[-1]
            version_findings.append(f"Iterative Increment ({prev_v['version']} → {curr_v['version']}): Release maturity expanded from {prev_v['compliance_score']}% to {curr_v['compliance_score']}%.")
        else:
            version_findings.append(f"Iteration 1 ({version_tag}): Upload subsequent increments (v0.1 Inception → v0.5 Elaboration → v1.0 Construction) to track RUP cycles.")

    adjusted_compliance = max(0, min(100, raw_compliance - methodology_penalty + methodology_bonus))

    return {
        "raw_compliance_score": raw_compliance,
        "adjusted_compliance_score": adjusted_compliance,
        "methodology_penalty": methodology_penalty,
        "methodology_bonus": methodology_bonus,
        "methodology_name": methodology_name,
        "gate_status": gate_status,
        "phases_breakdown": phases_breakdown,
        "version_tag": version_tag or "v1.0",
        "version_timeline": version_timeline,
        "sdlc_findings": sdlc_findings,
        "version_findings": version_findings,
        "missing_rules": missing_rules,
        "satisfied_items": satisfied_items,
    }


def get_next_quest(sdlc_model, existing_files, files_dict=None):
    """
    Walks quest_steps in step_order, skipping any step whose rule is already
    satisfied, and respecting prerequisite_step_id so nothing is surfaced
    out of order. Returns the first unmet step, or None if all complete.
    """
    conn = get_connection()
    steps = conn.execute(
        """
        SELECT qs.*, r.required_item, r.phase_name
        FROM quest_steps qs
        JOIN sdlc_rules r ON qs.rule_id = r.id
        WHERE LOWER(r.sdlc_model) = LOWER(?)
        ORDER BY qs.step_order ASC
        """,
        (sdlc_model,),
    ).fetchall()
    conn.close()

    existing_set = set(_normalize_path(f) for f in existing_files)
    completed_step_ids = set()

    for step in steps:
        is_done = is_item_present(step["required_item"], existing_set, existing_files, files_dict=files_dict, phase_name=step["phase_name"])
        if is_done:
            completed_step_ids.add(step["id"])
            continue

        prereq = step["prerequisite_step_id"]
        if prereq is not None and prereq not in completed_step_ids:
            continue

        return {
            "phase": step["phase_name"],
            "message": step["quest_message"],
            "step_order": step["step_order"],
            "required_item": step["required_item"],
        }

    return None
