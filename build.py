#!/usr/bin/env python3
"""Managed launcher for the headless Python CAD build."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
TOOLS_DIR = PROJECT_DIR / ".tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

try:
    from python_cad_tools.cli import main  # noqa: E402
except ModuleNotFoundError as error:
    candidates = (
        PROJECT_DIR / ".venv" / "bin" / "python",
        PROJECT_DIR / ".venv" / "Scripts" / "python.exe",
    )
    environment_python = next((path for path in candidates if path.exists()), None)
    if environment_python and environment_python.absolute() != Path(sys.executable).absolute():
        os.execv(str(environment_python), [str(environment_python), str(__file__), *sys.argv[1:]])
    raise SystemExit(
        "CAD runtime dependencies are unavailable. Create .venv and install "
        ".tools/requirements/runtime.lock, then rerun python build.py."
    ) from error

if __name__ == "__main__":
    raise SystemExit(main(project_dir=PROJECT_DIR))
