# CLI reference

## Bootstrap and adapters

```text
archqed bootstrap --target PATH [--stage STAGE] [--adapter ID] [--allow-mismatch]
archqed uninstall --target PATH [--purge-control-data]
archqed probe --target PATH
archqed adapter list
archqed adapter detect --target PATH
archqed adapter configure [ADAPTER-ID] --target PATH --command NAME=COMMAND
archqed check [--only NAME] [--include-install]
```

`bootstrap` is idempotent and installs a vendored runtime. Adapter ambiguity exits with code 4 and writes `.archqed/probe.json`.

Supported command names:

```text
install
lint
typecheck
unit_test
integration_test
build
smoke_test
```

## Architecture lifecycle

```text
archqed init --name PROJECT --stage discovery|stabilizing|delivery
archqed sync [--check]
archqed status
archqed doctor
archqed set-stage discovery|stabilizing|delivery
archqed approve-change CHANGE-ID
archqed compile-complete CHANGE-ID
```

## Task lifecycle

```text
archqed task list
archqed task next
archqed task start TASK-ID
archqed task submit TASK-ID
archqed task transition TASK-ID --to STATUS
archqed verify TASK-ID
```

## Common options

`--root PATH` may appear before the subcommand. `--json` may appear before or after the subcommand.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 2 | invalid data or environment |
| 3 | unrecorded architecture drift |
| 4 | lifecycle gate or adapter selection blocked |
| 5 | verification/project check failed |
| 130 | interrupted |
