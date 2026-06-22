#!/usr/bin/env bash
set -euo pipefail
TASK_ID="${1:?usage: scripts/codex-verify.sh TASK-ID}"
command -v codex >/dev/null 2>&1 || { echo "codex CLI not found" >&2; exit 127; }
exec codex exec --sandbox workspace-write "\$archqed-verify Independently verify ${TASK_ID}. Do not change product code, tests, human documents, or task requirements. Run archqed verify ${TASK_ID}, inspect evidence, and report the result."
