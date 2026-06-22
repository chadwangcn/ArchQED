#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

CANONICAL_BOOTSTRAP_URL = "https://raw.githubusercontent.com/chadwangcn/ArchQED/main/BOOTSTRAP.md"
CANONICAL_STABLE_URL = "https://raw.githubusercontent.com/chadwangcn/ArchQED/main/stable.json"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "release-manifest.json"
    bootstrap_path = root / "BOOTSTRAP.md"
    init_path = root / "src/archqed/__init__.py"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"release manifest error: {exc}", file=sys.stderr)
        return 2
    match = re.search(r'__version__\s*=\s*"([^"]+)"', init_path.read_text(encoding="utf-8"))
    if not match:
        print("cannot read ArchQED version", file=sys.stderr)
        return 2
    version = match.group(1)
    actual = hashlib.sha256(bootstrap_path.read_bytes()).hexdigest()
    errors = []
    if manifest.get("version") != version:
        errors.append(f"manifest version {manifest.get('version')} != runtime version {version}")
    if manifest.get("release_ref") != "stable-channel":
        errors.append("release_ref must be stable-channel")
    if manifest.get("bootstrap_url") != CANONICAL_BOOTSTRAP_URL:
        errors.append("bootstrap_url is not the permanent main/BOOTSTRAP.md URL")
    if manifest.get("stable_url") != CANONICAL_STABLE_URL:
        errors.append("stable_url is not the permanent main/stable.json URL")
    if manifest.get("bootstrap_sha256") != actual:
        errors.append(f"BOOTSTRAP.md sha256 {actual} != manifest {manifest.get('bootstrap_sha256')}")
    if f"/v{version}/BOOTSTRAP.md" in bootstrap_path.read_text(encoding="utf-8"):
        errors.append("BOOTSTRAP.md contains a versioned public entry URL")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 2
    print(f"release manifest verified: ArchQED {version}, BOOTSTRAP sha256 {actual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
