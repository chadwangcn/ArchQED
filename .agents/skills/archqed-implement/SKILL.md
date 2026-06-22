---
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
