from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

from .errors import GateError
from .io import canonical_hash, now_utc, write_json
from .tasks import assert_control_ready, get_task, transition_task

DEFAULT_OUTPUT_LIMIT = 20000
DEFAULT_TIMEOUT = 300


def task_contract_hash(task: dict[str, Any]) -> str:
    volatile = {"status", "updated_at", "started_at", "submitted_at", "verified_at", "latest_evidence"}
    return canonical_hash({key: value for key, value in task.items() if key not in volatile})


def run_case(root: Path, case: dict[str, Any], output_limit: int) -> dict[str, Any]:
    try:
        result = subprocess.run(case["command"], cwd=root, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=int(case.get("timeout_seconds", DEFAULT_TIMEOUT)))
        return {"id": case.get("id"), "command": case["command"], "exit_code": result.returncode, "passed": result.returncode == 0, "stdout": result.stdout[-output_limit:], "stderr": result.stderr[-output_limit:]}
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = exc.stdout or "", exc.stderr or ""
        if isinstance(stdout, bytes): stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes): stderr = stderr.decode(errors="replace")
        return {"id": case.get("id"), "command": case["command"], "exit_code": None, "passed": False, "timed_out": True, "stdout": stdout[-output_limit:], "stderr": stderr[-output_limit:]}


def iter_text_files(root: Path, locations: Iterable[str]) -> Iterable[Path]:
    for location in locations:
        target = root / location
        if target.is_file(): yield target
        elif target.exists():
            for path in target.rglob("*"):
                if path.is_file() and ".git" not in path.parts and path.stat().st_size <= 1_000_000:
                    yield path


def scan_forbidden(root: Path, rules: list[Any]) -> list[dict[str, Any]]:
    findings = []
    for index, raw in enumerate(rules):
        rule = {"id": f"rule-{index + 1}", "pattern": raw, "paths": ["src"]} if isinstance(raw, str) else raw
        if not isinstance(rule, dict):
            findings.append({"rule": f"rule-{index + 1}", "error": "rule must be string or object"}); continue
        try: pattern = re.compile(rule["pattern"], re.MULTILINE)
        except (KeyError, re.error) as exc:
            findings.append({"rule": rule.get("id", f"rule-{index + 1}"), "error": str(exc)}); continue
        excluded = tuple(rule.get("exclude_paths", []))
        for path in iter_text_files(root, rule.get("paths", ["src"])):
            relative = path.relative_to(root).as_posix()
            if excluded and any(relative.startswith(prefix) for prefix in excluded): continue
            try: text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError: continue
            for match in pattern.finditer(text):
                findings.append({"rule": rule.get("id", f"rule-{index + 1}"), "path": relative, "line": text.count("\n", 0, match.start()) + 1, "match": match.group(0)[:160]})
    return findings


def verify_task(root: Path, task_id: str) -> dict[str, Any]:
    config, manifest = assert_control_ready(root)
    task = get_task(root, task_id)
    if task.get("status") != "implemented_unverified":
        raise GateError("Task must be implemented_unverified before independent verification.")
    acceptance = task.get("acceptance", [])
    if not acceptance:
        raise GateError("Task has no executable acceptance cases.")
    limit = int(config.get("evidence_output_limit", DEFAULT_OUTPUT_LIMIT))
    cases = [run_case(root, case, limit) for case in acceptance]
    findings = scan_forbidden(root, task.get("forbidden", []))
    passed = all(case["passed"] for case in cases) and not findings
    stamp = now_utc().replace("-", "").replace(":", "")[:15]
    evidence_id = f"EVD-{task_id}-{stamp}"
    evidence = {"schema_version": "0.1", "id": evidence_id, "task_id": task_id, "source_revision": manifest["source"]["revision"], "task_contract_hash": task_contract_hash(task), "created_at": now_utc(), "passed": passed, "acceptance_results": cases, "forbidden_findings": findings}
    path = root / ".ai-control/evidence" / task_id / f"{evidence_id}.json"
    write_json(path, evidence)
    relative = path.relative_to(root).as_posix()
    if passed: transition_task(root, task_id, "verified", verifier=True, evidence_path=relative)
    return {"task_id": task_id, "passed": passed, "status": "verified" if passed else "implemented_unverified", "evidence": relative, "failed_cases": [case["id"] for case in cases if not case["passed"]], "forbidden_findings": len(findings)}
