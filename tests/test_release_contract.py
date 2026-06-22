import hashlib
import json
import re
import unittest
from pathlib import Path

from archqed import __version__
from archqed.adapters import ADAPTERS
from archqed.templates import MANAGED_FILES


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_BOOTSTRAP_URL = "https://raw.githubusercontent.com/chadwangcn/ArchQED/main/BOOTSTRAP.md"
CANONICAL_STABLE_URL = "https://raw.githubusercontent.com/chadwangcn/ArchQED/main/stable.json"


class ReleaseContractTests(unittest.TestCase):
    def test_release_manifest_matches_bootstrap_and_runtime(self):
        manifest = json.loads((ROOT / "release-manifest.json").read_text())
        bootstrap = (ROOT / "BOOTSTRAP.md").read_bytes()
        self.assertEqual(manifest["version"], __version__)
        self.assertEqual(manifest["release_ref"], "stable-channel")
        self.assertEqual(manifest["bootstrap_url"], CANONICAL_BOOTSTRAP_URL)
        self.assertEqual(manifest["stable_url"], CANONICAL_STABLE_URL)
        self.assertEqual(manifest["bootstrap_sha256"], hashlib.sha256(bootstrap).hexdigest())
        self.assertEqual(set(manifest["adapters"]), set(ADAPTERS))
        self.assertTrue(manifest["project_neutral"])

    def test_one_link_protocol_is_permanent_but_install_is_pinned(self):
        text = (ROOT / "BOOTSTRAP.md").read_text()
        self.assertIn(CANONICAL_BOOTSTRAP_URL, text)
        self.assertIn(CANONICAL_STABLE_URL, text)
        self.assertIn("checkout --detach", text)
        self.assertIn("stable.json", text)
        self.assertIn("EVD-BOOTSTRAP", text)
        self.assertIn("PowerShell", text)
        self.assertNotRegex(text, r"raw\.githubusercontent\.com/chadwangcn/ArchQED/v\d+\.\d+\.\d+/BOOTSTRAP\.md")

    def test_core_is_not_coupled_to_a_named_business_project(self):
        paths = [ROOT / "src", ROOT / "docs", ROOT / "README.md", ROOT / "README.zh-CN.md", ROOT / "BOOTSTRAP.md"]
        matches = []
        pattern = re.compile(r"\bK1\b", re.IGNORECASE)
        for base in paths:
            files = [base] if base.is_file() else base.rglob("*")
            for path in files:
                if not path.is_file():
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                if pattern.search(text):
                    matches.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(matches, [])

    def test_repository_managed_files_match_bootstrap_templates(self):
        for relative, expected in MANAGED_FILES.items():
            with self.subTest(path=relative):
                actual = (ROOT / relative).read_text(encoding="utf-8")
                self.assertEqual(actual.rstrip("\n"), expected.rstrip("\n"))

    def test_all_json_contract_files_parse(self):
        for path in list((ROOT / "schemas").glob("*.json")) + [ROOT / "release-manifest.json"]:
            with self.subTest(path=path.name):
                json.loads(path.read_text())


if __name__ == "__main__":
    unittest.main()
