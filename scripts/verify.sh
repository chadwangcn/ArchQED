#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python -m compileall -q src tests
PYTHONPATH=src python -m unittest discover -s tests -v
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
PYTHONPATH=src python -m archqed --root "$TMP" init --name smoke --stage discovery --json >/dev/null
PYTHONPATH=src python -m archqed --root "$TMP" doctor --json >/dev/null
PYTHONPATH=src python -m archqed --root "$TMP" sync --check --json >/dev/null
echo "VERIFY PASSED"
