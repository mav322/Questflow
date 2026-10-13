"""
Unit Test Suite // QuestFlow Rule Engine & Compliance Gating
"""
import unittest
import os
import sys

# Ensure backend modules are discoverable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "questflow-backend"))
from services.rule_engine import (
    calculate_compliance,
    evaluate_sdlc_methodology,
    get_next_quest,
    get_rules_for_model,
    is_item_present,
)


class TestRuleEngine(unittest.TestCase):

    def setUp(self):
        self.waterfall_rules = get_rules_for_model("Waterfall")
        self.agile_rules = get_rules_for_model("Agile")

    def test_empty_repository_scores_zero(self):
        """Validates that a repository with zero artifacts scores 0% compliance."""
        score, missing, satisfied = calculate_compliance("Waterfall", [])
        self.assertEqual(score, 0)
        self.assertEqual(len(missing), 9)
        self.assertEqual(len(satisfied), 0)

    def test_full_textbook_waterfall_scores_hundred(self):
        """Validates that a complete textbook repository scores 100% compliance."""
        textbook_files = [
            "1_Requirements/SRS.md",
            "1_Requirements/user_stories.md",
            "2_Design/architecture.png",
            "2_Design/schema.sql",
            "3_Source/app.py",
            "4_Testing/unit_tests/test_main.py",
            "4_Testing/test_matrix.md",
            "5_DevOps/Dockerfile",
            "5_DevOps/.github/workflows/ci.yml"
        ]
        score, missing, satisfied = calculate_compliance("Waterfall", textbook_files)
        self.assertEqual(score, 100)
        self.assertEqual(len(missing), 0)
        self.assertEqual(len(satisfied), 9)

    def test_deep_subfolder_matching(self):
        """Validates that files deeply nested inside subfolders satisfy deliverables."""
        nested_files = [
            "questflow-master/questflow-backend/models/schema.sql",
            "questflow-master/questflow-backend/app.py",
            "questflow-master/docs/architecture.png",
            "questflow-master/docs/SRS.md",
            "questflow-master/docs/user_stories.md",
            "questflow-master/tests/unit_tests/test_core.py",
            "questflow-master/docs/test_matrix.md",
            "questflow-master/Dockerfile",
            "questflow-master/.github/workflows/ci.yml"
        ]
        score, missing, satisfied = calculate_compliance("Waterfall", nested_files)
        self.assertEqual(score, 100)
        self.assertEqual(len(missing), 0)
        self.assertIn("2_Design/schema.sql", satisfied)
        self.assertIn("3_Source/", satisfied)
        self.assertIn("5_DevOps/Dockerfile", satisfied)

    def test_dag_prerequisite_quest_ordering(self):
        """Validates that next quest correctly respects topological prerequisite order."""
        first_quest = get_next_quest("Waterfall", [])
        self.assertIsNotNone(first_quest)
        self.assertEqual(first_quest["step_order"], 1)
        self.assertEqual(first_quest["required_item"], "1_Requirements/SRS.md")

        second_quest = get_next_quest("Waterfall", ["1_Requirements/SRS.md"])
        self.assertIsNotNone(second_quest)
        self.assertEqual(second_quest["step_order"], 2)

        all_files = [
            "1_Requirements/SRS.md", "1_Requirements/user_stories.md",
            "2_Design/architecture.png", "2_Design/schema.sql",
            "3_Source/app.py", "4_Testing/unit_tests/test_1.py",
            "4_Testing/test_matrix.md", "5_DevOps/Dockerfile",
            "5_DevOps/.github/workflows/ci.yml"
        ]
        final_quest = get_next_quest("Waterfall", all_files)
        self.assertIsNone(final_quest)

    def test_agile_model_compliance(self):
        """Validates compliance evaluation under Agile/Scrum paradigm."""
        agile_files = [
            "docs/backlog.md",
            "docs/sprint_board.json",
            "docs/wireframes/mockup.png",
            "docs/api_contract.json",
            "src/components/App.jsx",
            "src/api/server.js",
            "tests/unit/app.test.js",
            "tests/integration/api.test.js",
            "Dockerfile",
            "docker-compose.yml"
        ]
        score, missing, satisfied = calculate_compliance("Agile", agile_files)
        self.assertEqual(score, 100)
        self.assertEqual(len(missing), 0)

    def test_sdlc_methodology_differentiation(self):
        """Validates that a Waterfall repo scores 100% on Waterfall but distinct partial scores on other SDLC models."""
        waterfall_repo = [
            "1_Requirements/SRS.md",
            "1_Requirements/user_stories.md",
            "2_Design/architecture.png",
            "2_Design/schema.sql",
            "questflow-backend/app.py",
            "questflow-frontend/script.js",
            "tests/test_rule_engine.py",
            "tests/test_api.py",
            "4_Testing/test_matrix.md",
            "Dockerfile",
            "docker-compose.yml",
            ".github/workflows/ci.yml"
        ]
        wf_eval = evaluate_sdlc_methodology("Waterfall", waterfall_repo)
        ag_eval = evaluate_sdlc_methodology("Agile", waterfall_repo)
        vm_eval = evaluate_sdlc_methodology("V-Model", waterfall_repo)
        sp_eval = evaluate_sdlc_methodology("Spiral", waterfall_repo)
        it_eval = evaluate_sdlc_methodology("Iterative", waterfall_repo)

        self.assertEqual(wf_eval["adjusted_compliance_score"], 100)
        self.assertLess(ag_eval["adjusted_compliance_score"], 100)
        self.assertLess(vm_eval["adjusted_compliance_score"], 100)
        self.assertLess(sp_eval["adjusted_compliance_score"], 100)
        self.assertLess(it_eval["adjusted_compliance_score"], 100)

    def test_waterfall_out_of_order_violation(self):
        """Validates that coding before completing Requirements triggers a Waterfall Phase-Gate Violation penalty."""
        out_of_order_files = ["3_Source/app.py", "5_DevOps/Dockerfile"]
        res = evaluate_sdlc_methodology("Waterfall", out_of_order_files)
        self.assertEqual(res["gate_status"], "PHASE-GATE VIOLATION")
        self.assertGreater(res["methodology_penalty"], 0)
        self.assertLess(res["adjusted_compliance_score"], res["raw_compliance_score"])

    def test_embedded_multi_version_progression(self):
        """Validates multi-version progression across v1/ and v2/ repository subfolders."""
        multi_ver_files = [
            "v1/1_Requirements/SRS.md",
            "v1/1_Requirements/user_stories.md",
            "v2/1_Requirements/SRS.md",
            "v2/1_Requirements/user_stories.md",
            "v2/2_Design/architecture.png",
            "v2/2_Design/schema.sql",
            "v2/3_Source/app.py"
        ]
        res = evaluate_sdlc_methodology("Waterfall", multi_ver_files)
        self.assertEqual(len(res["version_timeline"]), 2)
        self.assertEqual(res["version_timeline"][0]["version"], "v1")
        self.assertEqual(res["version_timeline"][1]["version"], "v2")
        self.assertGreater(res["version_timeline"][1]["compliance_score"], res["version_timeline"][0]["compliance_score"])


if __name__ == "__main__":
    unittest.main()
