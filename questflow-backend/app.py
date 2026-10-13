from flask import Flask, jsonify
from flask_cors import CORS

from routes.templates_routes import templates_bp
from routes.check_routes import check_bp
from services.ml_engine import train_or_load_classifier

app = Flask(__name__)
CORS(app)  # allow the frontend to call this API

app.register_blueprint(templates_bp)
app.register_blueprint(check_bp)

# Warm up ML pipeline at startup
try:
    train_or_load_classifier()
except Exception as e:
    print(f"[QuestFlow Backend] ML pipeline warning: {e}")


@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": "QuestFlow Backend API // AI & SDLC Governance",
        "status": "online",
        "port": 5000,
        "endpoints": [
            "/api/health",
            "/api/templates",
            "/api/scaffold-download",
            "/api/check-sdlc",
            "/api/scan-repo",
            "/api/upload-repo",
            "/api/ml-status",
            "/api/audit-history",
            "/api/audit-details/<id>"
        ]
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "QuestFlow backend",
        "engine": "SDLC Governance & AI Repository Intelligence",
        "port": 5000
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
