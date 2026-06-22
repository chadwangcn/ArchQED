---
name: archqed-compile
description: Compile changed architecture or feature-detail documents into ArchQED contracts, traceability, tasks, gaps, and acceptance criteria. Use whenever status reports drift, awaiting approval, needs_compile, needs_recompile, or requires_revalidation. Do not use this skill to write product code.
---

# ArchQED Compile

1. Run `archqed status --json`; when drift exists, run `archqed sync` once.
2. Read the current change under `.ai-control/changes/`.
3. If it is `awaiting_approval`, stop and ask the human to run `archqed approve-change CHANGE-ID`. Never self-approve.
4. Read changed human documents and stable `ARCH-*`, `REQ-*`, `ADR-*`, `API-*`, `DATA-*`, and `AGENT-*` IDs.
5. Update generated contracts and traceability. Never edit human source documents to match existing code.
6. Generate small JSON tasks. Every task needs source refs, dependencies, requirements, executable acceptance commands, and forbidden shortcuts.
7. Missing defaults, sources, failure rules, consistency rules, or external behavior become gap files and `needs_clarification`. Never guess.
8. Preserve unaffected verified tasks for scoped feature changes. When traceability is uncertain, keep the broader impact.
9. Run `archqed doctor`, fix control-data errors, then run `archqed compile-complete CHANGE-ID`.
10. Report impact, affected tasks, gaps, and final control state. Do not write product code.
