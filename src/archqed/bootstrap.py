from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from . import __version__
from .adapters import (
    PROJECT_CONFIG_PATH,
    detect_project,
    get_detection,
    load_project_configuration,
    project_configuration,
    select_adapter,
    write_project_configuration,
)
from .doctor import doctor_project
from .errors import GateError
from .io import canonical_hash, now_utc, read_json, sha256_bytes, write_json
from .project import CONFIG_PATH, MANIFEST_PATH, init_project
from .templates import AGENTS_BLOCK, EXECUTABLE_FILES, MANAGED_FILES

AGENTS_START = "# >>> ArchQED managed instructions >>>"
AGENTS_END = "# <<< ArchQED managed instructions <<<"
INSTALL_RECORD_PATH = Path(".archqed/install.json")
PROBE_PATH = Path(".archqed/probe.json")


def _write_text(path: Path, content: str, *, executable: bool = False) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = content if content.endswith("\n") else content + "\n"
    previous = path.read_text(encoding="utf-8") if path.exists() else None
    changed = previous != normalized
    if changed:
        path.write_text(normalized, encoding="utf-8")
    if executable and os.name != "nt":
        path.chmod(path.stat().st_mode | 0o111)
    return {
        "path": path.as_posix(),
        "changed": changed,
        "sha256": sha256_bytes(normalized.encode("utf-8")),
    }


def _strip_managed_block(text: str) -> str:
    start_count = text.splitlines().count(AGENTS_START)
    end_count = text.splitlines().count(AGENTS_END)
    if start_count != end_count or start_count > 1:
        raise GateError("AGENTS.md contains a malformed or duplicated ArchQED managed block; repair it before bootstrap.")
    lines = text.splitlines()
    output: list[str] = []
    skipping = False
    for line in lines:
        if line == AGENTS_START:
            skipping = True
            continue
        if line == AGENTS_END:
            skipping = False
            continue
        if not skipping:
            output.append(line)
    while output and not output[-1].strip():
        output.pop()
    return "\n".join(output)


def _merge_agents(path: Path) -> dict[str, Any]:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    preserved = _strip_managed_block(existing)
    parts = [part for part in (preserved, AGENTS_START, AGENTS_BLOCK.rstrip(), AGENTS_END) if part]
    return _write_text(path, "\n\n".join(parts))


