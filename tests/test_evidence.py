import tempfile
import unittest
from pathlib import Path

from archqed.errors import DriftError, GateError
from archqed.evidence import verify_task
from archqed.io import read_json, write_json
from archqed.project import init_project
from archqed.tasks import next_task, transition_task


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name); init_project(self.root, "demo", "discovery")
        self.path = self.root / ".ai-control/tasks/TASK-1.json"
        write_json(self.path, {"id":"TASK-1","title":"Real path","status":"approved","priority":1,"source_refs":[],"dependencies":[],"acceptance":[{"id":"AC-1","command":"python -c \"print('real')\""}],"forbidden":[{"id":"no-placeholder","pattern":"PLACEHOLDER","paths":["src"]}]})
    def tearDown(self): self.temp.cleanup()

    def test_only_evidence_marks_verified(self):
        self.assertEqual(next_task(self.root)["id"], "TASK-1")
        transition_task(self.root, "TASK-1", "in_progress"); transition_task(self.root, "TASK-1", "implemented_unverified")
        with self.assertRaises(GateError): transition_task(self.root, "TASK-1", "verified")
        result = verify_task(self.root, "TASK-1")
        self.assertTrue(result["passed"]); self.assertEqual(read_json(self.path)["status"], "verified")

    def test_drift_blocks_work(self):
        (self.root / "docs/features/new.md").write_text("REQ-NEW-001\nChanged.\n")
        with self.assertRaises(DriftError): transition_task(self.root, "TASK-1", "in_progress")

    def test_forbidden_fails_verification(self):
        (self.root / "src").mkdir(); (self.root / "src/bad.py").write_text("PLACEHOLDER = True\n")
        transition_task(self.root, "TASK-1", "in_progress"); transition_task(self.root, "TASK-1", "implemented_unverified")
        result = verify_task(self.root, "TASK-1")
        self.assertFalse(result["passed"]); self.assertEqual(result["forbidden_findings"], 1)


if __name__ == "__main__": unittest.main()
