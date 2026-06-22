---
name: archqed-implement
description: Implement exactly one approved ArchQED task with real integrations and executable acceptance checks. Use for product-code work only when the control state is ready. Never self-verify or modify human architecture.
---

# ArchQED Implement

1. Run `archqed sync --check` and `archqed status --json`; stop unless control state is `ready`.
2. Run `archqed task next --json`. If no task is ready, do not invent work.
3. Select exactly one task and read its source refs, contracts, dependencies, and existing implementation.
4. Ambiguity means `needs_clarification` and a precise gap; never invent defaults or data sources.
5. Run `archqed task start TASK-ID`.
6. Add tests that exercise the real path, then implement the smallest complete vertical slice.
7. Connect UI to real API, API to real service/repository, and persistence/external calls to documented sources.
8. Do not use production mocks, placeholders, hardcoded success, silent fallback, or TODO-only behavior.
9. Run declared acceptance and relevant project checks. Never weaken acceptance to fit broken code.
10. Run `archqed task submit TASK-ID`; the state must be `implemented_unverified`.
11. Delegate final verification to the project-scoped `archqed_verifier`. Never set `verified` yourself.
