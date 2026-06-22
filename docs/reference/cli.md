# CLI reference

```text
archqed init --name PROJECT --stage STAGE
archqed sync [--check]
archqed status
archqed doctor
archqed set-stage discovery|stabilizing|delivery
archqed approve-change CHANGE-ID
archqed compile-complete CHANGE-ID
archqed task list
archqed task next
archqed task start TASK-ID
archqed task submit TASK-ID
archqed task transition TASK-ID --to STATUS
archqed verify TASK-ID
```

All commands accept `--root PATH` before the subcommand and `--json` for automation.

Exit codes: 0 success, 2 invalid data, 3 drift, 4 lifecycle gate blocked, 5 verification failed, 130 interrupted.
