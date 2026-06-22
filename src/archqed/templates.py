from __future__ import annotations

AGENTS_BLOCK = """# ArchQED managed instructions

- Human intent lives in `docs/architecture/` and `docs/features/`.
- Generated control data lives in `.ai-control/`; it is not the human design source.
- Before product work, run `./scripts/archqed sync --check` and `./scripts/archqed status --json`.
- When source drift or a non-ready state exists, use `$archqed-compile`.
- Implement exactly one approved task with `$archqed-implement`.
- The implementation agent may only submit `implemented_unverified`.
- Use a separate `archqed_verifier` agent and `$archqed-verify` for final acceptance.
- Read `.archqed/project.json` for the selected backend adapter and project commands.
- Never invent missing defaults, data sources, failure behavior, build commands, or fallbacks.
- Never weaken acceptance tests to make an implementation pass.
- No evidence, no done.
"""

COMPILE_SKILL = """---
name: archqed-compile
description: Compile changed backend architecture or feature-detail documents into ArchQED contracts, traceability, tasks, gaps, and acceptance criteria. Use whenever status reports drift, awaiting approval, needs_compile, needs_recompile, or requires_revalidation. Do not write product code.
---

# ArchQED Compile

1. Run `./scripts/archqed status --json`; when drift exists, run `./scripts/archqed sync` once.
2. Read `.archqed/project.json` and the current change under `.ai-control/changes/`.
3. If the change is `awaiting_approval`, stop and ask a human to approve it. Never self-approve.
4. Read changed human documents and stable `ARCH-*`, `REQ-*`, `ADR-*`, `API-*`, `DATA-*`, and `AGENT-*` IDs.
5. Update generated contracts and traceability. Never edit human source documents to match existing code.
6. Generate small JSON tasks with source refs, dependencies, requirements, executable acceptance commands, and forbidden shortcuts.
7. Use project commands from `.archqed/project.json`; do not invent commands when the adapter is generic or ambiguous.
8. Missing defaults, sources, failure rules, consistency rules, external behavior, or verification commands become blocking gaps.
9. Preserve unaffected verified tasks for scoped feature changes. When traceability is uncertain, keep the broader impact.
10. Run `./scripts/archqed doctor`, then `./scripts/archqed compile-complete CHANGE-ID` only when valid.
"""

IMPLEMENT_SKILL = """---
name: archqed-implement
description: Implement exactly one approved ArchQED task in any backend stack, using the selected project adapter, real integrations, and executable acceptance checks. Use only when the control state is ready. Never self-verify or modify human architecture.
---

# ArchQED Implement

1. Run `./scripts/archqed sync --check` and `./scripts/archqed status --json`; stop unless control state is `ready`.
2. Read `.archqed/project.json` and run `./scripts/archqed task next --json`.
3. Select exactly one task and read its source refs, contracts, dependencies, and current implementation.
4. Ambiguity means `needs_clarification`; never invent defaults, data sources, or framework commands.
5. Run `./scripts/archqed task start TASK-ID`.
6. Add tests that exercise the real path, then implement the smallest complete vertical slice.
7. Connect transport to real service/repository code and documented persistence, queue, storage, or external services.
8. Do not use production mocks, placeholders, hardcoded success, silent fallback, or TODO-only behavior.
9. Run the task acceptance commands and relevant enabled commands from `.archqed/project.json`.
10. Never weaken acceptance to fit broken code.
11. Run `./scripts/archqed task submit TASK-ID`; the state must be `implemented_unverified`.
12. Delegate final verification to `archqed_verifier`. Never set `verified` yourself.
"""

VERIFY_SKILL = """---
name: archqed-verify
description: Independently verify an implemented_unverified ArchQED backend task by tracing real execution paths, running acceptance commands, scanning forbidden shortcuts, and preserving evidence. Do not repair code or weaken tests.
---

# ArchQED Verify

1. Run `./scripts/archqed sync --check` and confirm control state is `ready`.
2. Read `.archqed/project.json`, the task, source refs, generated contracts, and implementation diff.
3. Trace the real path from entry point through service/repository code to storage, queue, model provider, or documented dependency.
4. Look for disconnected layers, mock-only paths, hardcoded responses, silent defaults, and success without side effects.
5. Do not edit product code, human docs, task requirements, acceptance commands, or forbidden rules.
6. Run `./scripts/archqed verify TASK-ID`.
7. Read the evidence bundle and report failures with reproduction commands.
8. A failed task stays `implemented_unverified`; do not fix it in verifier role.
"""

