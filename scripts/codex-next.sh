#!/usr/bin/env bash
set -euo pipefail
command -v codex >/dev/null 2>&1 || { echo "codex CLI not found" >&2; exit 127; }
exec codex exec --sandbox workspace-write '$archqed-implement Implement exactly one next approved ArchQED backend task. Use the selected adapter and real integrations, run declared checks, submit implemented_unverified, and delegate final verification to archqed_verifier. Never self-verify.'
