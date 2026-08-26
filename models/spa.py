"""Hot-tub shell, water, access steps, and platform; keep below 400 lines."""

from __future__ import annotations

from typing import Any

from python_cad_tools.elements import Dimensions
from python_cad_tools.geometry import box
from python_cad_tools.units import INCH, Length, to_mm

from models.shared import CUT_MARGIN, ZERO


def add_spa(builder: Any, cfg: Any, hot_tub_x: Length, hot_tub_y: Length) -> None:
    """Append the lower-deck hot-tub assembly in stable order."""
    hot_tub_z = cfg.LOWER_DECK_ELEVATION - (cfg.HOT_TUB_TOTAL_HEIGHT - cfg.HOT_TUB_ABOVE_DECK)
    hot_tub_outer = box(
        cfg.HOT_TUB_WIDTH,
        cfg.HOT_TUB_DEPTH,
        cfg.HOT_TUB_TOTAL_HEIGHT,
        origin=(hot_tub_x, hot_tub_y, hot_tub_z),
    )
    hot_tub_basin = box(
        cfg.HOT_TUB_WIDTH - 2 * cfg.HOT_TUB_RIM_WIDTH + CUT_MARGIN,
        cfg.HOT_TUB_DEPTH - 2 * cfg.HOT_TUB_RIM_WIDTH + CUT_MARGIN,
        cfg.HOT_TUB_TOTAL_HEIGHT - cfg.HOT_TUB_SHELL_THICKNESS + CUT_MARGIN,
        origin=(
            hot_tub_x + cfg.HOT_TUB_RIM_WIDTH - CUT_MARGIN / 2,
            hot_tub_y + cfg.HOT_TUB_RIM_WIDTH - CUT_MARGIN / 2,
            hot_tub_z + cfg.HOT_TUB_SHELL_THICKNESS - CUT_MARGIN / 2,
        ),
    )
    builder.add_shape(
        "feature",
        "HotTubSpaShell",
        hot_tub_outer.cut(hot_tub_basin),
        (0.08, 0.10, 0.12),
        Dimensions(to_mm(cfg.HOT_TUB_WIDTH), to_mm(cfg.HOT_TUB_DEPTH), to_mm(cfg.HOT_TUB_TOTAL_HEIGHT)),
        placement=(hot_tub_x, hot_tub_y, hot_tub_z),
        drawing_label=True,
        stable_id="complex.feature.hot_tub_placeholder",
        properties={
            "label": "Lower Deck Hot Tub Spa",
            "complex_type": "recessed_hot_tub_spa",
            "assembly_role": "spa_shell",
            "replaces_placeholder": True,
            "service_access_side": "south",
        },
    )
    builder.add_box(
        "pool",
        "HotTubWater",
        cfg.HOT_TUB_WIDTH - 2 * cfg.HOT_TUB_RIM_WIDTH,
        cfg.HOT_TUB_DEPTH - 2 * cfg.HOT_TUB_RIM_WIDTH,
        1 * INCH,
        hot_tub_x + cfg.HOT_TUB_RIM_WIDTH,
        hot_tub_y + cfg.HOT_TUB_RIM_WIDTH,
        hot_tub_z + cfg.HOT_TUB_TOTAL_HEIGHT - cfg.HOT_TUB_WATER_OFFSET,
        cfg.WATER_COLOR,
        parent_id="complex.feature.hot_tub_placeholder",
        properties={"complex_type": "spa_water_surface", "assembly_role": "water"},
    )
    for step_index in range(2):
        builder.add_box(
            "feature",
            f"HotTubAccessStep_{step_index + 1}",
            cfg.HOT_TUB_STEP_WIDTH,
            cfg.HOT_TUB_STEP_DEPTH,
            cfg.HOT_TUB_STEP_HEIGHT * (step_index + 1),
            hot_tub_x + (cfg.HOT_TUB_WIDTH - cfg.HOT_TUB_STEP_WIDTH) / 2,
            hot_tub_y - cfg.HOT_TUB_STEP_DEPTH * (2 - step_index),
            cfg.LOWER_DECK_ELEVATION,
            cfg.SKIRTING_COLOR,
            parent_id="complex.feature.hot_tub_placeholder",
            properties={"complex_type": "spa_access_step", "assembly_role": "access_step"},
        )
    builder.add_box(
        "structure",
        "HotTubPlatform",
        cfg.HOT_TUB_WIDTH,
        cfg.HOT_TUB_DEPTH,
        cfg.LOWER_DECK_ELEVATION,
        hot_tub_x,
        hot_tub_y,
        ZERO,
        (0.15, 0.15, 0.15),
    )
