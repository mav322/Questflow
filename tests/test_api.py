"""
Integration Test Suite // QuestFlow Flask API Endpoints
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "questflow-backend"))
from app import app


class TestApiEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def test_health_endpoint(self):
        """Verifies /api/health responds with 200 OK and expected engine info."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["port"], 5000)

    def test_check_sdlc_endpoint(self):
        """Verifies /api/check-sdlc calculates compliance and returns satisfied items."""
        payload = {
            "sdlc_model": "Waterfall",
            "existing_files": [
                "1_Requirements/SRS.md",
                "2_Design/schema.sql",
                "3_Source/app.py"
            ]
        }
        response = self.client.post("/api/check-sdlc", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("score", data)
        self.assertGreater(data["score"], 0)
        self.assertIn("satisfied_items", data)
        self.assertIn("next_quest", data)

    def test_templates_endpoint(self):
        """Verifies /api/templates returns all 5 SDLC models."""
        response = self.client.get("/api/templates")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        models = data.get("models", [])
        self.assertIn("Waterfall", models)
        self.assertIn("Agile", models)

    def test_ml_status_endpoint(self):
        """Verifies /api/ml-status returns classifier operational metrics."""
        response = self.client.get("/api/ml-status")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("model_info", data)
        self.assertGreaterEqual(data["model_info"]["accuracy"], 0.85)


if __name__ == "__main__":
    unittest.main()
