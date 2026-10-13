import io
import os
import zipfile
from flask import Blueprint, request, jsonify
from services.rule_engine import (
    calculate_compliance,
    evaluate_sdlc_methodology,
    get_next_quest,
    get_repo_version_history,
)
from services.ml_engine import audit_repository_with_ai, get_ml_status
from models.init_db import get_connection

check_bp = Blueprint("check", __name__)


@check_bp.route("/api/check-sdlc", methods=["POST"])
def check_sdlc():
    data = request.get_json(silent=True) or {}
    sdlc_model = data.get("sdlc_model", "Waterfall")
    version_tag = data.get("version_tag", "v1.0")
    repo_name = data.get("repo_name", "Repository")
    existing_files = data.get("existing_files", [])

    if data.get("files"):
        return jsonify(audit_repository_with_ai(repo_name, sdlc_model, data["files"], version_tag=version_tag))

    raw_score, missing, satisfied = calculate_compliance(sdlc_model, existing_files)
    sdlc_eval = evaluate_sdlc_methodology(
        sdlc_model=sdlc_model,
        existing_files=existing_files,
        version_tag=version_tag,
        repo_name=repo_name,
    )
    next_quest = get_next_quest(sdlc_model, existing_files)

    return jsonify({
        "score": sdlc_eval["adjusted_compliance_score"],
        "raw_score": raw_score,
        "missing": [{"phase": m["phase_name"], "required_item": m["required_item"], "weightage": m["weightage"]} for m in missing],
        "satisfied_items": satisfied,
        "next_quest": next_quest,
        "sdlc_model": sdlc_model,
        "version_tag": version_tag,
        "sdlc_governance": sdlc_eval,
    })


@check_bp.route("/api/scan-repo", methods=["POST"])
def scan_repo():
    data = request.get_json(silent=True) or {}
    sdlc_model = data.get("sdlc_model", "Waterfall")
    version_tag = data.get("version_tag", "v1.0")
    repo_name = data.get("repo_name", "Uploaded Project")
    files_dict = data.get("files") or {f: "" for f in data.get("existing_files", [])}

    return jsonify(audit_repository_with_ai(repo_name, sdlc_model, files_dict, version_tag=version_tag))


@check_bp.route("/api/upload-repo", methods=["POST"])
def upload_repo():
    sdlc_model = request.form.get("sdlc_model", "Waterfall")
    version_tag = request.form.get("version_tag", "v1.0")
    repo_name = request.form.get("repo_name", "Uploaded Archive")
    uploaded_files_dict = {}

    file_obj = request.files.get("file") or request.files.get("repo_zip")
    if file_obj and file_obj.filename:
        repo_name = os.path.splitext(file_obj.filename)[0]
        try:
            with zipfile.ZipFile(io.BytesIO(file_obj.read())) as zf:
                for name in zf.namelist():
                    if name.endswith("/") or any(ign in name.lower() for ign in ["__pycache__", ".git/", "node_modules/", ".ds_store"]):
                        continue
                    info = zf.getinfo(name)
                    content = zf.read(name).decode("utf-8", errors="ignore") if info.file_size <= 250 * 1024 else "[Large file]"
                    parts = name.split("/")
                    norm_path = "/".join(parts[1:]) if len(parts) > 1 and not parts[0].startswith(("1_", "2_", "3_", "4_", "5_", "src", "docs")) else name
                    uploaded_files_dict[norm_path] = content
        except Exception as e:
            return jsonify({"error": f"Failed to read ZIP archive: {str(e)}"}), 400

    if not uploaded_files_dict:
        for key, item in request.files.items():
            if item.filename:
                rel_path = request.form.get(f"path_{key}", item.filename)
                uploaded_files_dict[rel_path] = item.read().decode("utf-8", errors="ignore")

    if not uploaded_files_dict:
        return jsonify({"error": "No valid files received for repository evaluation."}), 400

    return jsonify(audit_repository_with_ai(repo_name, sdlc_model, uploaded_files_dict, version_tag=version_tag))


@check_bp.route("/api/version-history", methods=["GET"])
def version_history():
    repo_name = request.args.get("repo_name", "")
    sdlc_model = request.args.get("sdlc_model", "Waterfall")
    return jsonify({
        "repo_name": repo_name,
        "sdlc_model": sdlc_model,
        "versions": get_repo_version_history(repo_name, sdlc_model),
    })


@check_bp.route("/api/ml-status", methods=["GET"])
def ml_status():
    return jsonify(get_ml_status())


@check_bp.route("/api/audit-history", methods=["GET"])
def audit_history():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM audit_history ORDER BY scanned_at DESC LIMIT 20").fetchall()
    conn.close()
    return jsonify({"audits": [dict(r) for r in rows]})


@check_bp.route("/api/audit-details/<int:audit_id>", methods=["GET"])
def audit_details(audit_id):
    conn = get_connection()
    audit_row = conn.execute("SELECT * FROM audit_history WHERE id = ?", (audit_id,)).fetchone()
    if not audit_row:
        conn.close()
        return jsonify({"error": "Audit record not found"}), 404
    files_rows = conn.execute("SELECT * FROM audit_file_details WHERE audit_id = ? ORDER BY id ASC", (audit_id,)).fetchall()
    conn.close()

    return jsonify({"audit": dict(audit_row), "files": [dict(f) for f in files_rows]})
