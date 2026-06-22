from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .errors import GateError
from .io import now_utc, read_json, write_json

PROJECT_CONFIG_PATH = Path(".archqed/project.json")
COMMAND_KEYS = (
    "install",
    "lint",
    "typecheck",
    "unit_test",
    "integration_test",
    "build",
    "smoke_test",
)


@dataclass(frozen=True)
class Detection:
    adapter_id: str
    label: str
    score: int
    evidence: tuple[str, ...]
    commands: dict[str, str]
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.adapter_id,
            "label": self.label,
            "score": self.score,
            "evidence": list(self.evidence),
            "commands": self.commands,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class AdapterDefinition:
    adapter_id: str
    label: str
    detect: Callable[[Path], Detection | None]
    description: str


def _exists(root: Path, *names: str) -> list[str]:
    return [name for name in names if (root / name).exists()]


def _glob_exists(root: Path, pattern: str) -> list[str]:
    return sorted(path.relative_to(root).as_posix() for path in root.glob(pattern) if path.is_file())


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}


def _command_map(**commands: str | None) -> dict[str, str]:
    return {key: value for key, value in commands.items() if key in COMMAND_KEYS and value}


def _python(root: Path) -> Detection | None:
    markers = _exists(
        root,
        "pyproject.toml",
        "requirements.txt",
        "setup.py",
        "setup.cfg",
        "Pipfile",
        "poetry.lock",
        "uv.lock",
    )
    markers.extend(_glob_exists(root, "requirements*.txt"))
    markers = sorted(set(markers))
    if not markers:
        return None
    combined = "\n".join(_read_text(root / name) for name in markers if (root / name).is_file()).lower()
    backend_frameworks = ("fastapi", "django", "flask", "starlette", "litestar", "sanic", "aiohttp", "falcon", "grpcio")
    evidence = list(markers)
    score = 60
    found_frameworks = sorted(name for name in backend_frameworks if name in combined)
    if found_frameworks:
        score += 25
        evidence.append("backend-framework:" + ",".join(found_frameworks))
    install = None
    if (root / "uv.lock").exists():
        install = "uv sync --frozen"
    elif (root / "poetry.lock").exists():
        install = "poetry install --no-interaction"
    elif (root / "requirements.txt").exists():
        install = "python -m pip install -r requirements.txt"
    elif (root / "pyproject.toml").exists() or (root / "setup.py").exists():
        install = "python -m pip install -e ."
    unit = "python -m pytest -q" if "pytest" in combined or (root / "pytest.ini").exists() else "python -m unittest discover -v"
    return Detection(
        "python",
        "Python",
        min(score, 100),
        tuple(evidence),
        _command_map(
            install=install,
            lint="python -m ruff check ." if "ruff" in combined else None,
            typecheck="python -m mypy ." if "mypy" in combined else None,
            unit_test=unit,
            build="python -m build" if "python -m build" in combined or "[build-system]" in combined else None,
        ),
    )


