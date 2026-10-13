"""
Unit Test Suite // QuestFlow AST Parser & Artifact Quality Scorer
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "questflow-backend"))
from services.ml_engine import parse_code_ast, evaluate_artifact_quality


class TestMLEngine(unittest.TestCase):

    def test_ast_python_code_metrics(self):
        """Verifies AST parser extracts functions, classes, and assertions accurately."""
        py_code = """
import os
import sys

class Evaluator:
    def __init__(self, name):
        self.name = name

    def execute_check(self, x):
        assert x > 0, "Input must be positive"
        return x * 2

def standalone_helper():
    assert True
    return 42
"""
        ast_info = parse_code_ast("test_script.py", py_code)
        self.assertGreater(ast_info["loc"], 5)
        self.assertEqual(ast_info["classes"], 1)
        self.assertGreaterEqual(ast_info["functions"], 2)
        self.assertGreaterEqual(ast_info["assertions"], 2)

    def test_stub_detection_flags_empty_code(self):
        """Flags empty placeholders or stubs with low authenticity."""
        stub_code = "def placeholder():\n    pass"
        ast_info = parse_code_ast("stub.py", stub_code)
        self.assertGreaterEqual(ast_info["stubs"], 1)

        quality = evaluate_artifact_quality("stub.py", stub_code)
        self.assertIn(quality["quality_tier"], ["STUB / DUMMY", "ADEQUATE"])

    def test_production_grade_srs_evaluation(self):
        """Validates that authentic SRS documents with formal sections receive top scores."""
        srs_content = """
# Software Requirements Specification (SRS)
## 1.0 Introduction
The purpose of QuestFlow is to enforce engineering discipline and continuous SDLC governance.
## 2.0 Scope
The system audits multi-tier monorepos, parses code syntax, and executes DAG-ordered milestones.
## 3.0 Functional Requirements
- FR-101: Ingest directories recursively across subfolders.
- FR-102: Compute deterministic compliance score (0-100%).
- FR-103: Topologically sequence prerequisite quest tasks.
## 4.0 Non-Functional Requirements
- NFR-201: Ingestion latency under 300ms.
- NFR-202: Zero data loss during AST traversal.
## 5.0 Acceptance Criteria & User Stories
As a software engineer, I want automated gate validation so that my project meets formal standards.
"""
        quality = evaluate_artifact_quality("1_Requirements/SRS.md", srs_content)
        self.assertEqual(quality["quality_tier"], "PRODUCTION GRADE")
        self.assertGreaterEqual(quality["authenticity_score"], 80)


if __name__ == "__main__":
    unittest.main()
