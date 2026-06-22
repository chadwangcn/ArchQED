# Generic backend adapter example

Use this pattern when the backend is not recognized by a built-in adapter:

```bash
./scripts/archqed adapter configure generic \
  --command 'unit_test=./tools/test-unit.sh' \
  --command 'integration_test=./tools/test-integration.sh' \
  --command 'build=./tools/build.sh'
```

ArchQED records these as human-reviewed commands and preserves them across upgrades.
