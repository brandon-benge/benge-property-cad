#!/usr/bin/env python3
"""Update managed FreeCAD macro tooling without touching project files."""
import argparse
import json
import os
import platform
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


DEFAULT_SOURCE_URL = "https://github.com/brandon-benge/freecad_macro_project_template"
MANIFEST_PATH = Path(".tools") / "manifest.json"
MACRO_NAMES = (
    "Project.FCMacro",
    "Build.FCMacro",
    "InitRepo.FCMacro",
    "ConfigureParams.FCMacro",
    "Revert.FCMacro",
)
DEFAULT_MANAGED_FILES = (
    ".tools/freecad_macro_tools",
    ".tools/macros",
    ".tools/manifest.json",
    "Project.FCMacro",
    "Build.FCMacro",
    "InitRepo.FCMacro",
    "ConfigureParams.FCMacro",
    "Revert.FCMacro",
    "build.py",
    "helpers.py",
    "macro_actions.py",
    "install.py",
    "update_tools.py",
)
DEFAULT_USER_FILES = (
    ".agents",
    ".claude",
    ".codex",
    ".opencode",
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "config.py",
    "model.py",
    "params.yaml",
)
DEFAULT_SEED_FILES = (
    ".agents",
    ".opencode",
    "AGENTS.md",
)
DEFAULT_FORCE_PROJECT_FILES = (
    ".agents",
    ".claude",
    ".codex",
    ".opencode",
    "AGENTS.md",
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Update only managed FreeCAD macro project tooling."
    )
    parser.add_argument(
        "--source-url",
        default=DEFAULT_SOURCE_URL,
        help="Remote template GitHub repo or ZIP URL. Defaults to this GitHub repo.",
    )
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Existing project folder to update. Defaults to the current folder.",
    )
    parser.add_argument(
        "--macro-dir",
        default=None,
        help="FreeCAD macro folder. Auto-detected when omitted.",
    )
    parser.add_argument(
        "--skip-launchers",
        action="store_true",
        help="Do not reinstall FreeCAD macro-folder launchers.",
    )
    parser.add_argument(
        "--force-project-files",
        action="store_true",
        help=(
            "Overwrite project-owned agent/config defaults from the template. "
            "Does not overwrite README.md, config.py, model.py, or params.yaml."
        ),
    )
    return parser.parse_args()


def normalize_source_url(source_url):
    source_url = source_url.strip().rstrip("/")
    if source_url.endswith(".zip"):
        return source_url
    if source_url.startswith("https://github.com/") and "/archive/" not in source_url:
        return f"{source_url}/archive/refs/heads/main.zip"
    return source_url


def download_source(source_url, temp_dir):
    source_url = normalize_source_url(source_url)
    archive_path = temp_dir / "template.zip"
    local_source = Path(source_url).expanduser()
    if local_source.exists():
        print(f"Using local tools archive:\n{local_source}")
        shutil.copy2(local_source, archive_path)
    else:
        print(f"Downloading tools:\n{source_url}")
        urllib.request.urlretrieve(source_url, archive_path)

    extract_dir = temp_dir / "source"
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(extract_dir)

    children = [path for path in extract_dir.iterdir() if path.is_dir()]
    if len(children) == 1:
        return children[0]
    return extract_dir