OPENAI_SKILL_YAML = {
    "archqed-compile": """interface:\n  display_name: \"ArchQED Compile\"\n  short_description: \"Compile backend architecture into controlled tasks\"\n  default_prompt: \"Reconcile current ArchQED changes without writing product code.\"\npolicy:\n  allow_implicit_invocation: true\n""",
    "archqed-implement": """interface:\n  display_name: \"ArchQED Implement\"\n  short_description: \"Implement one approved backend task without self-verification\"\n  default_prompt: \"Implement one next approved ArchQED task and submit it for verification.\"\npolicy:\n  allow_implicit_invocation: true\n""",
    "archqed-verify": """interface:\n  display_name: \"ArchQED Verify\"\n  short_description: \"Independently prove or reject backend task completion\"\n  default_prompt: \"Verify the specified ArchQED task without changing implementation or tests.\"\npolicy:\n  allow_implicit_invocation: true\n""",
}

AGENT_CONFIGS = {
    ".codex/agents/archqed-compiler.toml": """name = \"archqed_compiler\"\ndescription = \"Backend architecture compiler that updates ArchQED control data but never writes product code or self-approves.\"\nmodel_reasoning_effort = \"high\"\nsandbox_mode = \"workspace-write\"\ndeveloper_instructions = \"\"\"\nUse archqed-compile. Read .archqed/project.json. Treat human documents as intent. Do not write product code, self-approve, or guess missing decisions or project commands.\n\"\"\"\nnickname_candidates = [\"Euclid\", \"Compiler\", \"Cartographer\"]\n""",
    ".codex/agents/archqed-implementer.toml": """name = \"archqed_implementer\"\ndescription = \"Backend implementation agent that owns exactly one approved ArchQED task and may only submit implemented_unverified.\"\nmodel_reasoning_effort = \"high\"\nsandbox_mode = \"workspace-write\"\ndeveloper_instructions = \"\"\"\nUse archqed-implement and the adapter in .archqed/project.json. Implement one approved task with real integrations. Never invent defaults or commands, use production placeholders, weaken acceptance, or mark verified.\n\"\"\"\nnickname_candidates = [\"Builder\", \"Turing\", \"Forge\"]\n""",
    ".codex/agents/archqed-verifier.toml": """name = \"archqed_verifier\"\ndescription = \"Independent backend verifier focused on real execution paths, anti-fake findings, and reproducible evidence.\"\nmodel_reasoning_effort = \"high\"\nsandbox_mode = \"workspace-write\"\ndeveloper_instructions = \"\"\"\nUse archqed-verify. Read .archqed/project.json. Do not repair product code, alter tests, human docs, or requirements. Failed verification must remain failed.\n\"\"\"\nnickname_candidates = [\"QED\", \"Verifier\", \"Gauss\"]\n""",
}

ARCHQED_WRAPPER = r'''#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ARCHQED_PYTHON:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "ArchQED requires Python 3.11+; set ARCHQED_PYTHON to a compatible interpreter." >&2
  exit 127
fi
if [[ -d "$ROOT/.archqed/runtime/archqed" ]]; then
  ARCHQED_RUNTIME="$ROOT/.archqed/runtime"
elif [[ -d "$ROOT/src/archqed" ]]; then
  ARCHQED_RUNTIME="$ROOT/src"
else
  echo "ArchQED runtime not found. Re-run the bootstrap protocol." >&2
  exit 4
fi
export PYTHONPATH="$ARCHQED_RUNTIME${PYTHONPATH:+:$PYTHONPATH}"
exec "$PYTHON_BIN" -m archqed --root "$ROOT" "$@"
'''

