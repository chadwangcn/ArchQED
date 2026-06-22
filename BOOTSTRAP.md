# ArchQED One-Link Bootstrap Protocol

**Protocol version:** 0.2  
**Channel:** `stable`  
**Scope:** any backend project root, independent of language, framework, or business project

This is the permanent public entry point for coding agents:

```text
https://raw.githubusercontent.com/chadwangcn/ArchQED/main/BOOTSTRAP.md
```

The URL intentionally has no release number. This document resolves the current stable release through:

```text
https://raw.githubusercontent.com/chadwangcn/ArchQED/main/stable.json
```

`stable.json` contains an immutable Git commit. The coding agent must install that exact commit rather than execute the moving `main` branch.

A coding agent that can read public GitHub content, run terminal commands, and write the current repository must follow the protocol below.

## Non-negotiable rules

1. Treat the current repository as the target backend project. Do not assume any project name, domain, framework, or architecture.
2. Do not modify product code, tests, architecture meaning, dependency manifests, or build configuration during installation.
3. Do not guess the backend adapter or project commands when detection is ambiguous.
4. Use `main` only to read this protocol and `stable.json`; install the exact commit declared by `stable.json`.
5. Do not report success until `doctor` passes and a bootstrap evidence file exists.
6. Preserve existing `AGENTS.md` content and existing `.codex/config.toml`.
7. Stop and report a precise blocker when Git, Python 3.11+, network access, or repository write access is unavailable.

## Required capabilities

- Read public HTTPS URLs or clone a public GitHub repository.
- Execute Git and shell or PowerShell commands.
- Execute Python 3.11 or newer. This is the ArchQED runtime requirement; the target backend may use any stack.
- Write files inside the target repository.

## POSIX installation

Run from anywhere inside the target repository:

```bash
set -euo pipefail
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ARCHQED_TMP="$(mktemp -d)"
trap 'rm -rf "$ARCHQED_TMP"' EXIT

git clone --depth 1 \
  https://github.com/chadwangcn/ArchQED.git \
  "$ARCHQED_TMP/ArchQED"

ARCHQED_COMMIT="$(
  python3 - "$ARCHQED_TMP/ArchQED/stable.json" <<'PY'
import json
import pathlib
import sys

value = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
commit = value.get("commit")
if not isinstance(commit, str) or len(commit) != 40:
    raise SystemExit("stable.json does not contain a valid immutable commit")
print(commit)
PY
)"

git -C "$ARCHQED_TMP/ArchQED" fetch --depth 1 origin "$ARCHQED_COMMIT"
git -C "$ARCHQED_TMP/ArchQED" checkout --detach "$ARCHQED_COMMIT"

"$ARCHQED_TMP/ArchQED/scripts/bootstrap.sh" "$PROJECT_ROOT"
"$PROJECT_ROOT/scripts/archqed" doctor --json
"$PROJECT_ROOT/scripts/archqed" status --json
```

## PowerShell installation

Run from anywhere inside the target repository:

```powershell
$ErrorActionPreference = "Stop"
$ProjectRoot = (git rev-parse --show-toplevel 2>$null)
if (-not $ProjectRoot) { $ProjectRoot = (Get-Location).Path }
$ArchQEDTemp = Join-Path ([System.IO.Path]::GetTempPath()) ("archqed-" + [guid]::NewGuid())

git clone --depth 1 `
  https://github.com/chadwangcn/ArchQED.git `
  $ArchQEDTemp

$Stable = Get-Content (Join-Path $ArchQEDTemp "stable.json") -Raw | ConvertFrom-Json
$ArchQEDCommit = [string]$Stable.commit
if ($ArchQEDCommit -notmatch '^[0-9a-f]{40}$') {
  throw "stable.json does not contain a valid immutable commit"
}

git -C $ArchQEDTemp fetch --depth 1 origin $ArchQEDCommit
git -C $ArchQEDTemp checkout --detach $ArchQEDCommit

& "$ArchQEDTemp/scripts/bootstrap.ps1" -Target $ProjectRoot
& "$ProjectRoot/scripts/archqed.ps1" doctor --json
& "$ProjectRoot/scripts/archqed.ps1" status --json
Remove-Item -Recurse -Force $ArchQEDTemp
```

## Adapter ambiguity

When bootstrap exits with code 4 and reports ambiguous detection:

1. Read `.archqed/probe.json`.
2. Present the candidate adapters and evidence to the human.
3. Do not select one silently.
4. Re-run the already checked-out stable installer with the approved adapter:

```bash
"$ARCHQED_TMP/ArchQED/scripts/bootstrap.sh" "$PROJECT_ROOT" --adapter python
```

Available built-in adapters can be listed after installation:

```bash
./scripts/archqed adapter list
```

## Unsupported or custom backend

ArchQED falls back to the `generic` adapter. It installs successfully but does not invent build or test commands. Configure reviewed project commands explicitly:

```bash
./scripts/archqed adapter configure generic \
  --command 'unit_test=make test' \
  --command 'integration_test=make integration-test' \
  --command 'build=make build'

./scripts/archqed check --only unit_test --only build
```

## Required post-install evidence

The agent must verify all of the following:

```text
scripts/archqed or scripts/archqed.ps1 exists
.archqed/runtime/archqed exists
.archqed/project.json exists
.ai-control/manifest.json exists
.agents/skills/archqed-compile/SKILL.md exists
.agents/skills/archqed-implement/SKILL.md exists
.agents/skills/archqed-verify/SKILL.md exists
.codex/agents/archqed-verifier.toml exists
```

The bootstrap command writes evidence under:

```text
.ai-control/evidence/bootstrap/EVD-BOOTSTRAP-*.json
```

The final agent response must include:

- target repository path;
- resolved stable version and immutable commit;
- selected adapter and whether it was automatic or human-approved;
- exact commands executed;
- `doctor` result;
- bootstrap evidence path;
- any command configuration still required.

## After installation

Codex automatically reads the managed `AGENTS.md`, discovers the three repository skills, and can use the project-scoped agents. Deterministic entry points are:

```bash
./scripts/codex-sync.sh
./scripts/codex-next.sh
./scripts/codex-verify.sh TASK-ID
```

Other coding agents may follow the same `AGENTS.md`, Skill documents, `.archqed/project.json`, and CLI lifecycle even if they do not implement Codex Skill discovery.