def _copy_runtime(target: Path) -> list[dict[str, Any]]:
    source = Path(__file__).resolve().parent
    destination = target / ".archqed/runtime/archqed"
    temporary = target / ".archqed/runtime/.archqed-next"
    if temporary.exists():
        shutil.rmtree(temporary)
    temporary.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for path in sorted(source.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(source)
        output = temporary / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        raw = path.read_bytes()
        output.write_bytes(raw)
        records.append({
            "path": (Path(".archqed/runtime/archqed") / relative).as_posix(),
            "changed": True,
            "sha256": sha256_bytes(raw),
        })
    if destination.exists():
        shutil.rmtree(destination)
    temporary.replace(destination)
    return records


def _select_for_bootstrap(
    target: Path,
    probe: dict[str, Any],
    requested_adapter: str | None,
    *,
    allow_mismatch: bool,
) -> tuple[Any, str]:
    existing = load_project_configuration(target)
    adapter_id = requested_adapter
    selected_by = "explicit" if requested_adapter else "auto"
    if not adapter_id and existing:
        existing_adapter = existing.get("adapter", {}).get("id")
        if existing_adapter:
            adapter_id = str(existing_adapter)
            selected_by = "preserved"
    if adapter_id:
        try:
            detection = get_detection(probe, adapter_id)
        except GateError:
            if not allow_mismatch and selected_by != "preserved":
                raise
            from .adapters import ADAPTERS, Detection

            if adapter_id not in ADAPTERS:
                raise
            definition = ADAPTERS[adapter_id]
            detected = definition.detect(target)
            detection = detected or Detection(
                adapter_id,
                definition.label,
                0,
                (),
                {},
                ("selection preserved or explicitly allowed despite marker mismatch",),
            )
        return detection, selected_by
    if probe.get("ambiguous"):
        names = ", ".join(candidate["id"] for candidate in probe.get("candidates", [])[:5])
        raise GateError(
            f"Backend adapter detection is ambiguous: {names}. "
            "Read .archqed/probe.json and re-run bootstrap with --adapter ADAPTER-ID."
        )
    recommended = str(probe.get("recommended_adapter") or "generic")
    return get_detection(probe, recommended), "auto"


def bootstrap_project(
    target: Path,
    *,
    stage: str = "discovery",
    adapter: str | None = None,
    allow_mismatch: bool = False,
) -> dict[str, Any]:
    target = target.resolve()
    if not target.exists() or not target.is_dir():
        raise GateError(f"Target is not a directory: {target}")

    probe = detect_project(target)
    write_json(target / PROBE_PATH, probe)
    detection, selected_by = _select_for_bootstrap(
        target,
        probe,
        adapter,
        allow_mismatch=allow_mismatch,
    )

    has_config = (target / CONFIG_PATH).exists()
    has_manifest = (target / MANIFEST_PATH).exists()
    if has_config != has_manifest:
        raise GateError("Partial ArchQED installation detected: config and manifest must both exist.")
    initialized = False
    if not has_config:
        init_project(target, target.name, stage)
        initialized = True

    existing_project = load_project_configuration(target)
    project_config = project_configuration(
        target,
        detection,
        selected_by,
        existing=existing_project,
    )
    project_config["archqed_version"] = __version__
    project_config["probe_summary"] = {
        "recommended_adapter": probe.get("recommended_adapter"),
        "ambiguous": probe.get("ambiguous"),
        "candidate_ids": [candidate.get("id") for candidate in probe.get("candidates", [])],
    }
    write_project_configuration(target, project_config)

    previous_install = read_json(target / INSTALL_RECORD_PATH, {}) or {}
    previous_managed = set(previous_install.get("managed_files", []))
    installed: list[dict[str, Any]] = []
    installed.extend(_copy_runtime(target))
    for relative, content in MANAGED_FILES.items():
        output = target / relative
        if relative == ".codex/config.toml" and output.exists() and relative not in previous_managed:
            continue
        record = _write_text(
            output,
            content,
            executable=relative in EXECUTABLE_FILES,
        )
        record["path"] = relative
        installed.append(record)
    agents_record = _merge_agents(target / "AGENTS.md")
    agents_record["path"] = "AGENTS.md"
    installed.append(agents_record)

    install_record = {
        "schema_version": "0.2",
        "archqed_version": __version__,
        "installed_at": previous_install.get("installed_at", now_utc()),
        "updated_at": now_utc(),
        "adapter": detection.adapter_id,
        "selected_by": selected_by,
        "managed_files": sorted(record["path"] for record in installed),
        "runtime_hash": canonical_hash(
            {record["path"]: record["sha256"] for record in installed if record["path"].startswith(".archqed/runtime/")}
        ),
    }
    write_json(target / INSTALL_RECORD_PATH, install_record)

    doctor = doctor_project(target)
    stamp = now_utc().replace("-", "").replace(":", "")[:15]
    evidence_id = f"EVD-BOOTSTRAP-{stamp}"
    evidence_path = target / ".ai-control/evidence/bootstrap" / f"{evidence_id}.json"
    evidence = {
        "schema_version": "0.2",
        "id": evidence_id,
        "kind": "bootstrap",
        "created_at": now_utc(),
        "archqed_version": __version__,
        "target": str(target),
        "initialized": initialized,
        "adapter": project_config["adapter"],
        "requires_command_configuration": project_config["requires_command_configuration"],
        "probe_hash": canonical_hash(probe),
        "managed_files": installed,
        "doctor": doctor,
        "passed": bool(doctor.get("ok")),
    }
    write_json(evidence_path, evidence)
    result = {
        "ok": bool(doctor.get("ok")),
        "target": str(target),
        "archqed_version": __version__,
        "adapter": detection.adapter_id,
        "selected_by": selected_by,
        "initialized": initialized,
        "requires_command_configuration": project_config["requires_command_configuration"],
        "evidence": evidence_path.relative_to(target).as_posix(),
        "next": [
            "./scripts/archqed doctor",
            "./scripts/archqed status",
            "edit docs/architecture and docs/features",
            "./scripts/archqed sync",
            "./scripts/codex-sync.sh",
        ],
    }
    if not result["ok"]:
        raise GateError(f"Bootstrap verification failed; inspect {result['evidence']}")
    return result


def uninstall_project(target: Path, *, purge_control_data: bool = False) -> dict[str, Any]:
    target = target.resolve()
    removed: list[str] = []
    install_record = read_json(target / INSTALL_RECORD_PATH, {}) or {}
    managed = install_record.get("managed_files", [])
    for relative in sorted(set(str(path) for path in managed), reverse=True):
        path = target / relative
        if path.is_file() or path.is_symlink():
            path.unlink()
            removed.append(relative)
    runtime = target / ".archqed/runtime"
    if runtime.exists():
        shutil.rmtree(runtime)
        removed.append(".archqed/runtime/")
    agents = target / "AGENTS.md"
    if agents.exists():
        preserved = _strip_managed_block(agents.read_text(encoding="utf-8"))
        if preserved:
            agents.write_text(preserved + "\n", encoding="utf-8")
        else:
            agents.unlink()
        removed.append("AGENTS.md managed block")
    for relative in (INSTALL_RECORD_PATH, PROBE_PATH, PROJECT_CONFIG_PATH):
        path = target / relative
        if path.exists():
            path.unlink()
            removed.append(relative.as_posix())
    if purge_control_data:
        for relative in (Path(".ai-control"), Path(".archqed")):
            path = target / relative
            if path.exists():
                shutil.rmtree(path)
                removed.append(relative.as_posix() + "/")
    return {
        "ok": True,
        "target": str(target),
        "purged_control_data": purge_control_data,
        "removed": sorted(set(removed)),
    }
