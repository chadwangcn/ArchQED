# Project adapter configuration

`.archqed/project.json` describes the target backend toolchain.

```json
{
  "schema_version": "0.2",
  "archqed_version": "0.2.0",
  "adapter": {
    "id": "go",
    "label": "Go",
    "selected_by": "auto",
    "score": 80,
    "evidence": ["go.mod"],
    "notes": []
  },
  "commands": {
    "lint": {
      "command": "go vet ./...",
      "source": "detected",
      "enabled": true
    },
    "unit_test": {
      "command": "go test ./...",
      "source": "detected",
      "enabled": true
    }
  },
  "requires_command_configuration": false
}
```

A command with source `human` is preserved by later bootstrap runs. Secrets must not be placed directly in commands; use the repository's normal environment configuration.
