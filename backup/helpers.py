"""Compatibility shim for existing model.py imports."""
import os
import sys

TOOLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tools")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from freecad_macro_tools.helpers import *  # noqa: F401,F403
