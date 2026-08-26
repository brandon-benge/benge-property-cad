"""Skirt and stair lighting collection; keep this focused module under 400 lines."""

from __future__ import annotations

import math
from typing import Any

from python_cad_tools.units import INCH, Length, mm, to_mm

import config as cfg
from models.shared import ZERO, Point2
from models.shared import slug as _slug
from models.stairs import line_frame

LIGHT_COLOR = (0.95, 0.85, 0.10)


def _fixture_offsets(run_length: Length, cfg_module: Any = cfg) -> list[float]:
    run_mm = to_mm(run_length)
    inset_mm = min(to_mm(cfg_module.DECK_LIGHT_END_INSET), run_mm / 2)
    usable_mm = max(0.0, run_mm - 2 * inset_mm)
    intervals = max(1, math.ceil(usable_mm / to_mm(cfg_module.DECK_LIGHT_MAX_SPACING)))
    return [inset_mm + usable_mm * index / intervals for index in range(intervals + 1)]


def add_skirt_lights(builder: Any, skirt_thickness: Length, lower_x: Length, cfg_module: Any = cfg) -> None:
    def add_lights(name: str, x: Length, y: Length, run_length: Length, z: Length, *, axis: str) -> None:
        for index, offset_mm in enumerate(_fixture_offsets(run_length, cfg_module), start=1):
            builder.add_box(
                "skirting",
                f"{name}Light_{index:02d}",
                cfg_module.DECK_LIGHT_PROJECTION if axis == "y" else cfg_module.DECK_LIGHT_FACE_WIDTH,
                cfg_module.DECK_LIGHT_FACE_WIDTH if axis == "y" else cfg_module.DECK_LIGHT_PROJECTION,
                cfg_module.DECK_LIGHT_FACE_HEIGHT,
                mm(to_mm(x) if axis == "y" else to_mm(x) + offset_mm - to_mm(cfg_module.DECK_LIGHT_FACE_WIDTH) / 2),
                mm(to_mm(y) + offset_mm - to_mm(cfg_module.DECK_LIGHT_FACE_WIDTH) / 2 if axis == "y" else to_mm(y)),
                z,
                LIGHT_COLOR,
                properties={
                    "complex_type": "deck_skirt_light",
                    "assembly_role": "low_voltage_perimeter_lighting",
                    "illuminates": f"complex.skirting.{_slug(name)}",
                    "color_temperature_k": 2700,
                    "voltage_v": 12,
                    "aim": "downward",
                },
            )

    z = cfg_module.DECK_LIGHT_HEIGHT_ABOVE_GRADE
    add_lights(
        "UpperDeckFrontSkirt",
        ZERO,
        -cfg_module.UPPER_DECK_DEPTH - skirt_thickness - cfg_module.DECK_LIGHT_PROJECTION,
        cfg_module.UPPER_DECK_WIDTH,
        z,
        axis="x",
    )
    add_lights(
        "UpperDeckLeftSkirt",
        -skirt_thickness - cfg_module.DECK_LIGHT_PROJECTION,
        -cfg_module.UPPER_DECK_DEPTH,
        cfg_module.UPPER_DECK_DEPTH,
        z,
        axis="y",
    )
    add_lights(
        "UpperDeckRightSkirt",
        cfg_module.UPPER_DECK_WIDTH + skirt_thickness,
        -cfg_module.UPPER_DECK_DEPTH,
        cfg_module.UPPER_DECK_DEPTH,
        z,
        axis="y",
    )
    add_lights(
        "LowerDeckRightSkirt",
        lower_x + cfg_module.LOWER_DECK_WIDTH + skirt_thickness,
        -cfg_module.LOWER_DECK_DEPTH,
        cfg_module.LOWER_DECK_DEPTH,
        z,
        axis="y",
    )
    add_lights(
        "LowerDeckLeftSkirt",
        -skirt_thickness - cfg_module.DECK_LIGHT_PROJECTION,
        -cfg_module.UPPER_DECK_DEPTH,
        cfg_module.LOWER_DECK_DEPTH - cfg_module.UPPER_DECK_DEPTH,
        z,
        axis="y",
    )


def add_stair_lights(
    builder: Any,
    prefix: str,
    start: Point2,
    end: Point2,
    start_z: Length,
    end_z: Length,
    width: Length = cfg.STAIR_WIDTH,
    axis: str = "y",
    cfg_module: Any = cfg,
) -> None:
    dx, dy, _run, _px, _py = line_frame(start, end)
    steps = max(1, math.ceil(abs(to_mm(start_z - end_z)) / to_mm(cfg_module.MAX_RISER)))
    rise = to_mm(start_z - end_z) / steps
    for index in range(1, steps + 1):
        ratio = index / steps
        center_x = to_mm(start[0]) + dx * ratio
        center_y = to_mm(start[1]) + dy * ratio
        tread_z = to_mm(start_z) - rise * index
        lateral_ratios = (0.25, 0.75) if width > cfg_module.WIDE_STAIR_LIGHT_THRESHOLD else (0.5,)
        for fixture_index, lateral_ratio in enumerate(lateral_ratios, start=1):
            if axis == "y":
                light_x = mm(
                    center_x
                    - to_mm(width) / 2
                    + to_mm(width) * lateral_ratio
                    - to_mm(cfg_module.DECK_LIGHT_FACE_WIDTH) / 2
                )
                light_y = mm(center_y - to_mm(cfg_module.DECK_LIGHT_PROJECTION) / 2)
                light_size_x, light_size_y = cfg_module.DECK_LIGHT_FACE_WIDTH, cfg_module.DECK_LIGHT_PROJECTION
            else:
                light_x = mm(center_x - to_mm(cfg_module.DECK_LIGHT_PROJECTION) / 2)
                light_y = mm(
                    center_y
                    - to_mm(width) / 2
                    + to_mm(width) * lateral_ratio
                    - to_mm(cfg_module.DECK_LIGHT_FACE_WIDTH) / 2
                )
                light_size_x, light_size_y = cfg_module.DECK_LIGHT_PROJECTION, cfg_module.DECK_LIGHT_FACE_WIDTH
            builder.add_box(
                "stair",
                f"{prefix}RiserLight_{index:02d}_{fixture_index:02d}",
                light_size_x,
                light_size_y,
                cfg_module.DECK_LIGHT_FACE_HEIGHT,
                light_x,
                light_y,
                mm(tread_z + to_mm(INCH)),
                LIGHT_COLOR,
                properties={
                    "complex_type": "stair_riser_light",
                    "assembly_role": "low_voltage_step_lighting",
                    "illuminates": f"complex.stair.{_slug(prefix)}_riser_{index:02d}",
                    "color_temperature_k": 2700,
                    "voltage_v": 12,
                    "aim": "downward",
                },
            )
