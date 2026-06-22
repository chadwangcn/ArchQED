# ArchQED · 构证

**Human architecture. Machine contracts. Verified software.**

ArchQED is an open protocol, deterministic Python CLI, and Codex skill suite that turns human-readable architecture into controlled implementation tasks and accepts only evidence-backed completion.

> **No evidence, no done.**

[中文说明](README.zh-CN.md)

## Why

Coding agents can report success after producing placeholders, mock-only paths, silent defaults, disconnected layers, or tests that never exercise the real system. ArchQED places them inside an auditable lifecycle:

```text
human architecture and feature details
                ↓
change detection, impact, and approval
                ↓
contracts, tasks, gaps, and acceptance criteria
                ↓
implementation agent
                ↓
independent verifier
                ↓
evidence-backed task state
```

## What v0.1.0 includes

- `discovery`, `stabilizing`, and `delivery` change stages.
- Repeated-edit superseding, revert handling, and stale-approval protection.
- Global architecture impact and stable-ID-scoped feature refinement.
- A task state machine that prevents implementation agents from setting `verified`.
- Executable acceptance commands, forbidden-pattern scans, and evidence bundles.
- Three repository-scoped Codex skills under `.agents/skills/`.
- Three project-scoped Codex agents under `.codex/agents/`.
- Chinese documentation for each workflow stage.
- A Python 3.11+ CLI with no runtime dependencies.

## Install

```bash
git clone https://github.com/chadwangcn/ArchQED.git
cd ArchQED
python -m pip install .
./scripts/verify.sh
```

Install ArchQED into an existing project:

```bash
./scripts/install-project.sh /path/to/project discovery
```

## First lifecycle

```bash
cd /path/to/project
$EDITOR docs/architecture/system.md
$EDITOR docs/features/story-generation.md
archqed sync
./scripts/codex-sync.sh
./scripts/codex-next.sh
archqed status
```

## Change stages

| Stage | Architecture changes | Feature-detail changes |
|---|---|---|
| `discovery` | Global recompile; approval off by default | Global recompile |
| `stabilizing` | Human approval and global impact | Scoped by stable IDs |
| `delivery` | Human approval and global impact | Human approval and scoped revalidation |

## Codex integration

Codex reads `AGENTS.md`, discovers repository skills under `.agents/skills/`, and project agents under `.codex/agents/`. The wrappers use explicit skill invocation:

```bash
./scripts/codex-sync.sh
./scripts/codex-next.sh
./scripts/codex-verify.sh TASK-ID
```

## Core commands

```text
archqed init
archqed sync [--check]
archqed status
archqed doctor
archqed set-stage STAGE
archqed approve-change CHANGE-ID
archqed compile-complete CHANGE-ID
archqed task list|next|start|submit|transition
archqed verify TASK-ID
```

See the [Chinese quickstart](docs/zh-CN/quickstart.md), [change model](docs/protocol/change-model.md), [evidence model](docs/protocol/evidence-model.md), and [CLI reference](docs/reference/cli.md).

## Status

ArchQED v0.1.0 is an alpha protocol and working reference implementation. Control-data formats may evolve before v1.0.

## License

Apache License 2.0.
