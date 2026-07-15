"""Compatibility shim for command-line rebuilds."""
import os
import sys

TOOLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tools")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from freecad_macro_tools.build import *  # noqa: F401,F403


if __name__ == "__main__":
    rebuild()