ARCHQED_WRAPPER_PS1 = r'''$ErrorActionPreference = "Stop"
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
'''

CODEX_SYNC_SH = r'''#!/usr/bin/env bash
set -euo pipefail
command -v codex >/dev/null 2>&1 || { echo "codex CLI not found" >&2; exit 127; }
exec codex exec --sandbox workspace-write '$archqed-compile Reconcile current backend architecture and feature-detail changes. Read .archqed/project.json. Update generated control data only, respect approval gates, create gaps instead of guessing, run doctor, and close compilation only when valid.'
'''

CODEX_NEXT_SH = r'''#!/usr/bin/env bash
set -euo pipefail
command -v codex >/dev/null 2>&1 || { echo "codex CLI not found" >&2; exit 127; }
exec codex exec --sandbox workspace-write '$archqed-implement Implement exactly one next approved ArchQED backend task. Use the selected adapter and real integrations, run declared checks, submit implemented_unverified, and delegate final verification to archqed_verifier. Never self-verify.'
'''

CODEX_VERIFY_SH = r'''#!/usr/bin/env bash
set -euo pipefail
TASK_ID="${1:?usage: scripts/codex-verify.sh TASK-ID}"
command -v codex >/dev/null 2>&1 || { echo "codex CLI not found" >&2; exit 127; }
exec codex exec --sandbox workspace-write "\$archqed-verify Independently verify ${TASK_ID}. Read .archqed/project.json. Do not change product code, tests, human documents, or task requirements. Run ./scripts/archqed verify ${TASK_ID} and inspect evidence."
'''

CODEX_SYNC_PS1 = r'''$ErrorActionPreference = "Stop"
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { throw "codex CLI not found" }
codex exec --sandbox workspace-write '$archqed-compile Reconcile current backend architecture and feature-detail changes. Read .archqed/project.json. Update generated control data only and never guess.'
exit $LASTEXITCODE
'''

CODEX_NEXT_PS1 = r'''$ErrorActionPreference = "Stop"
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { throw "codex CLI not found" }
codex exec --sandbox workspace-write '$archqed-implement Implement exactly one next approved ArchQED backend task, submit implemented_unverified, and delegate final verification.'
exit $LASTEXITCODE
'''

CODEX_VERIFY_PS1 = r'''param([Parameter(Mandatory=$true)][string]$TaskId)
$ErrorActionPreference = "Stop"
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { throw "codex CLI not found" }
codex exec --sandbox workspace-write "`$archqed-verify Independently verify $TaskId. Do not change product code, tests, human documents, or requirements."
exit $LASTEXITCODE
'''

MANAGED_FILES = {
    ".agents/skills/archqed-compile/SKILL.md": COMPILE_SKILL,
    ".agents/skills/archqed-implement/SKILL.md": IMPLEMENT_SKILL,
    ".agents/skills/archqed-verify/SKILL.md": VERIFY_SKILL,
    ".agents/skills/archqed-compile/agents/openai.yaml": OPENAI_SKILL_YAML["archqed-compile"],
    ".agents/skills/archqed-implement/agents/openai.yaml": OPENAI_SKILL_YAML["archqed-implement"],
    ".agents/skills/archqed-verify/agents/openai.yaml": OPENAI_SKILL_YAML["archqed-verify"],
    **AGENT_CONFIGS,
    "scripts/archqed": ARCHQED_WRAPPER,
    "scripts/archqed.ps1": ARCHQED_WRAPPER_PS1,
    "scripts/codex-sync.sh": CODEX_SYNC_SH,
    "scripts/codex-next.sh": CODEX_NEXT_SH,
    "scripts/codex-verify.sh": CODEX_VERIFY_SH,
    "scripts/codex-sync.ps1": CODEX_SYNC_PS1,
    "scripts/codex-next.ps1": CODEX_NEXT_PS1,
    "scripts/codex-verify.ps1": CODEX_VERIFY_PS1,
}

EXECUTABLE_FILES = {
    "scripts/archqed",
    "scripts/codex-sync.sh",
    "scripts/codex-next.sh",
    "scripts/codex-verify.sh",
}
