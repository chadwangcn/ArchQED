#!/usr/bin/env bash
set -euo pipefail
TASK_ID="${1:?usage: scripts/codex-verify.sh TASK-ID}"
command -v codex >/dev/null 2>&1 || { echo "codex CLI not found" >&2; exit 127; }
exec codex exec --sandbox workspace-write "\$archqed-verify Independently verify ${TASK_ID}. Read .archqed/project.json. Do not change product code, tests, human documents, or task requirements. Run ./scripts/archqed verify ${TASK_ID} and inspect evidence."