def _node(root: Path) -> Detection | None:
    package_path = root / "package.json"
    if not package_path.exists():
        return None
    package = _json_object(package_path)
    dependencies: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        value = package.get(key, {})
        if isinstance(value, dict):
            dependencies.update(str(name).lower() for name in value)
    backend_frameworks = {
        "express", "fastify", "@nestjs/core", "koa", "@hapi/hapi", "restify", "hono",
        "apollo-server", "@apollo/server", "graphql-yoga", "prisma", "@prisma/client",
        "typeorm", "sequelize", "mongoose", "knex", "drizzle-orm",
    }
    frontend_frameworks = {"react", "vue", "@angular/core", "svelte", "vite"}
    backend_hits = sorted(dependencies & backend_frameworks)
    frontend_hits = sorted(dependencies & frontend_frameworks)
    score = 45 + (35 if backend_hits else 0) - (10 if frontend_hits and not backend_hits else 0)
    evidence = ["package.json"]
    if backend_hits:
        evidence.append("backend-dependency:" + ",".join(backend_hits))
    if frontend_hits:
        evidence.append("frontend-dependency:" + ",".join(frontend_hits))
    scripts = package.get("scripts", {}) if isinstance(package.get("scripts"), dict) else {}
    if any(name in scripts for name in ("start", "serve", "dev", "api", "start:server")):
        score += 5
    if (root / "pnpm-lock.yaml").exists():
        runner, install = "pnpm", "pnpm install --frozen-lockfile"
    elif (root / "yarn.lock").exists():
        runner, install = "yarn", "yarn install --frozen-lockfile"
    elif (root / "bun.lockb").exists() or (root / "bun.lock").exists():
        runner, install = "bun", "bun install --frozen-lockfile"
    else:
        runner, install = "npm", "npm ci" if (root / "package-lock.json").exists() else "npm install"

    def run_script(*names: str) -> str | None:
        for name in names:
            if name in scripts:
                if runner == "npm" and name == "test":
                    return "npm test"
                return f"{runner} run {name}"
        return None

    notes: list[str] = []
    if frontend_hits and not backend_hits:
        notes.append("package.json looks frontend-heavy; confirm this is a backend package before selection")
    return Detection(
        "node",
        "Node.js",
        max(1, min(score, 100)),
        tuple(evidence),
        _command_map(
            install=install,
            lint=run_script("lint"),
            typecheck=run_script("typecheck", "type-check", "check:types"),
            unit_test=run_script("test:unit", "test"),
            integration_test=run_script("test:integration", "test:e2e"),
            build=run_script("build"),
            smoke_test=run_script("smoke", "test:smoke"),
        ),
        tuple(notes),
    )


def _maven(root: Path) -> Detection | None:
    if not (root / "pom.xml").exists():
        return None
    launcher = "./mvnw" if (root / "mvnw").exists() else "mvn"
    text = _read_text(root / "pom.xml").lower()
    score = 75 + (15 if "spring-boot" in text or "quarkus" in text or "micronaut" in text else 0)
    return Detection(
        "java-maven",
        "Java / Maven",
        min(score, 100),
        ("pom.xml",),
        _command_map(
            install=f"{launcher} -B dependency:go-offline",
            unit_test=f"{launcher} -B test",
            integration_test=f"{launcher} -B verify",
            build=f"{launcher} -B verify",
        ),
    )


def _gradle(root: Path) -> Detection | None:
    markers = _exists(root, "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts")
    if not markers:
        return None
    launcher = "./gradlew" if (root / "gradlew").exists() else "gradle"
    combined = "\n".join(_read_text(root / name) for name in markers).lower()
    notes: list[str] = []
    score = 70
    if "org.springframework.boot" in combined or "io.micronaut" in combined or "io.quarkus" in combined:
        score += 20
    if "com.android.application" in combined:
        score -= 35
        notes.append("Android plugin detected; confirm a backend module or select another adapter")
    return Detection(
        "java-gradle",
        "Java / Gradle",
        max(1, min(score, 100)),
        tuple(markers),
        _command_map(unit_test=f"{launcher} test", integration_test=f"{launcher} check", build=f"{launcher} build"),
        tuple(notes),
    )


def _go(root: Path) -> Detection | None:
    if not (root / "go.mod").exists():
        return None
    return Detection(
        "go",
        "Go",
        80,
        ("go.mod",),
        _command_map(install="go mod download", lint="go vet ./...", unit_test="go test ./...", build="go build ./..."),
    )


def _dotnet(root: Path) -> Detection | None:
    projects = _glob_exists(root, "*.sln") + _glob_exists(root, "*.csproj") + _glob_exists(root, "**/*.csproj")
    projects = sorted(set(projects))
    if not projects:
        return None
    return Detection(
        "dotnet",
        ".NET",
        75,
        tuple(projects[:20]),
        _command_map(install="dotnet restore", unit_test="dotnet test --no-restore", build="dotnet build --no-restore"),
    )


def _rust(root: Path) -> Detection | None:
    if not (root / "Cargo.toml").exists():
        return None
    text = _read_text(root / "Cargo.toml").lower()
    score = 65 + (20 if any(name in text for name in ("axum", "actix-web", "rocket", "warp", "poem")) else 0)
    return Detection(
        "rust",
        "Rust / Cargo",
        min(score, 100),
        ("Cargo.toml",),
        _command_map(
            install="cargo fetch --locked" if (root / "Cargo.lock").exists() else "cargo fetch",
            lint="cargo clippy --all-targets --all-features -- -D warnings",
            typecheck="cargo check --all-targets --all-features",
            unit_test="cargo test --all-features",
            build="cargo build --all-features",
        ),
    )


