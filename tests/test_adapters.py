import json
import tempfile
import unittest
from pathlib import Path

from archqed.adapters import configure_adapter, detect_project, load_project_configuration


class AdapterTests(unittest.TestCase):
    def project(self):
        temp = tempfile.TemporaryDirectory()
        return temp, Path(temp.name)

    def test_detects_python_backend_and_commands(self):
        temp, root = self.project()
        self.addCleanup(temp.cleanup)
        (root / "pyproject.toml").write_text('[project]\ndependencies = ["fastapi", "pytest", "ruff"]\n[build-system]\n')
        probe = detect_project(root)
        self.assertEqual(probe["recommended_adapter"], "python")
        candidate = probe["candidates"][0]
        self.assertEqual(candidate["id"], "python")
        self.assertIn("unit_test", candidate["commands"])
        self.assertIn("lint", candidate["commands"])

    def test_detects_node_scripts_without_inventing_missing_commands(self):
        temp, root = self.project()
        self.addCleanup(temp.cleanup)
        (root / "package.json").write_text(json.dumps({
            "dependencies": {"fastify": "1.0.0"},
            "scripts": {"test": "vitest run", "build": "tsc", "start": "node dist/server.js"},
        }))
        (root / "package-lock.json").write_text("{}")
        probe = detect_project(root)
        self.assertEqual(probe["recommended_adapter"], "node")
        commands = probe["candidates"][0]["commands"]
        self.assertEqual(commands["install"], "npm ci")
        self.assertEqual(commands["unit_test"], "npm test")
        self.assertNotIn("lint", commands)

    def test_multi_stack_is_ambiguous_when_scores_are_close(self):
        temp, root = self.project()
        self.addCleanup(temp.cleanup)
        (root / "pyproject.toml").write_text('[project]\ndependencies = ["fastapi"]\n')
        (root / "package.json").write_text(json.dumps({"dependencies": {"express": "1.0.0"}}))
        probe = detect_project(root)
        self.assertTrue(probe["ambiguous"])
        self.assertIsNone(probe["recommended_adapter"])

    def test_unknown_backend_falls_back_to_generic(self):
        temp, root = self.project()
        self.addCleanup(temp.cleanup)
        (root / "Makefile").write_text("test:\n\ttrue\n")
        probe = detect_project(root)
        self.assertEqual(probe["recommended_adapter"], "generic")
        self.assertFalse(probe["ambiguous"])

    def test_detects_each_builtin_backend_family(self):
        cases = [
            ({"pom.xml": "<project><dependency>spring-boot</dependency></project>"}, "java-maven"),
            ({"build.gradle": "plugins { id 'org.springframework.boot' }"}, "java-gradle"),
            ({"go.mod": "module example.com/service\n"}, "go"),
            ({"service.csproj": "<Project Sdk=\"Microsoft.NET.Sdk.Web\" />"}, "dotnet"),
            ({"Cargo.toml": "[dependencies]\naxum = \"0.7\"\n"}, "rust"),
            ({"composer.json": "{}"}, "php-composer"),
            ({"Gemfile": "gem 'rails'\n"}, "ruby-bundler"),
        ]
        for files, expected in cases:
            with self.subTest(adapter=expected):
                temp, root = self.project()
                try:
                    for name, content in files.items():
                        (root / name).write_text(content)
                    probe = detect_project(root)
                    self.assertEqual(probe["recommended_adapter"], expected)
                finally:
                    temp.cleanup()

    def test_generic_adapter_accepts_human_commands(self):
        temp, root = self.project()
        self.addCleanup(temp.cleanup)
        value = configure_adapter(root, "generic", ["unit_test=make test", "build=make build"])
        self.assertEqual(value["commands"]["unit_test"]["source"], "human")
        self.assertFalse(value["requires_command_configuration"])
        self.assertEqual(load_project_configuration(root)["commands"]["build"]["command"], "make build")


if __name__ == "__main__":
    unittest.main()
