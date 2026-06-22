# Backend adapter model

Adapters are project-tool descriptions, not business architecture plugins.

A probe returns candidates with marker evidence, score, suggested commands, notes, and ambiguity state. Selection is automatic only when it is unambiguous. The generic adapter supports all other backends through explicit commands.

Commands are stored in `.archqed/project.json` with a source of `detected` or `human`. Human commands survive upgrades and re-probing. ArchQED never creates dependency-manifest entries or build targets during detection.
