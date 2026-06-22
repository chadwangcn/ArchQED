# Evidence model

An agent completion message is not proof. Evidence records task ID, accepted source revision, task-contract hash, timestamp, every acceptance command, exit code, bounded stdout/stderr, timeout state, forbidden findings, and final result.

Evidence is stored under `.ai-control/evidence/TASK-ID/EVD-*.json`.

`archqed verify TASK-ID` refuses to run when source drift exists, control is not ready, task is not `implemented_unverified`, or no executable acceptance exists. It sets `verified` only when all commands pass and scans are clean.

Acceptance commands are project-controlled shell commands and should be reviewed like CI configuration.
