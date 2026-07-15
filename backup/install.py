#!/usr/bin/env python3
"""Install a FreeCAD macro project from the remote template repo."""
import argparse
import os
import platform
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


DEFAULT_SOURCE_URL = "https://github.com/brandon-benge/freecad_macro_project_template"
MACRO_NAMES = (
    "Project.FCMacro",
    "Build.FCMacro",
    "InitRepo.FCMacro",
    "ConfigureParams.FCMacro",
    "Revert.FCMacro",
)
EXCLUDED_NAMES = {
    ".git",
    ".autocommit",
    ".macro_venvs",
    ".macro_env",
    "__pycache__",
}
EXCLUDED_SUFFIXES = {
    ".pyc",
    ".FCBak",
    ".FCStd",
}
USER_OWNED_NAMES = {
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
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a FreeCAD macro project and install launcher macros."
    )
    parser.add_argument(
        "--source-url",
        default=DEFAULT_SOURCE_URL,
        help="Remote template GitHub repo or ZIP URL. Defaults to this GitHub repo.",
    )
    parser.add_argument(
        "--project-dir",
        default=None,
        help="Destination folder for the new project.",
    )
    parser.add_argument(
        "--macro-dir",
        default=None,
        help="FreeCAD macro folder. Auto-detected when omitted.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow installing into an existing non-empty project folder.",
    )
    return parser.parse_args()


def prompt(message, default):
    suffix = f" [{default}]" if default else ""
    value = input(f"{message}{suffix}: ").strip()
    return value or default


def default_project_dir():
    return str(Path.cwd() / "freecad_macro_project")


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


def download_source(source_url, temp_dir):
    source_url = normalize_source_url(source_url)
    archive_path = temp_dir / "template.zip"
    local_source = Path(source_url).expanduser()
    if local_source.exists():
        print(f"Using local template archive:\n{local_source}")
        shutil.copy2(local_source, archive_path)
    else:
        print(f"Downloading template:\n{source_url}")
        urllib.request.urlretrieve(source_url, archive_path)

    extract_dir = temp_dir / "source"
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(extract_dir)

    children = [path for path in extract_dir.iterdir() if path.is_dir()]
    if len(children) == 1:
        return children[0]
    return extract_dir


def normalize_source_url(source_url):
    source_url = source_url.strip().rstrip("/")
    if source_url.endswith(".zip"):
        return source_url
    if source_url.startswith("https://github.com/") and "/archive/" not in source_url:
        return f"{source_url}/archive/refs/heads/main.zip"
    return source_url


def should_copy(path):
    if path.name in EXCLUDED_NAMES:
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return True


def copy_template(source_dir, project_dir, force):
    project_dir.mkdir(parents=True, exist_ok=True)
    if any(project_dir.iterdir()) and not force:
        raise RuntimeError(
            f"Project folder is not empty: {project_dir}\n"
            "Choose an empty folder or rerun with --force."
        )

    for item in source_dir.iterdir():
        if not should_copy(item):
            continue
        destination = project_dir / item.name
        if force and destination.exists() and item.name in USER_OWNED_NAMES:
            print(f"Preserved existing project file: {destination}")
            continue
        if item.is_dir():
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(item, destination, symlinks=True, ignore=ignore_template_files)
        else:
            shutil.copy2(item, destination)


def ignore_template_files(directory, names):
    ignored = set()
    for name in names:
        path = Path(directory) / name
        if not should_copy(path):
            ignored.add(name)
    return ignored


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
        print(f"Installed launcher: {launcher_path}")


def ensure_agent_links(project_dir):
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
        if not agents_link.exists() and not agents_link.is_symlink():
            agents_link.symlink_to(agents_target)
        if not skills_link.exists() and not skills_link.is_symlink():
            skills_link.symlink_to(skills_target)


def ensure_claude_guidance_link(project_dir):
    claude_link = project_dir / "CLAUDE.md"
    if not claude_link.exists() and not claude_link.is_symlink():
        claude_link.symlink_to("AGENTS.md")


def main():
    args = parse_args()
    project_dir = Path(
        args.project_dir
        or prompt("Project folder", default_project_dir())
    ).expanduser().resolve()
    macro_dir = Path(
        args.macro_dir
        or prompt("FreeCAD macro folder", str(default_macro_dir()))
    ).expanduser().resolve()

    with tempfile.TemporaryDirectory() as temp_name:
        source_dir = download_source(args.source_url, Path(temp_name))
        copy_template(source_dir, project_dir, args.force)

    ensure_agent_links(project_dir)
    ensure_claude_guidance_link(project_dir)
    install_launchers(project_dir, macro_dir)
    print("\nInstall complete.")
    print(f"Project folder: {project_dir}")
    print(f"FreeCAD macro folder: {macro_dir}")
    print("Open FreeCAD and run ConfigureParams.FCMacro, then InitRepo.FCMacro.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Install failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
