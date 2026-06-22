#!/usr/bin/env bash
set -euo pipefail
command -v codex >/dev/null 2>&1 || { echo "codex CLI not found" >&2; exit 127; }
exec codex exec --sandbox workspace-write '$archqed-compile Reconcile current architecture and feature-detail changes. Update generated control data only. Respect approval gates, preserve scoped verified work, create gaps instead of guessing, run archqed doctor, and close compilation only when valid.'
