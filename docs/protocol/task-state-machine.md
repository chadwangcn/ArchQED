# Task state machine

```text
draft → approved → in_progress → implemented_unverified → verified
  ├→ needs_clarification
  ├→ blocked
  └→ deprecated

verified → requires_revalidation → approved
active → needs_recompile → approved
```

Compiler manages generated intent. Implementer may reach only `implemented_unverified`. The deterministic verifier alone may set `verified`. Direct transitions to `verified` are rejected.
