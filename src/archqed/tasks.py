from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import DriftError, GateError
from .io import diff_snapshots, has_diff, now_utc, read_json, source_snapshot, write_json
from .project import load_project

TASK_STATES = {"draft", "needs_clarification", "approved", "in_progress", "implemented_unverified", "verified", "needs_recompile", "requires_revalidation", "blocked", "deprecated"}
TRANSITIONS = {
    "draft": {"approved", "needs_clarification", "blocked", "deprecated"},
    "needs_clarification": {"draft", "approved", "blocked", "deprecated"},
    "approved": {"in_progress", "needs_clarification", "blocked", "deprecated"},
    "in_progress": {"implemented_unverified", "needs_clarification", "blocked", "deprecated"},
    "implemented_unverified": {"in_progress", "needs_clarification", "blocked", "deprecated"},
    "needs_recompile": {"draft", "approved", "needs_clarification", "blocked", "deprecated"},
    "requires_revalidation": {"approved", "needs_clarification", "blocked", "deprecated"},
    "blocked": {"draft", "approved", "needs_clarification", "deprecated"},
    "verified": {"requires_revalidation", "deprecated"},
    "deprecated": set(),
}
REQUIRED_TASK_FIELDS = {"id", "title", "status", "source_refs", "dependencies", "acceptance", "forbidden"}


def task_path(root: Path, task_id: str) -> Path:
    return root / ".ai-control/tasks" / f"{task_id}.json"


def validate_task(task: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TASK_FIELDS - set(task))
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    if task.get("status") not in TASK_STATES:
        errors.append(f"invalid status: {task.get('status')}")
    for field in ("source_refs", "dependencies", "acceptance", "forbidden"):
        if not isinstance(task.get(field, []), list):
            errors.append(f"{field} must be a list")
    for index, case in enumerate(task.get("acceptance", [])):
        if not isinstance(case, dict) or not case.get("id") or not case.get("command"):
            errors.append(f"acceptance[{index}] requires id and command")
    return errors


def get_task(root: Path, task_id: str) -> dict[str, Any]:
    task = read_json(task_path(root, task_id))
    if not task:
        raise GateError(f"Unknown task: {task_id}")
    errors = validate_task(task)
    if errors:
        raise GateError(f"Invalid task {task_id}: {'; '.join(errors)}")
    return task


def list_tasks(root: Path) -> list[dict[str, Any]]:
    return [read_json(path, {}) for path in sorted((root / ".ai-control/tasks").glob("*.json"))]


def assert_control_ready(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    config, manifest = load_project(root)
    current = source_snapshot(root, config)
    if has_diff(diff_snapshots(manifest["source"], current)):
        raise DriftError("Human source documents changed. Run `archqed sync` and compile the change.")
    if manifest.get("control_state") != "ready":
        raise GateError(f"Control plane is {manifest.get('control_state')}, not ready.")
    return config, manifest


def next_task(root: Path) -> dict[str, Any] | None:
    assert_control_ready(root)
    candidates = []
    for task in list_tasks(root):
        if task.get("status") != "approved":
            continue
        if all(get_task(root, dep).get("status") == "verified" for dep in task.get("dependencies", [])):
            candidates.append(task)
    return min(candidates, key=lambda item: (item.get("priority", 100), item.get("id", "")), default=None)


def transition_task(root: Path, task_id: str, target: str, *, verifier: bool = False, evidence_path: str | None = None) -> dict[str, Any]:
    task = get_task(root, task_id)
    current = task["status"]
    if target == "verified" and not verifier:
        raise GateError("Only `archqed verify` may set a task to verified.")
    allowed = target in TRANSITIONS.get(current, set())
    if verifier and current == "implemented_unverified" and target == "verified":
        allowed = True
    if not allowed:
        raise GateError(f"Invalid task transition: {current} -> {target}")
    if target in {"in_progress", "implemented_unverified", "verified"}:
        assert_control_ready(root)
    task["status"] = target
    task["updated_at"] = now_utc()
    if target == "in_progress": task["started_at"] = now_utc()
    if target == "implemented_unverified": task["submitted_at"] = now_utc()
    if target == "verified":
        task["verified_at"] = now_utc()
        task["latest_evidence"] = evidence_path
    write_json(task_path(root, task_id), task)
    return task
