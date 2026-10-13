import io
import json
import zipfile
from flask import Blueprint, jsonify, request, send_file
from models.init_db import get_connection

templates_bp = Blueprint("templates", __name__)


@templates_bp.route("/api/templates", methods=["GET"])
def get_templates():
    """Returns all available SDLC models, their tech stacks, and rules."""
    conn = get_connection()
    templates_rows = conn.execute("SELECT * FROM templates").fetchall()
    rules_rows = conn.execute("SELECT * FROM sdlc_rules ORDER BY sdlc_model, id ASC").fetchall()
    conn.close()

    models = sorted({row["sdlc_model"] for row in templates_rows})
    stacks = sorted({row["tech_stack"] for row in templates_rows})

    templates_by_model = {}
    for r in templates_rows:
        try:
            folder_struct = json.loads(r["folder_structure"])
        except Exception:
            folder_struct = {}
        templates_by_model[r["sdlc_model"]] = {
            "tech_stack": r["tech_stack"],
            "folder_structure": folder_struct
        }

    rules_by_model = {}
    for r in rules_rows:
        m = r["sdlc_model"]
        if m not in rules_by_model:
            rules_by_model[m] = []
        rules_by_model[m].append({
            "id": r["id"],
            "phase": r["phase_name"],
            "item": r["required_item"],
            "weight": r["weightage"]
        })

    return jsonify({
        "models": models,
        "tech_stacks": stacks,
        "templates": templates_by_model,
        "rules": rules_by_model
    })


@templates_bp.route("/api/scaffold-download", methods=["GET"])
def download_scaffold():
    """
    Builds and downloads an in-memory ZIP package containing the baseline
    folder structure and starter engineering files for the requested SDLC model.
    """
    model = request.args.get("model", "Waterfall")
    conn = get_connection()
    tmpl = conn.execute(
        "SELECT * FROM templates WHERE LOWER(sdlc_model) = LOWER(?)", (model,)
    ).fetchone()
    conn.close()

    if not tmpl:
        return jsonify({"error": f"Template for model '{model}' not found"}), 404

    try:
        folder_structure = json.loads(tmpl["folder_structure"])
    except Exception:
        folder_structure = {}

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Generate starter files based on structure
        root_dir = f"QuestFlow_{model}_Project"

        readme_content = (
            f"# {model} Engineering Project Scaffold\n\n"
            f"Generated via **QuestFlow SDLC Governance & Compliance Engine**.\n"
            f"Target Tech Stack: {tmpl['tech_stack']}\n\n"
            f"## Directory Structure & Deliverables:\n"
            f"Follow the sequential quest milestones to achieve 100% repository compliance.\n"
        )
        zf.writestr(f"{root_dir}/README.md", readme_content)
        zf.writestr(f"{root_dir}/.gitignore", "__pycache__/\nnode_modules/\n*.log\n.env\ndist/\n")

        for key, value in folder_structure.items():
            if value is None:
                if key not in ("README.md", ".gitignore"):
                    zf.writestr(f"{root_dir}/{key}", f"# {key}\nInitial template artifact.\n")
            elif isinstance(value, list):
                dir_name = key
                if not value:
                    zf.writestr(f"{root_dir}/{dir_name}/.gitkeep", "")
                for file_item in value:
                    if file_item.endswith("/"):
                        zf.writestr(f"{root_dir}/{dir_name}/{file_item}.gitkeep", "")
                    else:
                        file_path = f"{root_dir}/{dir_name}/{file_item}"
                        if file_item.endswith(".md"):
                            starter_text = (
                                f"# {file_item.replace('.md', '')}\n\n"
                                f"## 1. Introduction & Scope\nDescribe the system objectives here.\n\n"
                                f"## 2. Deliverables & Specifications\nDetail functional items and acceptance criteria.\n"
                            )
                        elif file_item.endswith(".sql"):
                            starter_text = "-- DDL Schema Definition\nCREATE TABLE app_entities (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    name TEXT NOT NULL\n);\n"
                        elif "Dockerfile" in file_item:
                            starter_text = "FROM python:3.12-slim\nWORKDIR /app\nCOPY . .\nCMD [\"python\", \"app.py\"]\n"
                        else:
                            starter_text = f"// Starter file: {file_item}\n"
                        zf.writestr(file_path, starter_text)

    zip_buffer.seek(0)
    download_filename = f"QuestFlow_{model}_Scaffold.zip"
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=download_filename
    )
