$ErrorActionPreference = "Stop"
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { throw "codex CLI not found" }
codex exec --sandbox workspace-write '$archqed-compile Reconcile current backend architecture and feature-detail changes. Read .archqed/project.json. Update generated control data only and never guess.'
exit $LASTEXITCODE
