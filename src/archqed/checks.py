from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters import COMMAND_KEYS, load_project_configuration
from .errors import GateError
from .evidence import DEFAULT_OUTPUT_LIMIT, run_case
from .io import canonical_hash, now_utc, write_json
from .tasks import assert_control_ready


def run_project_checks(
    root: Path,
    *,
    only: list[str] | None = None,
    include_install: bool = False,
) -> dict[str, Any]:
    config, manifest = assert_control_ready(root)
    project = load_project_configuration(root)
    if not project:
        raise GateError("Missing .archqed/project.json. Run `archqed bootstrap --target .`.")
    configured = project.get("commands", {})
    if not isinstance(configured, dict):
        raise GateError("Project commands must be an object.")
    requested = only or [name for name in COMMAND_KEYS if name != "install"]
    unknown = sorted(set(requested) - set(COMMAND_KEYS))
    if unknown:
        raise GateError(f"Unknown project check names: {', '.join(unknown)}")
    if include_install and "install" not in requested:
        requested = ["install", *requested]
    cases: list[dict[str, Any]] = []
    for name in requested:
        value = configured.get(name)
        if not isinstance(value, dict) or not value.get("enabled", True):
            continue
        command = value.get("command")
        if not command:
            continue
        cases.append({
            "id": f"PROJECT-{name.upper()}",
            "name": name,
            "command": str(command),
            "timeout_seconds": int(value.get("timeout_seconds", 900)),
        })
    if not cases:
        raise GateError(
            "No enabled project commands were selected. Configure the generic adapter with "
            "`archqed adapter configure generic --command unit_test=...` or select a detected adapter."
        )
    output_limit = int(config.get("evidence_output_limit", DEFAULT_OUTPUT_LIMIT))
    results = []
    for case in cases:
        result = run_case(root, case, output_limit)
        result["name"] = case["name"]
        results.append(result)
        if not result["passed"]:
            break
    passed = len(results) == len(cases) and all(result["passed"] for result in results)
    stamp = now_utc().replace("-", "").replace(":", "")[:15]
    evidence_id = f"EVD-PROJECT-CHECK-{stamp}"
    evidence_path = root / ".ai-control/evidence/project-check" / f"{evidence_id}.json"
    evidence = {
        "schema_version": "0.2",
        "id": evidence_id,
        "kind": "project-check",
        "created_at": now_utc(),
        "source_revision": manifest["source"]["revision"],
        "project_configuration_hash": canonical_hash(project),
        "requested_checks": requested,
        "passed": passed,
        "results": results,
    }
    write_json(evidence_path, evidence)
    return {
        "passed": passed,
        "evidence": evidence_path.relative_to(root).as_posix(),
        "executed": [result["name"] for result in results],
        "failed": next((result["name"] for result in results if not result["passed"]), None),
    }
