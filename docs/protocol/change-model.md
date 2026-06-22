# Change model

Human-source changes are compared with the last accepted snapshot.

- `discovery`: every source change is global; approval is off by default.
- `stabilizing`: architecture or mixed changes require approval and are global; feature changes can be scoped by stable IDs.
- `delivery`: every source change requires approval; feature scope is retained only when traceability is complete.

A second edit before compilation marks the previous pending change `superseded` and recalculates from the accepted baseline. Returning exactly to the baseline marks it `reverted`. Stale approvals and stale compile-complete operations are rejected.

Backend adapter changes are stored separately in `.archqed/project.json`. They do not rewrite human architecture, but changed verification commands should trigger task review before evidence is trusted.
