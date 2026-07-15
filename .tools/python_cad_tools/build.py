"""One-model build orchestration with staged artifact promotion."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from .context import BuildContext
from .exceptions import ModelValidationError
from .exporters import GlbExporter, IfcExporter, QuantityExporter, StepExporter
from .exporters.drawings import DrawingExporter
from .exporters.fcstd import FcstdExporter
from .manifests import write_manifests
from .validation import fatal_issues, validate_model

EXPORTERS: dict[str, type[Any]] = {
    "step": StepExporter,
    "ifc": IfcExporter,
    "glb": GlbExporter,
    "drawings": DrawingExporter,
    "quantities": QuantityExporter,
    "fcstd": FcstdExporter,
}


def build_project(project_dir: Path, formats: list[str], *, validate_only: bool = False) -> list[Path]:
    project_dir = project_dir.resolve()
    output_dir = project_dir / "generated"
    git_sha = _git_sha(project_dir)
    model = _build_shared_model(project_dir, output_dir, git_sha)
    issues = validate_model(model)
    fatals = fatal_issues(issues)
    if fatals:
        details = "\n".join(f"- {issue.code}: {issue.message} ({issue.element_id or 'model'})" for issue in fatals)
        raise ModelValidationError(f"Model validation failed:\n{details}")
    if validate_only:
        return []
    with tempfile.TemporaryDirectory(prefix=".generated-staging-", dir=project_dir) as temp_name:
        staging = Path(temp_name) / "generated"
        staging.mkdir()
        (staging / ".gitkeep").touch()
        generated: list[Path] = []
        for name in formats:
            generated.extend(EXPORTERS[name]().export(model, staging))
        generated.extend(write_manifests(model, staging, formats, issues, git_sha))
        _promote(staging, output_dir)
    return [output_dir / path.relative_to(staging) for path in generated]


def _build_shared_model(project_dir: Path, output_dir: Path, git_sha: str | None):
    previous_config = sys.modules.get("config")
    previous_model = sys.modules.get("model")
    sys.path.insert(0, str(project_dir))
    try:
        config = _load_project_module("config", project_dir / "config.py")
        sys.modules["config"] = config
        model_module = _load_project_module("model", project_dir / "model.py")
        sys.modules["model"] = model_module
        context = BuildContext(project_dir, output_dir, config, git_sha)
        return model_module.build_model(context)
    finally:
        sys.path.remove(str(project_dir))
        if previous_config is None:
            sys.modules.pop("config", None)
        else:
            sys.modules["config"] = previous_config
        if previous_model is None:
            sys.modules.pop("model", None)
        else:
            sys.modules["model"] = previous_model


def _load_project_module(name: str, path: Path):
    if not path.exists():
        raise ModelValidationError(f"Project source is missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ModelValidationError(f"Unable to load project module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def clean_generated(project_dir: Path) -> None:
    project_dir = project_dir.resolve()
    generated = project_dir / "generated"
    if generated.is_symlink():
        raise ModelValidationError("Refusing to clean a generated/ symlink")
    if generated.resolve() != (project_dir / "generated").resolve():
        raise ModelValidationError("Refusing to clean outside generated/")
    if generated.exists():
        for child in generated.iterdir():
            if child.name == ".gitkeep":
                continue
            if child.is_symlink() or child.is_file():
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child)
    else:
        generated.mkdir()
        (generated / ".gitkeep").touch()


def _promote(staging: Path, output_dir: Path) -> None:
    if output_dir.is_symlink():
        raise ModelValidationError("Refusing to replace a generated/ symlink")
    backup = output_dir.with_name(".generated-previous")
    if backup.exists():
        shutil.rmtree(backup)
    if output_dir.exists():
        os.replace(output_dir, backup)
    try:
        os.replace(staging, output_dir)
    except Exception:
        if backup.exists() and not output_dir.exists():
            os.replace(backup, output_dir)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def _git_sha(project_dir: Path) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=project_dir, text=True, capture_output=True, check=False
    )
    return completed.stdout.strip() if completed.returncode == 0 else None
