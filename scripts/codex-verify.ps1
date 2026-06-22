param([Parameter(Mandatory=$true)][string]$TaskId)
$ErrorActionPreference = "Stop"
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { throw "codex CLI not found" }
codex exec --sandbox workspace-write "`$archqed-verify Independently verify $TaskId. Do not change product code, tests, human documents, or requirements."
exit $LASTEXITCODE
