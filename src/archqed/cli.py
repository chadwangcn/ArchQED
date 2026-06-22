from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .adapters import (
    configure_adapter,
    detect_project,
    list_adapters,
    load_project_configuration,
)
from .bootstrap import bootstrap_project, uninstall_project
from .changes import approve_change, complete_compile, sync_project
from .checks import run_project_checks
from .doctor import doctor_project
from .errors import ArchQEDError, GateError
from .evidence import verify_task
from .project import discover_root, init_project, project_status, set_stage
from .tasks import list_tasks, next_task, transition_task


def emit(value: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))
        return
    if isinstance(value, list):
        if not value:
            print("No items.")
        for item in value:
            if isinstance(item, dict):
                print(f"{item.get('id', '?')}\t{item.get('status', '')}\t{item.get('title') or item.get('label') or item.get('description', '')}")
            else:
                print(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            print(f"{key}: {json.dumps(item, ensure_ascii=False) if isinstance(item, (dict, list)) else item}")
    elif value is not None:
        print(value)


def command_root(args: argparse.Namespace, *, uninitialized: bool = False) -> Path:
    if getattr(args, "root", None):
        return Path(args.root).resolve()
    return Path.cwd().resolve() if uninitialized else discover_root()


def target_root(args: argparse.Namespace) -> Path:
    return Path(getattr(args, "target", None) or getattr(args, "root", None) or ".").resolve()


def _add_json(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help=argparse.SUPPRESS)


def build_parser() -> argparse.ArgumentParser:
    app = argparse.ArgumentParser(
        prog="archqed",
        description="Architecture-to-evidence control plane for backend coding agents.",
    )
    app.add_argument("--root")
    app.add_argument("--version", action="version", version=f"ArchQED {__version__}")
    _add_json(app)
    sub = app.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize ArchQED control data.")
    init.add_argument("--name")
    init.add_argument("--stage", choices=["discovery", "stabilizing", "delivery"], default="discovery")
    init.add_argument("--force", action="store_true")
    _add_json(init)

    bootstrap = sub.add_parser("bootstrap", help="Install or upgrade ArchQED in any backend repository.")
    bootstrap.add_argument("--target", default=".")
    bootstrap.add_argument("--stage", choices=["discovery", "stabilizing", "delivery"], default="discovery")
    bootstrap.add_argument("--adapter")
    bootstrap.add_argument("--allow-mismatch", action="store_true")
    _add_json(bootstrap)

    uninstall = sub.add_parser("uninstall", help="Remove managed integration files.")
    uninstall.add_argument("--target", default=".")
    uninstall.add_argument("--purge-control-data", action="store_true")
    _add_json(uninstall)

    probe = sub.add_parser("probe", help="Detect backend technology and suggested project commands.")
    probe.add_argument("--target", default=".")
    _add_json(probe)

    adapter = sub.add_parser("adapter", help="Inspect or configure backend adapters.")
    adapter_sub = adapter.add_subparsers(dest="adapter_command", required=True)
    adapter_list = adapter_sub.add_parser("list")
    _add_json(adapter_list)
    adapter_detect = adapter_sub.add_parser("detect")
    adapter_detect.add_argument("--target", default=".")
    _add_json(adapter_detect)
    adapter_configure = adapter_sub.add_parser("configure")
    adapter_configure.add_argument("adapter_id", nargs="?")
    adapter_configure.add_argument("--target", default=".")
    adapter_configure.add_argument("--command", action="append", default=[])
    adapter_configure.add_argument("--allow-mismatch", action="store_true")
    _add_json(adapter_configure)

    sync = sub.add_parser("sync", help="Detect or verify human-document drift.")
    sync.add_argument("--check", action="store_true")
    _add_json(sync)

    status = sub.add_parser("status")
    _add_json(status)
    doctor = sub.add_parser("doctor")
    _add_json(doctor)

    stage = sub.add_parser("set-stage")
    stage.add_argument("stage", choices=["discovery", "stabilizing", "delivery"])
    _add_json(stage)

    approve = sub.add_parser("approve-change")
    approve.add_argument("change_id")
    _add_json(approve)

    complete = sub.add_parser("compile-complete")
    complete.add_argument("change_id")
    _add_json(complete)

    task = sub.add_parser("task")
    task_sub = task.add_subparsers(dest="task_command", required=True)
    task_list = task_sub.add_parser("list")
    _add_json(task_list)
    task_next = task_sub.add_parser("next")
    _add_json(task_next)
    task_start = task_sub.add_parser("start")
    task_start.add_argument("task_id")
    _add_json(task_start)
    task_submit = task_sub.add_parser("submit")
    task_submit.add_argument("task_id")
    _add_json(task_submit)
    task_move = task_sub.add_parser("transition")
    task_move.add_argument("task_id")
    task_move.add_argument("--to", required=True)
    _add_json(task_move)

    verify = sub.add_parser("verify")
    verify.add_argument("task_id")
    _add_json(verify)

    check = sub.add_parser("check", help="Run configured backend project checks and preserve evidence.")
    check.add_argument("--only", action="append", default=[])
    check.add_argument("--include-install", action="store_true")
    _add_json(check)
    return app


def dispatch(args: argparse.Namespace) -> Any:
    if args.command == "init":
        root = command_root(args, uninitialized=True)
        return init_project(root, args.name or root.name, args.stage, force=args.force)
    if args.command == "bootstrap":
        return bootstrap_project(
            target_root(args),
            stage=args.stage,
            adapter=args.adapter,
            allow_mismatch=args.allow_mismatch,
        )
    if args.command == "uninstall":
        return uninstall_project(target_root(args), purge_control_data=args.purge_control_data)
    if args.command == "probe":
        return detect_project(target_root(args))
    if args.command == "adapter":
        if args.adapter_command == "list":
            return list_adapters()
        if args.adapter_command == "detect":
            return detect_project(target_root(args))
        target = target_root(args)
        adapter_id = args.adapter_id
        if not adapter_id:
            current = load_project_configuration(target)
            adapter_id = current.get("adapter", {}).get("id") if current else None
        if not adapter_id:
            raise GateError("No adapter supplied and no existing adapter selection found.")
        return configure_adapter(
            target,
            str(adapter_id),
            args.command,
            allow_mismatch=args.allow_mismatch,
        )

    root = command_root(args)
    if args.command == "sync":
        return sync_project(root, check=args.check)
    if args.command == "status":
        return project_status(root)
    if args.command == "doctor":
        return doctor_project(root)
    if args.command == "set-stage":
        return set_stage(root, args.stage)
    if args.command == "approve-change":
        return approve_change(root, args.change_id)
    if args.command == "compile-complete":
        return complete_compile(root, args.change_id)
    if args.command == "verify":
        return verify_task(root, args.task_id)
    if args.command == "check":
        return run_project_checks(root, only=args.only or None, include_install=args.include_install)
    if args.task_command == "list":
        return list_tasks(root)
    if args.task_command == "next":
        return next_task(root) or {"task": None, "message": "No approved task is ready."}
    if args.task_command == "start":
        return transition_task(root, args.task_id, "in_progress")
    if args.task_command == "submit":
        return transition_task(root, args.task_id, "implemented_unverified")
    return transition_task(root, args.task_id, args.to)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = dispatch(args)
        emit(result, bool(getattr(args, "json", False)))
        if args.command == "doctor" and not result.get("ok"):
            return 2
        if args.command in {"verify", "check"} and not result.get("passed"):
            return 5
        return 0
    except ArchQEDError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return exc.exit_code
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
