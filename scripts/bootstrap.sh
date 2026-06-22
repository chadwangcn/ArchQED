#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$PWD"
if [[ $# -gt 0 && "$1" != --* ]]; then
  TARGET="$1"
  shift
fi
PYTHON_BIN="${ARCHQED_PYTHON:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "ArchQED requires Python 3.11+. Set ARCHQED_PYTHON to a compatible interpreter." >&2
  exit 127
fi
"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit("ArchQED requires Python 3.11 or newer")
PY
"$PYTHON_BIN" "$SOURCE/scripts/verify-release.py"
export PYTHONPATH="$SOURCE/src${PYTHONPATH:+:$PYTHONPATH}"
exec "$PYTHON_BIN" -m archqed bootstrap --target "$TARGET" "$@"
