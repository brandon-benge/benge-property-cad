#!/usr/bin/env python3
"""Compatibility launcher for the managed updater under .tools/."""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent / ".tools"
if str(TOOLS_DIR) in sys.path:
    sys.path.remove(str(TOOLS_DIR))
sys.path.insert(0, str(TOOLS_DIR))

from update_tools import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
