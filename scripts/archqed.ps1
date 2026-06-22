$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = if ($env:ARCHQED_PYTHON) { $env:ARCHQED_PYTHON } else { "python" }
$VendoredRuntime = Join-Path $Root ".archqed/runtime"
$SourceRuntime = Join-Path $Root "src"
if (Test-Path (Join-Path $VendoredRuntime "archqed")) { $Runtime = $VendoredRuntime }
elseif (Test-Path (Join-Path $SourceRuntime "archqed")) { $Runtime = $SourceRuntime }
else { throw "ArchQED runtime not found. Re-run the bootstrap protocol." }
if ($env:PYTHONPATH) { $env:PYTHONPATH = "$Runtime;$env:PYTHONPATH" } else { $env:PYTHONPATH = $Runtime }
& $Python -m archqed --root $Root @args
exit $LASTEXITCODE
