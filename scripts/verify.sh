#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python scripts/verify-release.py
python -m compileall -q src tests
PYTHONPATH=src python -m unittest discover -s tests -v
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
printf 'module example.com/smoke\n\ngo 1.22\n' > "$TMP/go.mod"
PYTHONPATH=src python -m archqed bootstrap --target "$TMP" --json >/tmp/archqed-bootstrap-smoke.json
"$TMP/scripts/archqed" doctor --json >/tmp/archqed-doctor-smoke.json
"$TMP/scripts/archqed" sync --check --json >/dev/null
echo "VERIFY PASSED"
