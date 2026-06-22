import tempfile
import unittest
from pathlib import Path

from archqed.changes import approve_change, complete_compile, sync_project
from archqed.errors import DriftError
from archqed.io import read_json, write_json
from archqed.project import init_project, project_status


class ChangeTests(unittest.TestCase):
    def project(self, stage="discovery"):
        temp = tempfile.TemporaryDirectory(); root = Path(temp.name); init_project(root, "demo", stage); return temp, root

    def test_discovery_churn_and_compile(self):
        temp, root = self.project(); self.addCleanup(temp.cleanup)
        (root / "docs/architecture/system.md").write_text("ARCH-SYSTEM-001\nChanged.\n")
        change = sync_project(root)
        self.assertEqual((change["impact"], change["status"]), ("global", "approved"))
        complete_compile(root, change["id"])
        self.assertEqual(project_status(root)["control_state"], "ready")

    def test_repeated_edit_supersedes_pending(self):
        temp, root = self.project(); self.addCleanup(temp.cleanup)
        path = root / "docs/architecture/system.md"; path.write_text("ARCH-SYSTEM-001\nOne.\n")
        first = sync_project(root); path.write_text("ARCH-SYSTEM-001\nTwo.\n"); second = sync_project(root)
        self.assertEqual(read_json(root / f".ai-control/changes/{first['id']}.json")["status"], "superseded")
        self.assertEqual(second["supersedes"], first["id"])

    def test_revert_clears_pending(self):
        temp, root = self.project(); self.addCleanup(temp.cleanup)
        path = root / "docs/architecture/README.md"; original = path.read_text(); path.write_text(original + "\nARCH-TEMP-001\n")
        change = sync_project(root); path.write_text(original); result = sync_project(root)
        self.assertEqual(result["reverted_change"], change["id"])

    def test_stale_approval_rejected(self):
        temp, root = self.project("stabilizing"); self.addCleanup(temp.cleanup)
        path = root / "docs/architecture/system.md"; path.write_text("ARCH-A-001\nOne.\n"); first = sync_project(root)
        path.write_text("ARCH-A-001\nTwo.\n")
        with self.assertRaises(DriftError): approve_change(root, first["id"])
        second = sync_project(root); approve_change(root, second["id"]); complete_compile(root, second["id"])

    def test_feature_change_scopes_by_ref(self):
        temp, root = self.project("stabilizing"); self.addCleanup(temp.cleanup)
        feature = root / "docs/features/story.md"; feature.write_text("REQ-STORY-001\nInitial.\n")
        baseline = sync_project(root); complete_compile(root, baseline["id"])
        base = {"title":"x","dependencies":[],"acceptance":[],"forbidden":[]}
        write_json(root / ".ai-control/tasks/TASK-A.json", {**base,"id":"TASK-A","status":"verified","source_refs":["REQ-STORY-001"]})
        write_json(root / ".ai-control/tasks/TASK-B.json", {**base,"id":"TASK-B","status":"verified","source_refs":["REQ-OTHER-001"]})
        feature.write_text("REQ-STORY-001\nRefined.\n"); change = sync_project(root)
        self.assertEqual(change["affected_tasks"], ["TASK-A"])
        self.assertEqual(read_json(root / ".ai-control/tasks/TASK-B.json")["status"], "verified")


if __name__ == "__main__": unittest.main()
