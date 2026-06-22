# Task file format

Tasks are JSON files under `.ai-control/tasks/`.

```json
{
  "id": "TASK-STORY-014",
  "title": "Persist and read back generated story",
  "status": "approved",
  "priority": 10,
  "source_refs": ["ARCH-CONTENT-001", "REQ-STORY-014"],
  "dependencies": [],
  "requirements": [
    "Read the real profile",
    "Persist the generated story",
    "Read it back by content ID"
  ],
  "acceptance": [
    {
      "id": "AC-1",
      "command": "./scripts/test-story-integration.sh",
      "timeout_seconds": 300
    }
  ],
  "forbidden": [
    {
      "id": "no-placeholder",
      "pattern": "(?i)placeholder|hardcoded_story",
      "paths": ["src"]
    }
  ]
}
```

Required fields are `id`, `title`, `status`, `source_refs`, `dependencies`, `acceptance`, and `forbidden`.

Acceptance commands are repository-controlled executable contracts. They must be reviewed with the same care as CI configuration.
