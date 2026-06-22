#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


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
    expected = manifest.get("bootstrap_sha256")
    errors = []
    if manifest.get("version") != version:
        errors.append(f"manifest version {manifest.get('version')} != runtime version {version}")
    if manifest.get("release_ref") != f"v{version}":
        errors.append(f"release_ref {manifest.get('release_ref')} != v{version}")
    if expected != actual:
        errors.append(f"BOOTSTRAP.md sha256 {actual} != manifest {expected}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 2
    print(f"release manifest verified: ArchQED {version}, BOOTSTRAP sha256 {actual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
