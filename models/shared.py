"""Shared property-model contract kept below 400 lines.

Constants, type aliases, IFC mapping, stable slugs, boolean helpers, and the
material registry live here so collection modules can share them without
importing the orchestration module.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from python_cad_tools.elements import DesignElement, IfcMapping, MaterialSpec
from python_cad_tools.geometry import box, cylinder_between
from python_cad_tools.units import MM, Length, to_mm

import config as cfg

Color = tuple[float, float, float]
Point3 = tuple[Length, Length, Length]
Point2 = tuple[Length, Length]
ZERO = 0 * MM
CUT_MARGIN = 1 * MM


def _capsule_solid(length: Length, width: Length, height: Length, origin: Point3 = (ZERO, ZERO, ZERO)) -> Any:
    if to_mm(length) < to_mm(width):
        raise ValueError("Capsule length must be at least its width")
    x, y, z = origin
    radius = width / 2
    body_length = length - width
    center = box(body_length, width, height, origin=(x + radius, y, z))
    left_cap = cylinder_between((x + radius, y + radius, z), (x + radius, y + radius, z + height), radius)
    right_cap = cylinder_between(
        (x + length - radius, y + radius, z), (x + length - radius, y + radius, z + height), radius
    )
    return center.fuse(left_cap, right_cap)


def _cut_capsule(length: Length, width: Length, height: Length, origin: Point3) -> Any:
    margin = CUT_MARGIN / 2
    return _capsule_solid(
        length + CUT_MARGIN,
        width + CUT_MARGIN,
        height + CUT_MARGIN,
        origin=(origin[0] - margin, origin[1] - margin, origin[2] - margin),
    )


def _cut_box(length: Length, depth: Length, height: Length, origin: Point3) -> Any:
    """Return a slightly oversized cutter box to avoid coplanar booleans."""
    margin = CUT_MARGIN / 2
    return box(
        length + CUT_MARGIN,
        depth + CUT_MARGIN,
        height + CUT_MARGIN,
        origin=(origin[0] - margin, origin[1] - margin, origin[2] - margin),
    )


@dataclass
class ModelState:
    """The single mutable collection state shared by all model phases."""

    elements: list[DesignElement] = field(default_factory=list)
    materials: dict[tuple[str, Color], MaterialSpec] = field(default_factory=dict)
    values: dict[str, Any] = field(default_factory=dict)


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value).lower()).strip("_")


def ifc_mapping(category: str, name: str) -> IfcMapping:
    mappings = {
        "deck-board": ("IfcSlab", "FLOOR"),
        "railing": ("IfcRailing", "GUARDRAIL"),
        "structure": ("IfcSlab", "BASESLAB"),
        "house": ("IfcWall", "STANDARD"),
        "pool": ("IfcBuildingElementProxy", "ELEMENT"),
        "rock-bed": ("IfcBuildingElementProxy", "ELEMENT"),
    }
    if category == "deck-framing":
        return (
            IfcMapping("IfcColumn", "COLUMN")
            if "Post" in name
            else IfcMapping("IfcBeam", "JOIST" if "Joist" in name else "BEAM")
        )
    if category == "roof":
        return IfcMapping("IfcRoof", "SHED_ROOF") if "RoofCover" in name else IfcMapping("IfcMember", "MEMBER")
    if category == "roof-framing":
        if "Rafter" in name:
            return IfcMapping("IfcMember", "RAFTER")
        return IfcMapping("IfcColumn", "COLUMN") if "Post" in name else IfcMapping("IfcBeam", "BEAM")
    if category == "skirting":
        return (
            IfcMapping("IfcLightFixture", "POINTSOURCE")
            if "Light" in name
            else IfcMapping("IfcCovering", "SKIRTINGBOARD")
        )
    if category == "stair":
        return IfcMapping("IfcLightFixture", "POINTSOURCE") if "Light" in name else IfcMapping("IfcMember", "PLATE")
    if category == "fireplace":
        if name in {"FireplaceMasonryBody", "FireplaceChimney"}:
            return IfcMapping("IfcWall", "STANDARD")
        if name == "FireplaceMantel":
            return IfcMapping("IfcMember", "MEMBER")
        if name == "FireplaceChimneyCap":
            return IfcMapping("IfcCovering", "ROOFING")
        return IfcMapping(
            "IfcBuildingElementProxy",
            "PROVISIONFORVOID" if name in {"FireplaceOpening", "FireplaceFlueHole"} else "ELEMENT",
        )
    if category == "shed":
        if "Door" in name:
            return IfcMapping("IfcDoor", "DOOR")
        if "Roof" in name:
            return IfcMapping("IfcRoof", "GABLE_ROOF")
        if "Slab" in name or "Floor" in name:
            return IfcMapping("IfcSlab", "BASESLAB")
        if "Wall" in name or "Siding" in name:
            return IfcMapping("IfcWall", "STANDARD")
        return IfcMapping("IfcMember", "MEMBER")
    if category == "feature":
        if name == "SlidingDoor":
            return IfcMapping("IfcDoor", "DOOR")
        if name.startswith("SlidingDoorFrame") or name == "SlidingDoorMeetingRail":
            return IfcMapping("IfcMember", "MULLION")
    if category == "pool-equipment":
        return IfcMapping("IfcSlab", "BASESLAB") if "Slab" in name else IfcMapping("IfcBuildingElementProxy", "ELEMENT")
    if category == "outdoor-kitchen":
        if "SinkBasin" in name:
            return IfcMapping("IfcSanitaryTerminal", "SINK")
        if "Cabinet" in name:
            return IfcMapping("IfcFurniture", "USERDEFINED")
    if category == "site" and "Fence" in name:
        return IfcMapping("IfcRailing", "BALUSTRADE")
    if category in {"feature", "pool", "pool-equipment", "outdoor-kitchen", "site", "rock-bed"}:
        return IfcMapping("IfcBuildingElementProxy", "ELEMENT")
    if category in mappings:
        return IfcMapping(*mappings[category])
    raise ValueError(f"No IFC mapping defined for {category!r} element {name!r}")


TREE_GREEN: Color = (0.0, 0.45, 0.15)
TREE_BROWN: Color = (0.40, 0.25, 0.10)
MATERIAL_REGISTRY: dict[tuple[str, Color], tuple[str, float | None]] = {
    ("deck-board", cfg.DECK_COLOR): ("Composite Decking", 700.0),
    ("deck-framing", cfg.SKIRTING_COLOR): ("Pressure-Treated Lumber", 500.0),
    ("deck-framing", cfg.RAILING_COLOR): ("Pressure-Treated Lumber", 500.0),
    ("roof", cfg.RAILING_COLOR): ("Roof Fascia Assembly", 500.0),
    ("roof", (0.18, 0.20, 0.22)): ("Roof Cover Assembly", 50.0),
    ("roof-framing", (0.92, 0.92, 0.90)): ("Dimensional Lumber", 500.0),
    ("roof-framing", cfg.RAILING_COLOR): ("Roof Beam Assembly", 500.0),
    ("feature", (0.55, 0.70, 0.82)): ("Glass Door Assembly", 2500.0),
    ("feature", (0.08, 0.10, 0.12)): ("Hot Tub Shell", 150.0),
    ("feature", cfg.RAILING_COLOR): ("Ceiling Fan Assembly", 500.0),
    ("feature", cfg.SKIRTING_COLOR): ("Fan Blade (Wood)", 600.0),
    ("fireplace", cfg.BRICK_COLOR): ("Brick Masonry", 2000.0),
    ("fireplace", (0.90, 0.28, 0.08)): ("Electric Fireplace Insert", 500.0),
    ("fireplace", (0.02, 0.02, 0.025)): ("Flat Screen TV", 300.0),
    ("fireplace", (0.03, 0.03, 0.03)): ("Fireplace Opening (Void)", 100.0),
    ("fireplace", (0.10, 0.10, 0.10)): ("Metal Chimney Cap", 500.0),
    ("fireplace", (0.02, 0.02, 0.02)): ("Chimney Flue Opening", 100.0),
    ("skirting", (0.30, 0.25, 0.20)): ("Access Panel (Wood)", 600.0),
    ("house", cfg.HOUSE_COLOR): ("Mixed Wall Assembly", 300.0),
    ("outdoor-kitchen", (0.45, 0.45, 0.42)): ("Granite Countertop", 2400.0),
    ("outdoor-kitchen", (0.05, 0.05, 0.05)): ("Stainless Steel Grill", 2700.0),
    ("outdoor-kitchen", (0.75, 0.75, 0.72)): ("Chrome Faucet", 2700.0),
    ("outdoor-kitchen", (0.12, 0.12, 0.12)): ("Cabinet Box (Wood)", 600.0),
    ("outdoor-kitchen", (0.12, 0.15, 0.16)): ("Stainless Steel Sink", 2700.0),
    ("outdoor-kitchen", (0.22, 0.22, 0.22)): ("Cabinet Door (Wood)", 600.0),
    ("pool", cfg.WATER_COLOR): ("Water", 1000.0),
    ("pool", cfg.POOL_SHELL_COLOR): ("Pool Shell", 450.0),
    ("railing", cfg.RAILING_COLOR): ("Wood/Metal Railing", 500.0),
    ("site", cfg.SKIRTING_COLOR): ("Pressure-Treated Wood", 500.0),
    ("site", cfg.SWING_SET_HARDWARE_COLOR): ("Dark Metal Hardware", 7850.0),
    ("site", cfg.PAVER_COLOR): ("Concrete Pavers", 2400.0),
    ("site", cfg.TILE_COLOR): ("Pool Tile", 2300.0),
    ("site", cfg.GRASS_COLOR): ("Turf Grass", 50.0),
    ("site", cfg.ROCK_COLOR): ("Landscape Rock", 1650.0),
    ("site", cfg.FENCE_COLOR): ("Black Powder-Coated Aluminum Fence", 2700.0),
    ("site", cfg.PROPERTY_LINE_FENCE_COLOR): ("White Privacy Fence Panel", 500.0),
    ("rock-bed", cfg.ROCK_COLOR): ("Landscape Rock Bed", 1650.0),
    ("pool-equipment", (0.50, 0.50, 0.50)): ("Concrete Equipment Pad", 2400.0),
    ("pool-equipment", (0.15, 0.15, 0.15)): ("Pool Pump", 500.0),
    ("pool-equipment", (0.25, 0.25, 0.25)): ("Pool Heater", 800.0),
    ("pool-equipment", (0.35, 0.35, 0.35)): ("Pool Filter", 600.0),
    ("site", TREE_GREEN): ("Evergreen Tree (Conceptual)", None),
    ("site", TREE_BROWN): ("Tree Trunk (Conceptual)", None),
    ("shed", cfg.SHED_SIDING_COLOR): ("Painted Wood Siding", 550.0),
    ("shed", cfg.SHED_TRIM_COLOR): ("Painted Wood Trim", 550.0),
    ("shed", cfg.SHED_ROOF_COLOR): ("Asphalt Shingle Roof", 50.0),
    ("shed", (0.15, 0.15, 0.15)): ("Concrete Shed Slab", 2400.0),
    ("skirting", cfg.SKIRTING_COLOR): ("Pressure-Treated Skirting", 500.0),
    ("skirting", (0.95, 0.85, 0.10)): ("Low-Voltage LED Deck Light", 100.0),
    ("stair", cfg.DECK_COLOR): ("Composite Tread", 700.0),
    ("stair", cfg.SKIRTING_COLOR): ("Framing Lumber", 500.0),
    ("stair", (0.95, 0.85, 0.10)): ("LED Step Light", 100.0),
    ("structure", (0.15, 0.15, 0.15)): ("Concrete Slab", 2400.0),
}

_slug = slug
_ifc_mapping = ifc_mapping
