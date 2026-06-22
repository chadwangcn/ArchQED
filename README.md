# ArchQED · 构证

**Human architecture. Machine contracts. Verified software.**

ArchQED is a project-neutral protocol, self-contained CLI, and coding-agent skill suite for any backend repository. It compiles human-readable architecture into controlled implementation tasks and accepts only evidence-backed completion.

> **No evidence, no done.**

[中文说明](README.zh-CN.md) · [One-link bootstrap](BOOTSTRAP.md)

## Give a coding agent one permanent link

```text
Read and execute this protocol in the current backend repository:
https://raw.githubusercontent.com/chadwangcn/ArchQED/main/BOOTSTRAP.md
```

The public entry URL has no version number. `BOOTSTRAP.md` reads `stable.json`, resolves the current stable release to an immutable Git commit, checks out that exact commit, installs a vendored ArchQED runtime and skills, initializes the control plane, runs `doctor`, and returns bootstrap evidence.

The target backend project does not need to use Python. Only the ArchQED runtime requires Python 3.11+.

## v0.2.0 — One-Link Bootstrap

- Permanent, model-neutral bootstrap URL.
- Stable-channel metadata resolved to an immutable Git commit.
- Idempotent `archqed bootstrap` and safe `archqed uninstall`.
- Self-contained runtime under `.archqed/runtime/`.
- Backend probing with evidence and ambiguity blocking.
- Built-in adapters for Python, Node.js, Maven, Gradle, Go, .NET, Rust, PHP, and Ruby.
- `generic` adapter for every other backend with human-reviewed commands.
- Project command evidence through `archqed check`.
- POSIX and PowerShell launchers.
- Existing `AGENTS.md` and `.codex/config.toml` preservation.
- No coupling to any business project.

## Manual installation

Give the coding agent the permanent link above, or follow [BOOTSTRAP.md](BOOTSTRAP.md) manually. The protocol clones the public repository, resolves `stable.json`, and checks out the declared immutable commit before installation.

## Installed project workflow

```bash
./scripts/archqed doctor
./scripts/archqed status

$EDITOR docs/architecture/system.md
$EDITOR docs/features/story-generation.md

./scripts/archqed sync
./scripts/codex-sync.sh
./scripts/codex-next.sh
./scripts/codex-verify.sh TASK-ID
```

## Adapter behavior

ArchQED detects marker files and only records commands supported by project evidence. A multi-stack repository is blocked when the selection is ambiguous. Unknown stacks use `generic` and require explicit commands:

```bash
./scripts/archqed adapter configure generic \
  --command 'unit_test=make test' \
  --command 'build=make build'
```

## Core commands

```text
archqed bootstrap --target PATH [--adapter ID]
archqed probe --target PATH
archqed adapter list|detect|configure
archqed check [--only NAME]
archqed uninstall [--purge-control-data]
archqed init
archqed sync [--check]
archqed status
archqed doctor
archqed approve-change CHANGE-ID
archqed compile-complete CHANGE-ID
archqed task list|next|start|submit|transition
archqed verify TASK-ID
```

See [Chinese quickstart](docs/zh-CN/quickstart.md), [adapter guide](docs/zh-CN/adapters.md), [one-link guide](docs/zh-CN/one-link-bootstrap.md), and [CLI reference](docs/reference/cli.md).

## Verify this repository

```bash
./scripts/verify.sh
```

## License

Apache License 2.0.
