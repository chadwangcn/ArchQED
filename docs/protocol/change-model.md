# Change model

Human-source changes are compared with the last accepted snapshot.

- `discovery`: every change is global; approval is off by default.
- `stabilizing`: architecture/mixed changes require approval and are global; feature changes can be scoped by stable IDs.
- `delivery`: every change requires approval; feature scope is retained when traceability is complete.

A second edit before compilation marks the previous pending change `superseded` and recalculates from the accepted baseline. Returning exactly to the baseline marks it `reverted`. Stale approvals and stale compile-complete operations are rejected.

A change is global when stage is discovery, kind is architecture/mixed, or stable references are unavailable. Scoped feature changes invalidate only tasks whose `source_refs` intersect the changed IDs. Verified affected tasks become `requires_revalidation`; other active affected tasks become `needs_recompile`.
