---
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
