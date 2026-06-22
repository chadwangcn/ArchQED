param(
  [string]$Target = (Get-Location).Path,
  [ValidateSet("discovery", "stabilizing", "delivery")][string]$Stage = "discovery",
  [string]$Adapter,
  [switch]$AllowMismatch
)
$ErrorActionPreference = "Stop"
$Source = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = if ($env:ARCHQED_PYTHON) { $env:ARCHQED_PYTHON } else { "python" }
& $Python (Join-Path $Source "scripts/verify-release.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$env:PYTHONPATH = if ($env:PYTHONPATH) { "$Source/src;$env:PYTHONPATH" } else { "$Source/src" }
$ArgsList = @("-m", "archqed", "bootstrap", "--target", $Target, "--stage", $Stage)
if ($Adapter) { $ArgsList += @("--adapter", $Adapter) }
if ($AllowMismatch) { $ArgsList += "--allow-mismatch" }
& $Python @ArgsList
exit $LASTEXITCODE
