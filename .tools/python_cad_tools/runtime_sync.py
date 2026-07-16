"""Synchronize the active Python environment with the managed runtime lock."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Callable
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

PIN_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s;]+)$")
LEGACY_OCP_DISTRIBUTIONS = ("cadquery-ocp", "cadquery-vtk")


def locked_versions(lock_path: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    for raw_line in lock_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = PIN_PATTERN.fullmatch(line)
        if not match:
            raise RuntimeError(f"Runtime lock entry is not an exact package pin: {line}")
        pins[match.group(1)] = match.group(2)
    if not pins:
        raise RuntimeError(f"Runtime lock contains no package pins: {lock_path}")
    return pins


def version_mismatches(
    pins: dict[str, str],
    *,
    get_version: Callable[[str], str] | None = None,
) -> list[str]:
    resolve_version = get_version or version
    mismatches: list[str] = []
    for name, expected in pins.items():
        try:
            installed = resolve_version(name)
        except PackageNotFoundError:
            mismatches.append(f"{name}: missing (requires {expected})")
        else:
            if installed != expected:
                mismatches.append(f"{name}: {installed} (requires {expected})")
    return mismatches


def installed_legacy_ocp(
    *,
    get_version: Callable[[str], str] | None = None,
) -> list[str]:
    resolve_version = get_version or version
    installed: list[str] = []
    for name in LEGACY_OCP_DISTRIBUTIONS:
        try:
            resolve_version(name)
        except PackageNotFoundError:
            continue
        installed.append(name)
    return installed


def in_virtual_environment() -> bool:
    return sys.prefix != sys.base_prefix


def synchronize(lock_path: Path) -> bool:
    """Install the lock when pinned versions or package consistency have drifted."""
    if not lock_path.is_file():
        raise RuntimeError(f"Managed runtime lock is missing: {lock_path}")
    pins = locked_versions(lock_path)
    mismatches = version_mismatches(pins)
    check = subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        text=True,
        capture_output=True,
        check=False,
    )
    if not mismatches and check.returncode == 0:
        return False
    if not in_virtual_environment():
        details = "; ".join(mismatches) or (check.stdout + check.stderr).strip()
        raise RuntimeError(
            "Runtime dependencies need synchronization, but the selected Python is not "
            f"inside a virtual environment ({details}). Create .venv and install {lock_path}."
        )

    print("Synchronizing the project virtual environment with the managed runtime lock...")
    legacy = installed_legacy_ocp() if "cadquery-ocp-novtk" in pins else []
    if legacy:
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", *legacy],
            check=True,
        )
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(lock_path)],
        check=True,
    )
    subprocess.run([sys.executable, "-m", "pip", "check"], check=True)
    remaining = version_mismatches(pins)
    if remaining:
        raise RuntimeError("Runtime synchronization did not satisfy the lock: " + "; ".join(remaining))
    return True


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lock_path", type=Path, help="Managed requirements lock to enforce")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    changed = synchronize(args.lock_path.expanduser().resolve())
    print("Runtime dependencies synchronized." if changed else "Runtime dependencies already match the managed lock.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"Runtime dependency synchronization failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
