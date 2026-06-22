from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import GateError
from .io import diff_snapshots, has_diff, now_utc, read_json, source_snapshot, write_json

STAGES = {"discovery", "stabilizing", "delivery"}
CONFIG_PATH = Path(".archqed/config.json")
MANIFEST_PATH = Path(".ai-control/manifest.json")


def discover_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / CONFIG_PATH).exists() or (candidate / ".git").exists():
            return candidate
    return current


def load_project(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    config = read_json(root / CONFIG_PATH)
    manifest = read_json(root / MANIFEST_PATH)
    if not config or not manifest:
        raise GateError("ArchQED is not initialized. Run `archqed init` in the project root.")
    return config, manifest


def init_project(root: Path, name: str, stage: str, *, force: bool = False) -> dict[str, Any]:
    if stage not in STAGES:
        raise GateError(f"Unknown stage: {stage}")
    root.mkdir(parents=True, exist_ok=True)
    if ((root / CONFIG_PATH).exists() or (root / MANIFEST_PATH).exists()) and not force:
        raise GateError("ArchQED is already initialized.")
    config = {
        "schema_version": "0.1", "project": name, "stage": stage,
        "architecture_globs": ["docs/architecture/**/*.md"],
        "feature_globs": ["docs/features/**/*.md"],
        "evidence_output_limit": 20000,
    }
    for folder in ("changes", "contracts", "evidence", "gaps", "tasks", "traceability"):
        (root / ".ai-control" / folder).mkdir(parents=True, exist_ok=True)
    (root / "docs/architecture").mkdir(parents=True, exist_ok=True)
    (root / "docs/features").mkdir(parents=True, exist_ok=True)
    samples = {
        root / "docs/architecture/README.md": "# Architecture source\n\nWrite for people and add stable `ARCH-*` identifiers.\n",
        root / "docs/features/README.md": "# Feature details\n\nUse stable identifiers such as `REQ-STORY-001`.\n",
    }
    for path, content in samples.items():
        if not path.exists():
            path.write_text(content, encoding="utf-8")
    write_json(root / CONFIG_PATH, config)
    accepted = source_snapshot(root, config)
    manifest = {
        "schema_version": "0.1", "project": name, "control_state": "ready",
        "source": accepted, "candidate_source": None, "pending_change": None,
        "updated_at": now_utc(),
    }
    write_json(root / MANIFEST_PATH, manifest)
    return manifest


def set_stage(root: Path, stage: str) -> dict[str, Any]:
    if stage not in STAGES:
        raise GateError(f"Unknown stage: {stage}")
    config, manifest = load_project(root)
    if manifest.get("pending_change"):
        raise GateError("Resolve the pending change before changing stage.")
    config["stage"] = stage
    config["updated_at"] = now_utc()
    write_json(root / CONFIG_PATH, config)
    return config


def project_status(root: Path) -> dict[str, Any]:
    config, manifest = load_project(root)
    current = source_snapshot(root, config)
    drift = diff_snapshots(manifest["source"], current)
    counts: dict[str, int] = {}
    for path in sorted((root / ".ai-control/tasks").glob("*.json")):
        state = read_json(path, {}).get("status", "invalid")
        counts[state] = counts.get(state, 0) + 1
    return {
        "project": config.get("project"), "stage": config.get("stage"),
        "control_state": manifest.get("control_state"),
        "accepted_revision": manifest.get("source", {}).get("revision"),
        "current_revision": current.get("revision"),
        "has_unrecorded_drift": has_diff(drift), "drift": drift,
        "pending_change": manifest.get("pending_change"), "task_counts": counts,
    }