def _php(root: Path) -> Detection | None:
    path = root / "composer.json"
    if not path.exists():
        return None
    composer = _json_object(path)
    scripts = composer.get("scripts", {}) if isinstance(composer.get("scripts"), dict) else {}

    def composer_script(*names: str) -> str | None:
        return next((f"composer run-script {name}" for name in names if name in scripts), None)

    return Detection(
        "php-composer",
        "PHP / Composer",
        70,
        ("composer.json",),
        _command_map(
            install="composer install --no-interaction --prefer-dist",
            lint=composer_script("lint", "analyse", "phpstan"),
            unit_test=composer_script("test", "test:unit"),
            integration_test=composer_script("test:integration"),
            build=composer_script("build"),
        ),
    )


def _ruby(root: Path) -> Detection | None:
    if not (root / "Gemfile").exists():
        return None
    text = _read_text(root / "Gemfile").lower()
    unit = "bundle exec rspec" if "rspec" in text else "bundle exec rake test"
    return Detection(
        "ruby-bundler",
        "Ruby / Bundler",
        65 + (15 if "rails" in text or "sinatra" in text or "hanami" in text else 0),
        ("Gemfile",),
        _command_map(install="bundle install", lint="bundle exec rubocop" if "rubocop" in text else None, unit_test=unit),
    )


def _generic(_: Path) -> Detection:
    return Detection(
        "generic",
        "Generic backend",
        1,
        (),
        {},
        ("No supported build marker was selected; configure commands explicitly.",),
    )


ADAPTERS: dict[str, AdapterDefinition] = {
    item.adapter_id: item
    for item in (
        AdapterDefinition("python", "Python", _python, "Python projects using pyproject, requirements, Poetry, Pipenv, or uv."),
        AdapterDefinition("node", "Node.js", _node, "Node.js projects with package.json and package-manager scripts."),
        AdapterDefinition("java-maven", "Java / Maven", _maven, "Java projects built with Maven."),
        AdapterDefinition("java-gradle", "Java / Gradle", _gradle, "Java or Kotlin projects built with Gradle."),
        AdapterDefinition("go", "Go", _go, "Go modules."),
        AdapterDefinition("dotnet", ".NET", _dotnet, ".NET solutions and projects."),
        AdapterDefinition("rust", "Rust / Cargo", _rust, "Rust Cargo projects."),
        AdapterDefinition("php-composer", "PHP / Composer", _php, "PHP Composer projects."),
        AdapterDefinition("ruby-bundler", "Ruby / Bundler", _ruby, "Ruby Bundler projects."),
        AdapterDefinition("generic", "Generic backend", _generic, "Any backend with explicit custom commands."),
    )
}


def list_adapters() -> list[dict[str, Any]]:
    return [
        {"id": adapter.adapter_id, "label": adapter.label, "description": adapter.description}
        for adapter in ADAPTERS.values()
    ]


def detect_project(root: Path) -> dict[str, Any]:
    root = root.resolve()
    candidates: list[Detection] = []
    for adapter_id, adapter in ADAPTERS.items():
        if adapter_id == "generic":
            continue
        result = adapter.detect(root)
        if result is not None:
            candidates.append(result)
    candidates.sort(key=lambda item: (-item.score, item.adapter_id))
    recommended: str | None = None
    ambiguous = False
    if not candidates:
        recommended = "generic"
    elif len(candidates) == 1:
        recommended = candidates[0].adapter_id
    else:
        lead, runner_up = candidates[0], candidates[1]
        if lead.score >= 70 and lead.score - runner_up.score >= 20:
            recommended = lead.adapter_id
        else:
            ambiguous = True
    return {
        "schema_version": "0.2",
        "root": str(root),
        "detected_at": now_utc(),
        "candidates": [candidate.as_dict() for candidate in candidates],
        "recommended_adapter": recommended,
        "ambiguous": ambiguous,
        "requires_human_selection": ambiguous,
    }


