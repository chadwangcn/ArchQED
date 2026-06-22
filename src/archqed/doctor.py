from __future__ import annotations

from pathlib import Path
from typing import Any

from .io import diff_snapshots, has_diff, source_snapshot
from .project import CONFIG_PATH, MANIFEST_PATH, load_project
from .tasks import list_tasks, validate_task


def doctor_project(root: Path) -> dict[str, Any]:
    errors, warnings = [], []
    for relative in [CONFIG_PATH, MANIFEST_PATH, Path(".ai-control/tasks"), Path(".ai-control/evidence")]:
        if not (root / relative).exists(): errors.append(f"missing: {relative.as_posix()}")
    if errors: return {"ok": False, "errors": errors, "warnings": warnings}
    try:
        config, manifest = load_project(root)
        current = source_snapshot(root, config)
    except Exception as exc:
        return {"ok": False, "errors": [str(exc)], "warnings": warnings}
    if has_diff(diff_snapshots(manifest["source"], current)):
        errors.append("human source documents have unrecorded drift")
    if manifest.get("pending_change") and not manifest.get("candidate_source"):
        errors.append("pending_change exists without candidate_source")
    if not manifest.get("pending_change") and manifest.get("candidate_source"):
        errors.append("candidate_source exists without pending_change")
    ids = set()
    refs = {ref for metadata in current.get("files", {}).values() for ref in metadata.get("refs", [])}
    for task in list_tasks(root):
        task_id = task.get("id", "<missing>")
        if task_id in ids: errors.append(f"duplicate task id: {task_id}")
        ids.add(task_id)
        for error in validate_task(task): errors.append(f"{task_id}: {error}")
        unknown = sorted(set(task.get("source_refs", [])) - refs)
        if unknown: warnings.append(f"{task_id}: source refs not found: {', '.join(unknown)}")
    return {"ok": not errors, "errors": errors, "warnings": warnings}
