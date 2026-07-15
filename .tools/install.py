#!/usr/bin/env python3
"""Managed installer implementation for Python-first CAD projects."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

DEFAULT_SOURCE_URL = "https://github.com/brandon-benge/freecad_macro_project_template"
MANIFEST = Path(".tools/manifest.json")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a headless Python CAD project from this template.")
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL, help="Template directory, ZIP, GitHub repository, or ZIP URL.")
    parser.add_argument("--project-dir", required=True, help="Destination project directory.")
    parser.add_argument("--force", action="store_true", help="Allow a non-empty destination; project-owned files remain preserved.")
    parser.add_argument("--replace-project-files", action="store_true", help="Explicitly replace project-owned seed files from the template.")
    parser.add_argument("--force-guidance", action="store_true", help="Restore template-managed agents and installed-project guidance.")
    return parser.parse_args(argv)


def normalize_source_url(value: str) -> str:
    value = value.strip().rstrip("/")
    if value.endswith(".zip"):
        return value
    if value.startswith("https://github.com/") and "/archive/" not in value:
        return f"{value}/archive/refs/heads/main.zip"
    return value


def acquire_source(value: str, temp_dir: Path) -> Path:
    local = Path(value).expanduser()
    if local.is_dir():
        return local.resolve()
    archive_path = temp_dir / "template.zip"
    if local.is_file():
        shutil.copy2(local, archive_path)
    else:
        urllib.request.urlretrieve(normalize_source_url(value), archive_path)
    extract_dir = temp_dir / "source"
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(extract_dir)
    children = [path for path in extract_dir.iterdir() if path.is_dir()]
    return children[0] if len(children) == 1 else extract_dir


def load_manifest(source: Path) -> dict[str, Any]:
    path = source / MANIFEST
    if not path.exists():
        raise RuntimeError(f"Template manifest is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def copy_path(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        if destination.is_dir() and not destination.is_symlink():
            shutil.rmtree(destination)
        else:
            destination.unlink()
    if source.is_symlink():
        destination.symlink_to(os.readlink(source))
    elif source.is_dir():
        shutil.copytree(source, destination, symlinks=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    else:
        shutil.copy2(source, destination)


def spec(value: str | dict[str, str]) -> tuple[str, str]:
    if isinstance(value, str):
        return value, value
    return value["source"], value["destination"]


def install_from_source(
    source: Path,
    project: Path,
    *,
    force: bool = False,
    replace_project_files: bool = False,
    force_guidance: bool = False,
) -> dict[str, list[str]]:
    project.mkdir(parents=True, exist_ok=True)
    if any(project.iterdir()) and not force:
        raise RuntimeError(f"Project folder is not empty: {project}; use --force to preserve existing project files")
    manifest = load_manifest(source)
    report = {"managed": [], "seeded": [], "preserved": [], "guidance": []}
    for item in manifest["managed_files"]:
        source_name, destination_name = spec(item)
        copy_path(source / source_name, project / destination_name)
        report["managed"].append(destination_name)
    for item in manifest["project_seed_files"]:
        source_name, destination_name = spec(item)
        destination = project / destination_name
        if (destination.exists() or destination.is_symlink()) and not replace_project_files:
            report["preserved"].append(destination_name)
            continue
        copy_path(source / source_name, destination)
        report["seeded"].append(destination_name)
    for item in manifest["force_refreshable_guidance"]:
        source_name, destination_name = spec(item)
        destination = project / destination_name
        if destination.exists() and not force_guidance:
            report["preserved"].append(destination_name)
            continue
        copy_path(source / source_name, destination)
        report["guidance"].append(destination_name)
    ensure_agent_links(project)
    return report


def ensure_agent_links(project: Path) -> None:
    for directory in (".claude", ".codex", ".opencode"):
        tool_dir = project / directory
        tool_dir.mkdir(parents=True, exist_ok=True)
        for name, target in (("agents", "../.agents/agents"), ("skills", "../.agents/skills")):
            link = tool_dir / name
            if not link.exists() and not link.is_symlink():
                link.symlink_to(target)
    claude = project / "CLAUDE.md"
    if not claude.exists() and not claude.is_symlink():
        claude.symlink_to("AGENTS.md")


def print_report(report: dict[str, list[str]]) -> None:
    labels = {"managed": "Installed managed paths", "seeded": "Seeded project-owned paths", "guidance": "Installed managed guidance", "preserved": "Preserved existing paths"}
    for key in ("managed", "seeded", "guidance", "preserved"):
        if report[key]:
            print(f"\n{labels[key]}:")
            for path in report[key]:
                print(f"- {path}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    project = Path(args.project_dir).expanduser().resolve()
    with tempfile.TemporaryDirectory() as temp_name:
        source = acquire_source(args.source_url, Path(temp_name))
        report = install_from_source(
            source, project, force=args.force, replace_project_files=args.replace_project_files, force_guidance=args.force_guidance
        )
    print_report(report)
    print("\nSetup: python -m venv .venv && .venv/bin/pip install -r .tools/requirements/runtime.lock")
    print("Build: python build.py")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"Install failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
