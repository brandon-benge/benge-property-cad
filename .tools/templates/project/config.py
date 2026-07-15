"""Project-owned typed dimensions, materials, colors, and export settings."""

from __future__ import annotations

from dataclasses import dataclass

from python_cad_tools.units import FOOT, INCH, MM, Length

PROJECT_NAME = "ProjectModel"
BASE_LENGTH = 10 * FOOT
BASE_WIDTH = 6 * FOOT
BASE_THICKNESS = 6 * INCH
BLOCK_LENGTH = 4 * FOOT
BLOCK_WIDTH = 3 * FOOT
BLOCK_HEIGHT = 2 * FOOT
BASE_COLOR = (0.65, 0.65, 0.62)
PRIMARY_COLOR = (0.25, 0.42, 0.58)
ACCENT_COLOR = (0.12, 0.12, 0.12)


@dataclass(frozen=True, slots=True)
class ExportSettings:
    step_schema_preference: str = "AP242"
    glb_linear_deflection_mm: float = 0.5
    glb_angular_deflection_rad: float = 0.25
    include_reference_geometry_in_glb: bool = False
    drawing_dimension_denominator: int = 16


EXPORTS = ExportSettings()

__all__ = [
    "ACCENT_COLOR", "BASE_COLOR", "BASE_LENGTH", "BASE_THICKNESS", "BASE_WIDTH",
    "BLOCK_HEIGHT", "BLOCK_LENGTH", "BLOCK_WIDTH", "EXPORTS", "FOOT", "INCH",
    "Length", "MM", "PRIMARY_COLOR", "PROJECT_NAME",
]