def get_detection(probe: dict[str, Any], adapter_id: str) -> Detection:
    if adapter_id == "generic":
        return _generic(Path(probe.get("root", ".")))
    for candidate in probe.get("candidates", []):
        if candidate.get("id") == adapter_id:
            return Detection(
                adapter_id=adapter_id,
                label=str(candidate.get("label", adapter_id)),
                score=int(candidate.get("score", 0)),
                evidence=tuple(candidate.get("evidence", [])),
                commands={str(key): str(value) for key, value in candidate.get("commands", {}).items()},
                notes=tuple(candidate.get("notes", [])),
            )
    if adapter_id not in ADAPTERS:
        raise GateError(f"Unknown adapter: {adapter_id}")
    detected = ADAPTERS[adapter_id].detect(Path(probe.get("root", ".")))
    if detected is None:
        raise GateError(f"Adapter {adapter_id} does not match this project. Use --allow-mismatch to override.")
    return detected


def select_adapter(
    root: Path,
    *,
    requested: str | None = None,
    allow_mismatch: bool = False,
) -> tuple[dict[str, Any], Detection, str]:
    probe = detect_project(root)
    if requested:
        if requested not in ADAPTERS:
            raise GateError(f"Unknown adapter: {requested}")
        try:
            detection = get_detection(probe, requested)
        except GateError:
            if not allow_mismatch:
                raise
            definition = ADAPTERS[requested]
            detected = definition.detect(root)
            detection = detected or Detection(requested, definition.label, 0, (), {}, ("selected with --allow-mismatch",))
        return probe, detection, "explicit"
    if probe["ambiguous"]:
        names = ", ".join(candidate["id"] for candidate in probe["candidates"][:5])
        raise GateError(f"Backend adapter detection is ambiguous: {names}. Re-run with --adapter ADAPTER-ID.")
    recommended = str(probe["recommended_adapter"])
    return probe, get_detection(probe, recommended), "auto"


def project_configuration(
    root: Path,
    detection: Detection,
    selected_by: str,
    *,
    existing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    previous = existing or {}
    previous_commands = previous.get("commands", {}) if isinstance(previous.get("commands"), dict) else {}
    commands: dict[str, Any] = {}
    for key in COMMAND_KEYS:
        previous_value = previous_commands.get(key)
        if isinstance(previous_value, dict) and previous_value.get("source") == "human":
            commands[key] = previous_value
        elif key in detection.commands:
            commands[key] = {"command": detection.commands[key], "source": "detected", "enabled": True}
    return {
        "schema_version": "0.2",
        "project_root": str(root.resolve()),
        "adapter": {
            "id": detection.adapter_id,
            "label": detection.label,
            "selected_by": selected_by,
            "score": detection.score,
            "evidence": list(detection.evidence),
            "notes": list(detection.notes),
        },
        "commands": commands,
        "requires_command_configuration": detection.adapter_id == "generic" and not commands,
        "updated_at": now_utc(),
    }


def load_project_configuration(root: Path) -> dict[str, Any] | None:
    value = read_json(root / PROJECT_CONFIG_PATH)
    return value if isinstance(value, dict) else None


def write_project_configuration(root: Path, value: dict[str, Any]) -> None:
    write_json(root / PROJECT_CONFIG_PATH, value)


def configure_adapter(
    root: Path,
    adapter_id: str,
    command_values: list[str],
    *,
    allow_mismatch: bool = False,
) -> dict[str, Any]:
    probe, detection, selected_by = select_adapter(root, requested=adapter_id, allow_mismatch=allow_mismatch)
    existing = load_project_configuration(root)
    value = project_configuration(root, detection, selected_by, existing=existing)
    commands = value.setdefault("commands", {})
    for raw in command_values:
        if "=" not in raw:
            raise GateError(f"Invalid --command value: {raw}; expected NAME=COMMAND")
        name, command = raw.split("=", 1)
        name = name.strip()
        command = command.strip()
        if name not in COMMAND_KEYS:
            raise GateError(f"Unknown command name {name}; choose from {', '.join(COMMAND_KEYS)}")
        if not command:
            commands.pop(name, None)
        else:
            commands[name] = {"command": command, "source": "human", "enabled": True}
    value["requires_command_configuration"] = adapter_id == "generic" and not commands
    value["probe"] = {
        "recommended_adapter": probe["recommended_adapter"],
        "candidate_ids": [candidate["id"] for candidate in probe["candidates"]],
    }
    value["updated_at"] = now_utc()
    write_project_configuration(root, value)
    return value
