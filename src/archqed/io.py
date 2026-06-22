from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REF_PATTERN = re.compile(r"\b(?:ARCH|REQ|ADR|API|DATA|AGENT)-[A-Z0-9][A-Z0-9_.-]*\b")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(payload)


def extract_refs(text: str) -> list[str]:
    return sorted(set(REF_PATTERN.findall(text)))


def source_snapshot(root: Path, config: dict[str, Any]) -> dict[str, Any]:
    files: dict[str, Any] = {}
    seen: set[Path] = set()
    groups = (
        ("architecture", config.get("architecture_globs", ["docs/architecture/**/*.md"])),
        ("feature", config.get("feature_globs", ["docs/features/**/*.md"])),
    )
    for kind, patterns in groups:
        for pattern in patterns:
            for path in sorted(root.glob(pattern)):
                if not path.is_file() or path in seen:
                    continue
                seen.add(path)
                raw = path.read_bytes()
                text = raw.decode("utf-8")
                files[path.relative_to(root).as_posix()] = {
                    "kind": kind,
                    "sha256": sha256_bytes(raw),
                    "refs": extract_refs(text),
                    "size": len(raw),
                }
    revision = canonical_hash(files)
    return {"revision": revision, "files": files}


def diff_snapshots(before: dict[str, Any], after: dict[str, Any]) -> dict[str, list[str]]:
    old_files = before.get("files", {})
    new_files = after.get("files", {})
    old_names = set(old_files)
    new_names = set(new_files)
    return {
        "added": sorted(new_names - old_names),
        "removed": sorted(old_names - new_names),
        "changed": sorted(name for name in old_names & new_names if old_files[name].get("sha256") != new_files[name].get("sha256")),
    }


def has_diff(changes: dict[str, list[str]]) -> bool:
    return any(changes.get(key) for key in ("added", "removed", "changed"))
