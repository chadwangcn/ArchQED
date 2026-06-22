#!/usr/bin/env bash
set -euo pipefail
command -v codex >/dev/null 2>&1 || { echo "codex CLI not found" >&2; exit 127; }
exec codex exec --sandbox workspace-write '$archqed-compile Reconcile current backend architecture and feature-detail changes. Read .archqed/project.json. Update generated control data only, respect approval gates, create gaps instead of guessing, run doctor, and close compilation only when valid.'
