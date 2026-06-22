# Task state machine

```text
draft → approved → in_progress → implemented_unverified → verified
  ├→ needs_clarification
  ├→ blocked
  └→ deprecated

verified → requires_revalidation → approved
active → needs_recompile → approved
```

Compiler manages generated task intent, implementer may reach only `implemented_unverified`, and verifier alone may set `verified`. Direct `task transition --to verified` is rejected.
