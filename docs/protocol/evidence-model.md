# Evidence model

An agent completion message is not proof.

Task evidence records task ID, accepted source revision, task-contract hash, timestamp, every acceptance command, exit code, bounded output, timeout state, forbidden findings, and final result.

Project-check evidence records the selected project configuration hash and every executed adapter command.

Bootstrap evidence records ArchQED version, target, adapter choice, probe hash, managed-file hashes, and `doctor` result.

Evidence locations:

```text
.ai-control/evidence/TASK-ID/EVD-*.json
.ai-control/evidence/project-check/EVD-PROJECT-CHECK-*.json
.ai-control/evidence/bootstrap/EVD-BOOTSTRAP-*.json
```
