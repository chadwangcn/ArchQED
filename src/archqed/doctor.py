from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from . import __version__
from .adapters import ADAPTERS, COMMAND_KEYS, PROJECT_CONFIG_PATH, detect_project, load_project_configuration
from .io import diff_snapshots, has_diff, read_json, source_snapshot
from .project import CONFIG_PATH, MANIFEST_PATH, load_project
from .tasks import list_tasks, validate_task


def doctor_project(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, Any] = {}
    for relative in [CONFIG_PATH, MANIFEST_PATH, Path(".ai-control/tasks"), Path(".ai-control/evidence")]:
        exists = (root / relative).exists()
        checks[f"exists:{relative.as_posix()}"] = exists
        if not exists:
            errors.append(f"missing: {relative.as_posix()}")
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings, "checks": checks}
    try:
        config, manifest = load_project(root)
        current = source_snapshot(root, config)
    except Exception as exc:
        return {"ok": False, "errors": [str(exc)], "warnings": warnings, "checks": checks}
    if has_diff(diff_snapshots(manifest["source"], current)):
        errors.append("human source documents have unrecorded drift")
    if manifest.get("pending_change") and not manifest.get("candidate_source"):
        errors.append("pending_change exists without candidate_source")
    if not manifest.get("pending_change") and manifest.get("candidate_source"):
        errors.append("candidate_source exists without pending_change")
    ids: set[str] = set()
    refs = {ref for metadata in current.get("files", {}).values() for ref in metadata.get("refs", [])}
    for task in list_tasks(root):
        task_id = task.get("id", "<missing>")
        if task_id in ids:
            errors.append(f"duplicate task id: {task_id}")
        ids.add(task_id)
        for error in validate_task(task):
            errors.append(f"{task_id}: {error}")
        unknown = sorted(set(task.get("source_refs", [])) - refs)
        if unknown:
            warnings.append(f"{task_id}: source refs not found: {', '.join(unknown)}")

    install = read_json(root / ".archqed/install.json", {}) or {}
    project = load_project_configuration(root)
    if project is None:
        message = "missing .archqed/project.json; run `archqed bootstrap --target .`"
        if install:
            errors.append(message)
        else:
            warnings.append(message)
    else:
        if project.get("schema_version") != "0.2":
            errors.append("unsupported .archqed/project.json schema_version")
        adapter = project.get("adapter", {})
        adapter_id = adapter.get("id") if isinstance(adapter, dict) else None
        if adapter_id not in ADAPTERS:
            errors.append(f"unknown project adapter: {adapter_id}")
        commands = project.get("commands", {})
        if not isinstance(commands, dict):
            errors.append("project commands must be an object")
        else:
            for name, value in commands.items():
                if name not in COMMAND_KEYS:
                    errors.append(f"unknown project command: {name}")
                    continue
                if not isinstance(value, dict) or not isinstance(value.get("command"), str) or not value.get("command", "").strip():
                    errors.append(f"invalid project command: {name}")
            if adapter_id == "generic" and not commands:
                warnings.append("generic adapter has no commands; configure at least unit_test or build before implementation")
        probe = detect_project(root)
        candidate_ids = {candidate["id"] for candidate in probe.get("candidates", [])}
        if adapter_id not in {"generic", *candidate_ids}:
            warnings.append(f"selected adapter {adapter_id} no longer matches detected project markers")
        if probe.get("ambiguous"):
            warnings.append("multiple backend adapters are plausible; explicit adapter selection is recommended")

    if install:
        if install.get("archqed_version") != __version__:
            errors.append(
                f"runtime/install version mismatch: runtime={__version__}, install={install.get('archqed_version')}"
            )
        required_managed = [
            Path("scripts/archqed"),
            Path(".agents/skills/archqed-compile/SKILL.md"),
            Path(".agents/skills/archqed-implement/SKILL.md"),
            Path(".agents/skills/archqed-verify/SKILL.md"),
            Path(".codex/agents/archqed-verifier.toml"),
        ]
        for relative in required_managed:
            if not (root / relative).exists():
                errors.append(f"missing managed integration file: {relative.as_posix()}")
        if not (root / ".archqed/runtime/archqed/__init__.py").exists():
            errors.append("missing vendored ArchQED runtime")

    if sys.version_info < (3, 11):
        errors.append("ArchQED requires Python 3.11 or newer")
    checks["python_version"] = ".".join(str(part) for part in sys.version_info[:3])
    checks["archqed_version"] = __version__
    return {"ok": not errors, "errors": errors, "warnings": warnings, "checks": checks}
