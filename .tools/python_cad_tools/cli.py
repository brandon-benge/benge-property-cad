"""Command-line interface used by the managed root launcher."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .build import build_project, clean_generated
from .exceptions import CadBuildError

DEFAULT_FORMATS = ["step", "ifc", "glb", "drawings", "quantities"]


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Build headless CAD/BIM artifacts from the shared Python model.")
    value.add_argument("--format", action="append", choices=DEFAULT_FORMATS, dest="formats", help="Export one format; repeat for several.")
    value.add_argument("--validate-only", action="store_true", help="Build and validate the shared model without writing artifacts.")
    value.add_argument("--clean", action="store_true", help="Safely remove generated artifacts and exit.")
    value.add_argument("--include-fcstd", action="store_true", help="Also request optional FreeCADCmd-based FCStd compatibility output.")
    return value


def main(argv: list[str] | None = None, project_dir: Path | None = None) -> int:
    args = parser().parse_args(argv)
    root = (project_dir or Path.cwd()).resolve()
    try:
        if args.clean:
            clean_generated(root)
            print(f"Cleaned {root / 'generated'}")
            return 0
        formats = list(dict.fromkeys(args.formats or DEFAULT_FORMATS))
        if args.include_fcstd:
            formats.append("fcstd")
        paths = build_project(root, formats, validate_only=args.validate_only)
        if args.validate_only:
            print("Shared model validation passed.")
        else:
            print(f"Build passed: {len(paths)} artifacts generated under {root / 'generated'}")
        return 0
    except (CadBuildError, ImportError, RuntimeError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        return 1