def read_manifest(source_dir):
    manifest_file = source_dir / MANIFEST_PATH
    if not manifest_file.exists():
        return {
            "managed_files": list(DEFAULT_MANAGED_FILES),
            "user_files": list(DEFAULT_USER_FILES),
        }
    with open(manifest_file, "r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def copy_managed_files(source_dir, project_dir, managed_files):
    updated = []
    for relative in managed_files:
        source = source_dir / relative
        destination = project_dir / relative
        if not source.exists():
            print(f"Skipped missing managed path from source: {relative}")
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        updated.append(relative)
    return updated


def seed_missing_project_files(source_dir, project_dir, seed_files):
    seeded = []
    for relative in seed_files:
        source = source_dir / relative
        destination = project_dir / relative
        if destination.exists() or destination.is_symlink():
            continue
        if not source.exists() and not source.is_symlink():
            print(f"Skipped missing seed path from source: {relative}")
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            destination.symlink_to(os.readlink(source))
        elif source.is_dir():
            shutil.copytree(source, destination, symlinks=True)
        else:
            shutil.copy2(source, destination)
        seeded.append(relative)
    return seeded


def copy_project_files(source_dir, project_dir, project_files):
    updated = []
    for relative in project_files:
        source = source_dir / relative
        destination = project_dir / relative
        if not source.exists() and not source.is_symlink():
            print(f"Skipped missing project path from source: {relative}")
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() or destination.is_symlink():
            if destination.is_dir() and not destination.is_symlink():
                shutil.rmtree(destination)
            else:
                destination.unlink()

        if source.is_symlink():
            destination.symlink_to(os.readlink(source))
        elif source.is_dir():
            shutil.copytree(source, destination, symlinks=True)
        else:
            shutil.copy2(source, destination)
        updated.append(relative)
    return updated


def default_macro_dir():
    system = platform.system()
    home = Path.home()
    if system == "Darwin":
        return home / "Library" / "Application Support" / "FreeCAD" / "Macro"
    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "FreeCAD" / "Macro"
        return home / "AppData" / "Roaming" / "FreeCAD" / "Macro"
    return home / ".local" / "share" / "FreeCAD" / "Macro"


def launcher_text(project_dir, macro_name):
    project_literal = repr(str(project_dir))
    macro_literal = repr(macro_name)
    return f"""import os
import runpy
import sys

PROJECT_DIR = {project_literal}
MACRO_NAME = {macro_literal}

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)
os.chdir(PROJECT_DIR)
runpy.run_path(os.path.join(PROJECT_DIR, MACRO_NAME), run_name="__main__")
"""


def install_launchers(project_dir, macro_dir):
    macro_dir.mkdir(parents=True, exist_ok=True)
    for macro_name in MACRO_NAMES:
        launcher_path = macro_dir / macro_name
        launcher_path.write_text(launcher_text(project_dir, macro_name), encoding="utf-8")
        print(f"Updated launcher: {launcher_path}")


def ensure_agent_links(project_dir, force=False):
    mappings = {
        ".claude": ("../.agents/agents", "../.agents/skills"),
        ".codex": ("../.agents/agents", "../.agents/skills"),
        ".opencode": ("../.agents/agents", "../.agents/skills"),
    }
    for directory, (agents_target, skills_target) in mappings.items():
        tool_dir = project_dir / directory
        tool_dir.mkdir(parents=True, exist_ok=True)
        agents_link = tool_dir / "agents"
        skills_link = tool_dir / "skills"
        for link_path in (agents_link, skills_link):
            if force and (link_path.exists() or link_path.is_symlink()):
                if link_path.is_dir() and not link_path.is_symlink():
                    shutil.rmtree(link_path)
                else:
                    link_path.unlink()
        if not agents_link.exists() and not agents_link.is_symlink():
            agents_link.symlink_to(agents_target)
        if not skills_link.exists() and not skills_link.is_symlink():
            skills_link.symlink_to(skills_target)


def ensure_claude_guidance_link(project_dir, force=False):
    claude_link = project_dir / "CLAUDE.md"
    if force and claude_link.exists() and not claude_link.is_symlink():
        claude_link.unlink()
    if not claude_link.exists() and not claude_link.is_symlink():
        claude_link.symlink_to("AGENTS.md")


def main():
    args = parse_args()
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        raise RuntimeError(f"Project folder does not exist: {project_dir}")

    with tempfile.TemporaryDirectory() as temp_name:
        source_dir = download_source(args.source_url, Path(temp_name))
        manifest = read_manifest(source_dir)
        updated = copy_managed_files(
            source_dir,
            project_dir,
            manifest.get("managed_files", DEFAULT_MANAGED_FILES),
        )
        preserved = manifest.get("user_files", DEFAULT_USER_FILES)
        seeded = seed_missing_project_files(
            source_dir,
            project_dir,
            manifest.get("seed_files", DEFAULT_SEED_FILES),
        )
        forced = []
        if args.force_project_files:
            forced = copy_project_files(
                source_dir,
                project_dir,
                manifest.get("force_project_files", DEFAULT_FORCE_PROJECT_FILES),
            )

    print("\nUpdated managed tool paths:")
    for relative in updated:
        print(f"- {relative}")

    if seeded:
        print("\nSeeded missing project-owned paths:")
        for relative in seeded:
            print(f"- {relative}")

    if forced:
        print("\nForce-updated project-owned defaults:")
        for relative in forced:
            print(f"- {relative}")

    if not args.skip_launchers:
        macro_dir = Path(args.macro_dir or default_macro_dir()).expanduser().resolve()
        install_launchers(project_dir, macro_dir)

    ensure_agent_links(project_dir, force=args.force_project_files)
    ensure_claude_guidance_link(project_dir, force=args.force_project_files)

    print("\nPreserved project-owned paths:")
    for relative in preserved:
        print(f"- {relative}")

    if args.force_project_files:
        print("\nTool update complete. Selected project-owned defaults were force-updated.")
    else:
        print("\nTool update complete. Existing project files were not modified.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Tool update failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
