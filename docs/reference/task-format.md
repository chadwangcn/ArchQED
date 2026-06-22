# Task file format

Tasks are JSON under `.ai-control/tasks/`.

```json
{
  "id": "TASK-STORY-014",
  "title": "Persist and read back generated story",
  "status": "approved",
  "source_refs": ["ARCH-CONTENT-001", "REQ-STORY-014"],
  "dependencies": [],
  "acceptance": [{"id": "AC-1", "command": "pytest -q tests/integration/test_story.py"}],
  "forbidden": [{"id": "no-placeholder", "pattern": "(?i)placeholder|hardcoded_story", "paths": ["src"]}]
}
```

Required fields are `id`, `title`, `status`, `source_refs`, `dependencies`, `acceptance`, and `forbidden`.
