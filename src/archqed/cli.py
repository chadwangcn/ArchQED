from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .changes import approve_change, complete_compile, sync_project
from .doctor import doctor_project
from .errors import ArchQEDError
from .evidence import verify_task
from .project import discover_root, init_project, project_status, set_stage
from .tasks import list_tasks, next_task, transition_task


def emit(value: Any, as_json: bool) -> None:
    if as_json: print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)); return
    if isinstance(value, list):
        if not value: print("No items.")
        for item in value: print(f"{item.get('id', '?')}\t{item.get('status', '?')}\t{item.get('title', '')}")
    elif isinstance(value, dict):
        for key, item in value.items():
            print(f"{key}: {json.dumps(item, ensure_ascii=False) if isinstance(item, (dict, list)) else item}")
    elif value is not None: print(value)


def command_root(args: argparse.Namespace, *, uninitialized: bool = False) -> Path:
    if args.root: return Path(args.root).resolve()
    return Path.cwd().resolve() if uninitialized else discover_root()


def build_parser() -> argparse.ArgumentParser:
    app = argparse.ArgumentParser(prog="archqed", description="Architecture-to-evidence control plane for coding agents.")
    app.add_argument("--root")
    app.add_argument("--version", action="version", version=f"ArchQED {__version__}")
    sub = app.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init"); init.add_argument("--name"); init.add_argument("--stage", choices=["discovery", "stabilizing", "delivery"], default="discovery"); init.add_argument("--force", action="store_true")
    sync = sub.add_parser("sync"); sync.add_argument("--check", action="store_true")
    sub.add_parser("status"); sub.add_parser("doctor")
    stage = sub.add_parser("set-stage"); stage.add_argument("stage", choices=["discovery", "stabilizing", "delivery"])
    approve = sub.add_parser("approve-change"); approve.add_argument("change_id")
    complete = sub.add_parser("compile-complete"); complete.add_argument("change_id")
    task = sub.add_parser("task"); task_sub = task.add_subparsers(dest="task_command", required=True)
    task_sub.add_parser("list"); task_sub.add_parser("next")
    start = task_sub.add_parser("start"); start.add_argument("task_id")
    submit = task_sub.add_parser("submit"); submit.add_argument("task_id")
    move = task_sub.add_parser("transition"); move.add_argument("task_id"); move.add_argument("--to", required=True)
    verify = sub.add_parser("verify"); verify.add_argument("task_id")
    for command in [app, *sub.choices.values(), *task_sub.choices.values()]: command.add_argument("--json", action="store_true", help=argparse.SUPPRESS)
    return app


def dispatch(args: argparse.Namespace) -> Any:
    if args.command == "init":
        root = command_root(args, uninitialized=True)
        return init_project(root, args.name or root.name, args.stage, force=args.force)
    root = command_root(args)
    if args.command == "sync": return sync_project(root, check=args.check)
    if args.command == "status": return project_status(root)
    if args.command == "doctor": return doctor_project(root)
    if args.command == "set-stage": return set_stage(root, args.stage)
    if args.command == "approve-change": return approve_change(root, args.change_id)
    if args.command == "compile-complete": return complete_compile(root, args.change_id)
    if args.command == "verify": return verify_task(root, args.task_id)
    if args.task_command == "list": return list_tasks(root)
    if args.task_command == "next": return next_task(root) or {"task": None, "message": "No approved task is ready."}
    if args.task_command == "start": return transition_task(root, args.task_id, "in_progress")
    if args.task_command == "submit": return transition_task(root, args.task_id, "implemented_unverified")
    return transition_task(root, args.task_id, args.to)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = dispatch(args); emit(result, args.json)
        if args.command == "doctor" and not result.get("ok"): return 2
        if args.command == "verify" and not result.get("passed"): return 5
        return 0
    except ArchQEDError as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return exc.exit_code
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 2
    except KeyboardInterrupt: return 130


if __name__ == "__main__": raise SystemExit(main())
