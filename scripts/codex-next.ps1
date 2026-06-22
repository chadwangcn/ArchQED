$ErrorActionPreference = "Stop"
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { throw "codex CLI not found" }
codex exec --sandbox workspace-write '$archqed-implement Implement exactly one next approved ArchQED backend task, submit implemented_unverified, and delegate final verification.'
exit $LASTEXITCODE
