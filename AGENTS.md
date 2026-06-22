# ArchQED managed instructions

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
