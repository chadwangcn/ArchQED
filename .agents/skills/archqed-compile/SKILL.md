---
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
