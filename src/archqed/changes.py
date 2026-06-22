from __future__ import annotations

import secrets
from pathlib import Path
from typing import Any

from .errors import DriftError, GateError
from .io import diff_snapshots, has_diff, now_utc, read_json, source_snapshot, write_json
from .project import MANIFEST_PATH, load_project


def approval_required(stage: str, kind: str) -> bool:
    return stage == "delivery" or (stage == "stabilizing" and kind in {"architecture", "mixed"})


def changed_refs(before: dict[str, Any], after: dict[str, Any], changes: dict[str, list[str]]) -> set[str]:
    refs: set[str] = set()
    for name in changes["added"] + changes["removed"] + changes["changed"]:
        refs.update(before.get("files", {}).get(name, {}).get("refs", []))
        refs.update(after.get("files", {}).get(name, {}).get("refs", []))
    return refs


def classify_change(before: dict[str, Any], after: dict[str, Any], changes: dict[str, list[str]]) -> str:
    kinds = set()
    for name in changes["added"] + changes["removed"] + changes["changed"]:
        metadata = after.get("files", {}).get(name) or before.get("files", {}).get(name, {})
        if metadata.get("kind"): kinds.add(metadata["kind"])
    return "mixed" if len(kinds) > 1 else next(iter(kinds), "feature")


def invalidate_tasks(root: Path, *, global_impact: bool, refs: set[str]) -> list[str]:
    affected = []
    for path in sorted((root / ".ai-control/tasks").glob("*.json")):
        task = read_json(path, {})
        status = task.get("status")
        if status in {"draft", "needs_clarification", "blocked", "deprecated"}:
            continue
        if not global_impact and not refs.intersection(task.get("source_refs", [])):
            continue
        task["status"] = "requires_revalidation" if status == "verified" else "needs_recompile"
        task["updated_at"] = now_utc()
        write_json(path, task)
        affected.append(task.get("id", path.stem))
    return affected


def change_path(root: Path, change_id: str) -> Path:
    return root / ".ai-control/changes" / f"{change_id}.json"


def sync_project(root: Path, *, check: bool = False) -> dict[str, Any]:
    config, manifest = load_project(root)
    current = source_snapshot(root, config)
    baseline = manifest["source"]
    changes = diff_snapshots(baseline, current)
    if check:
        if has_diff(changes) or manifest.get("pending_change"):
            raise DriftError("Architecture control data is not synchronized.")
        return {"changed": False, "control_state": manifest.get("control_state")}
    pending_id = manifest.get("pending_change")
    if not has_diff(changes):
        if pending_id:
            pending = read_json(change_path(root, pending_id), {})
            pending.update({"status": "reverted", "reverted_at": now_utc()})
            write_json(change_path(root, pending_id), pending)
            manifest.update({"control_state": "ready", "pending_change": None, "candidate_source": None, "updated_at": now_utc()})
            write_json(root / MANIFEST_PATH, manifest)
            return {"changed": False, "reverted_change": pending_id, "control_state": "ready"}
        return {"changed": False, "control_state": manifest.get("control_state")}
    candidate = manifest.get("candidate_source")
    if pending_id and candidate and candidate.get("revision") == current.get("revision"):
        return read_json(change_path(root, pending_id), {})
    if pending_id:
        old = read_json(change_path(root, pending_id), {})
        old.update({"status": "superseded", "superseded_at": now_utc()})
        write_json(change_path(root, pending_id), old)
    kind = classify_change(baseline, current, changes)
    refs = changed_refs(baseline, current, changes)
    global_impact = config["stage"] == "discovery" or kind in {"architecture", "mixed"} or not refs
    gated = approval_required(config["stage"], kind)
    stamp = now_utc().replace("-", "").replace(":", "")[:15]
    change_id = f"CHG-{stamp}-{current['revision'][:10].upper()}-{secrets.token_hex(2).upper()}"
    change = {
        "schema_version": "0.1", "id": change_id, "stage": config["stage"], "kind": kind,
        "status": "awaiting_approval" if gated else "approved", "requires_approval": gated,
        "baseline_revision": baseline["revision"], "candidate_revision": current["revision"],
        "diff": changes, "source_refs": sorted(refs),
        "impact": "global" if global_impact else "scoped",
        "affected_tasks": invalidate_tasks(root, global_impact=global_impact, refs=refs),
        "detected_at": now_utc(), "supersedes": pending_id,
    }
    write_json(change_path(root, change_id), change)
    manifest.update({"control_state": "awaiting_approval" if gated else "needs_compile", "pending_change": change_id, "candidate_source": current, "updated_at": now_utc()})
    write_json(root / MANIFEST_PATH, manifest)
    return change


def approve_change(root: Path, change_id: str) -> dict[str, Any]:
    config, manifest = load_project(root)
    if manifest.get("pending_change") != change_id:
        raise GateError("Only the current pending change can be approved.")
    change = read_json(change_path(root, change_id))
    if not change or change.get("status") != "awaiting_approval":
        raise GateError("Change is not awaiting approval.")
    if source_snapshot(root, config).get("revision") != change.get("candidate_revision"):
        raise DriftError("Source changed after this approval request. Run `archqed sync` first.")
    change.update({"status": "approved", "approved_at": now_utc()})
    manifest.update({"control_state": "needs_compile", "updated_at": now_utc()})
    write_json(change_path(root, change_id), change)
    write_json(root / MANIFEST_PATH, manifest)
    return change


def complete_compile(root: Path, change_id: str) -> dict[str, Any]:
    config, manifest = load_project(root)
    if manifest.get("pending_change") != change_id:
        raise GateError("Change is not the current pending change.")
    change = read_json(change_path(root, change_id))
    if not change or change.get("status") != "approved":
        raise GateError("Change must be approved before compilation can complete.")
    candidate = manifest.get("candidate_source") or {}
    if source_snapshot(root, config).get("revision") != candidate.get("revision"):
        raise DriftError("Source changed during compilation. Run `archqed sync`.")
    blocking = []
    for path in sorted((root / ".ai-control/gaps").glob("*.json")):
        gap = read_json(path, {})
        if gap.get("status", "open") == "open" and gap.get("blocking", False):
            blocking.append(gap.get("id", path.stem))
    if blocking:
        raise GateError(f"Blocking architecture gaps remain open: {', '.join(blocking)}")
    change.update({"status": "compiled", "compiled_at": now_utc()})
    manifest.update({"source": candidate, "candidate_source": None, "pending_change": None, "control_state": "ready", "updated_at": now_utc()})
    write_json(change_path(root, change_id), change)
    write_json(root / MANIFEST_PATH, manifest)
    return manifest
