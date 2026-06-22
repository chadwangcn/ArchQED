# ArchQED · 构证

**Human architecture. Machine contracts. Verified software.**

ArchQED is an open protocol, deterministic CLI, and Codex skill suite for turning human-readable architecture into controlled implementation tasks and accepting only evidence-backed completion.

> No evidence, no done.

[中文说明](README.zh-CN.md)

## Why

Coding agents often report success after producing interfaces, placeholders, mock-only paths, silent defaults, or tests that never exercise the real system. More prompting does not solve this reliably. ArchQED places the agent inside an auditable lifecycle:

```text
human architecture
      ↓
change detection and approval
      ↓
generated contracts, tasks, and acceptance criteria
      ↓
implementation agent
      ↓
independent verifier
      ↓
evidence-backed task state
```

## What v0.1 provides

- Human architecture and feature-detail documents remain the source of intent.
- SHA-256 source drift detection and recorded change sets.
- Three volatility stages: `discovery`, `stabilizing`, and `delivery`.
- Global architecture impact and scoped feature-refinement impact.
- Human approval gates where the stage requires them.
- A task state machine that prevents implementation agents from setting `verified`.
- Executable acceptance commands and evidence bundles.
- Three repository-scoped Codex skills: compile, implement, and verify.
- Project-scoped Codex custom agents and one-command workflow wrappers.
- A zero-runtime-dependency Python CLI.

## Install

Python 3.11 or newer is required.

```bash
git clone https://github.com/chadwangcn/ArchQED.git
cd ArchQED
python -m pip install .
```

Install ArchQED into an existing project:

```bash
./scripts/install-project.sh /path/to/your-project discovery
```

The installer keeps existing project files where possible, adds repository-scoped skills under `.agents/skills/`, adds project-scoped agents under `.codex/agents/`, initializes the control plane, and merges an ArchQED section into `AGENTS.md`.

## First lifecycle

```bash
cd /path/to/your-project

# 1. Continue writing architecture for people.
$EDITOR docs/architecture/system.md
$EDITOR docs/features/story-generation.md

# 2. Record source drift.
python -m archqed sync

# 3. Let Codex compile contracts and tasks.
./scripts/codex-sync.sh

# 4. Let Codex implement one approved task and request independent verification.
./scripts/codex-next.sh

# 5. Inspect truth rather than claims.
python -m archqed status
```

## Change stages

| Stage | Architecture changes | Feature-detail changes | Typical use |
|---|---|---|---|
| `discovery` | No approval by default; global recompile | Global recompile | Early design churn |
| `stabilizing` | Human approval; global impact | Scoped by stable IDs | Architecture mostly stable, behavior still moving |
| `delivery` | Human approval; migration-aware | Human approval and scoped revalidation | Release and production hardening |

Change stage explicitly:

```bash
python -m archqed set-stage stabilizing
```

## Automatic Codex use

Codex reads repository `AGENTS.md` before work and discovers repository skills under `.agents/skills`. The supplied skill descriptions allow implicit matching, while the wrappers use explicit `$archqed-*` invocation for predictable automation.

```bash
./scripts/codex-sync.sh   # compile architecture or feature changes
./scripts/codex-next.sh   # implement one task, then spawn verifier
```

Subagents are explicitly requested by the implementation workflow. The project-scoped `archqed_verifier` is instructed not to repair code or weaken tests.

## Core commands

```text
archqed init
archqed sync [--check]
archqed status
archqed doctor
archqed approve-change CHANGE-ID
archqed compile-complete CHANGE-ID
archqed set-stage STAGE
archqed task list|next|start|submit|transition|reconcile
archqed verify TASK-ID
```

See [CLI reference](docs/reference/cli.md), [change model](docs/protocol/change-model.md), and the [Chinese operating guide](docs/zh-CN/quickstart.md).

## Repository verification

```bash
./scripts/verify.sh
```

The repository test suite covers baseline compilation, architecture approval, scoped feature impact, drift blocking, task transitions, anti-fake findings, and evidence-backed verification.

## Status

ArchQED v0.1.0 is an alpha protocol and working reference implementation. File formats may evolve before v1.0; schema versions and migration notes will accompany changes.

## License

Apache License 2.0.
