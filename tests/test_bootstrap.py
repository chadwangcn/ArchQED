import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from archqed.adapters import configure_adapter, load_project_configuration
from archqed.bootstrap import bootstrap_project, uninstall_project
from archqed.checks import run_project_checks
from archqed.doctor import doctor_project
from archqed.errors import GateError


class BootstrapTests(unittest.TestCase):
    def project(self):
        temp = tempfile.TemporaryDirectory()
        return temp, Path(temp.name)

    def test_bootstrap_go_project_installs_self_contained_runtime(self):
        temp, root = self.project()
        self.addCleanup(temp.cleanup)
        (root / "go.mod").write_text("module example.com/service\n\ngo 1.22\n")
        result = bootstrap_project(root)
        self.assertTrue(result["ok"])
        self.assertEqual(result["adapter"], "go")
        self.assertTrue((root / "scripts/archqed").exists())
        self.assertTrue((root / "scripts/archqed.ps1").exists())
        self.assertTrue((root / ".archqed/runtime/archqed/cli.py").exists())
        self.assertTrue((root / ".agents/skills/archqed-compile/SKILL.md").exists())
        self.assertTrue((root / ".codex/agents/archqed-verifier.toml").exists())
        self.assertTrue((root / result["evidence"]).exists())
        self.assertTrue(doctor_project(root)["ok"])
        if os.name == "nt":
            command = ["pwsh", "-NoProfile", "-File", str(root / "scripts/archqed.ps1"), "--version"]
        else:
            command = [str(root / "scripts/archqed"), "--version"]
        completed = subprocess.run(
            command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "ARCHQED_PYTHON": "python"},
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("0.2.0", completed.stdout)

    def test_bootstrap_is_idempotent_and_preserves_human_agents_text_and_commands(self):
        temp, root = self.project()
        self.addCleanup(temp.cleanup)
        (root / "Makefile").write_text("test:\n\ttrue\n")
        (root / "AGENTS.md").write_text("# Team rules\n\nKeep this.\n")
        bootstrap_project(root, adapter="generic")
        configure_adapter(root, "generic", ["unit_test=make test"])
        bootstrap_project(root)
        agents = (root / "AGENTS.md").read_text()
        self.assertEqual(agents.count("# >>> ArchQED managed instructions >>>"), 1)
        self.assertIn("Keep this.", agents)
        project = load_project_configuration(root)
        self.assertEqual(project["commands"]["unit_test"]["source"], "human")

    def test_ambiguous_project_blocks_before_initialization_and_writes_probe(self):
        temp, root = self.project()
        self.addCleanup(temp.cleanup)
        (root / "pyproject.toml").write_text('[project]\ndependencies = ["fastapi"]\n')
        (root / "package.json").write_text(json.dumps({"dependencies": {"express": "1.0.0"}}))
        with self.assertRaises(GateError):
            bootstrap_project(root)
        self.assertTrue((root / ".archqed/probe.json").exists())
        self.assertFalse((root / ".ai-control/manifest.json").exists())
        result = bootstrap_project(root, adapter="python")
        self.assertEqual(result["adapter"], "python")

    def test_generic_project_check_creates_evidence(self):
        temp, root = self.project()
        self.addCleanup(temp.cleanup)
        bootstrap_project(root, adapter="generic")
        configure_adapter(root, "generic", ["unit_test=python -c \"print('ok')\""])
        result = run_project_checks(root, only=["unit_test"])
        self.assertTrue(result["passed"])
        self.assertTrue((root / result["evidence"]).exists())

    def test_bootstrap_refuses_malformed_managed_agents_block(self):
        temp, root = self.project()
        self.addCleanup(temp.cleanup)
        (root / "go.mod").write_text("module example.com/service\n")
        (root / "AGENTS.md").write_text("# >>> ArchQED managed instructions >>>\nhuman text without end marker\n")
        with self.assertRaises(GateError):
            bootstrap_project(root)

    def test_bootstrap_preserves_existing_codex_config(self):
        temp, root = self.project()
        self.addCleanup(temp.cleanup)
        (root / ".codex").mkdir()
        existing = "model = \"custom-model\"\n"
        (root / ".codex/config.toml").write_text(existing)
        (root / "go.mod").write_text("module example.com/service\n")
        bootstrap_project(root)
        self.assertEqual((root / ".codex/config.toml").read_text(), existing)

    def test_uninstall_preserves_control_data_by_default(self):
        temp, root = self.project()
        self.addCleanup(temp.cleanup)
        (root / "go.mod").write_text("module example.com/service\n")
        bootstrap_project(root)
        result = uninstall_project(root)
        self.assertTrue(result["ok"])
        self.assertTrue((root / ".ai-control/manifest.json").exists())
        self.assertFalse((root / ".agents/skills/archqed-compile/SKILL.md").exists())
        self.assertFalse((root / ".archqed/runtime").exists())


if __name__ == "__main__":
    unittest.main()
