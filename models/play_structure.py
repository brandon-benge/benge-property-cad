"""Swing-set platform, posts, header, top beam, and A-frame geometry."""

from __future__ import annotations

import math
from typing import Any

from python_cad_tools.elements import Dimensions
from python_cad_tools.geometry import prism_between
from python_cad_tools.units import INCH, Length, to_mm

from models.shared import ZERO


def add_play_structure(
    builder: Any,
    cfg: Any,
    swing_set_x: Length,
    swing_set_north_y: Length,
    swing_set_south_y: Length,
    swing_set_platform_y: Length,
) -> tuple[Length, Length, str]:
    """Append the platform and support frame, returning beam and platform heights."""
    swing_set_id = "complex.site.east_yard_swing_set"
    builder.add_box(
        "site",
        "East Yard Swing Set",
        cfg.SWING_SET_PLATFORM_LENGTH,
        cfg.SWING_SET_PLATFORM_DEPTH,
        cfg.SWING_SET_PLATFORM_THICKNESS,
        swing_set_x,
        swing_set_platform_y,
        cfg.SWING_SET_PLATFORM_HEIGHT,
        cfg.SKIRTING_COLOR,
        drawing_label=True,
        stable_id=swing_set_id,
        properties={
            "label": "East Yard Swing Set",
            "complex_type": "raised_play_platform",
            "assembly_role": "playground_structure",
            "finish": "pressure_treated_wood",
            "hardware_finish": "dark_metal",
            "orientation": "east_west",
            "components": "raised_platform, four_tower_posts, tower_header, top_beam, two_a_frame_legs, two_belt_swings, slide, ladder",
            "adjacent_to": "complex.site.unified_yard_grass",
            "clearance_from_pool_south_edge_mm": to_mm(cfg.SWING_SET_NEAR_EDGE_OFFSET),
            "south_footprint_limit_y_mm": to_mm(swing_set_south_y),
        },
    )
    post_positions = (
        (swing_set_x, swing_set_platform_y),
        (swing_set_x, swing_set_north_y - cfg.SWING_SET_POST_SIZE),
        (swing_set_x + cfg.SWING_SET_PLATFORM_LENGTH - cfg.SWING_SET_POST_SIZE, swing_set_platform_y),
        (
            swing_set_x + cfg.SWING_SET_PLATFORM_LENGTH - cfg.SWING_SET_POST_SIZE,
            swing_set_north_y - cfg.SWING_SET_POST_SIZE,
        ),
    )
    for index, (post_x, post_y) in enumerate(post_positions, 1):
        builder.add_box(
            "site",
            f"EastYardSwingSetSupportPost_{index:02d}",
            cfg.SWING_SET_POST_SIZE,
            cfg.SWING_SET_POST_SIZE,
            cfg.SWING_SET_POST_HEIGHT,
            post_x,
            post_y,
            ZERO,
            cfg.SKIRTING_COLOR,
            parent_id=swing_set_id,
            properties={
                "complex_type": "playground_support_post",
                "assembly_role": "support_post",
                "material": "pressure_treated_wood",
                "post_index": index,
                "label": f"East Yard Swing Set Tower Post {index:02d}",
                "connected_to": swing_set_id,
            },
        )
    beam_y = swing_set_platform_y + cfg.SWING_SET_PLATFORM_DEPTH / 2 - cfg.SWING_SET_POST_SIZE / 2
    beam_x = swing_set_x + cfg.SWING_SET_PLATFORM_LENGTH - cfg.SWING_SET_POST_SIZE
    beam_length = cfg.SWING_SET_LENGTH - cfg.SWING_SET_PLATFORM_LENGTH + cfg.SWING_SET_POST_SIZE
    builder.add_box(
        "site",
        "EastYardSwingSetTowerHeader",
        cfg.SWING_SET_POST_SIZE,
        cfg.SWING_SET_PLATFORM_DEPTH,
        cfg.SWING_SET_POST_SIZE,
        beam_x,
        swing_set_platform_y,
        cfg.SWING_SET_BEAM_HEIGHT,
        cfg.SKIRTING_COLOR,
        parent_id=swing_set_id,
        properties={
            "complex_type": "playground_support_beam",
            "assembly_role": "tower_header",
            "material": "pressure_treated_wood",
            "label": "East Yard Swing Set Tower Header",
            "connected_to": "complex.site.east_yard_swing_set_top_beam",
        },
    )
    builder.add_box(
        "site",
        "EastYardSwingSetTopBeam",
        beam_length,
        cfg.SWING_SET_POST_SIZE,
        cfg.SWING_SET_POST_SIZE,
        beam_x,
        beam_y,
        cfg.SWING_SET_BEAM_HEIGHT,
        cfg.SKIRTING_COLOR,
        parent_id=swing_set_id,
        properties={
            "complex_type": "playground_support_beam",
            "assembly_role": "overhead_beam",
            "material": "pressure_treated_wood",
            "orientation": "east_west",
            "label": "East Yard Swing Set Top Beam",
            "connected_to": "complex.site.east_yard_swing_set_tower_header, complex.site.east_yard_swing_set_a_frame_leg_01, complex.site.east_yard_swing_set_a_frame_leg_02",
        },
    )
    a_frame_top_x = swing_set_x + cfg.SWING_SET_LENGTH - cfg.SWING_SET_POST_SIZE / 2
    a_frame_top_y = beam_y + cfg.SWING_SET_POST_SIZE / 2
    for index, bottom_y in enumerate((swing_set_north_y - 9 * INCH, swing_set_platform_y + 9 * INCH), 1):
        builder.add_shape(
            "site",
            f"EastYardSwingSetAFrameLeg_{index:02d}",
            prism_between(
                (a_frame_top_x, bottom_y, ZERO),
                (a_frame_top_x, a_frame_top_y, cfg.SWING_SET_BEAM_HEIGHT),
                4 * INCH,
                4 * INCH,
            ),
            cfg.SKIRTING_COLOR,
            Dimensions(
                math.dist(
                    (to_mm(a_frame_top_x), to_mm(bottom_y), 0.0),
                    (to_mm(a_frame_top_x), to_mm(a_frame_top_y), to_mm(cfg.SWING_SET_BEAM_HEIGHT)),
                ),
                to_mm(4 * INCH),
                to_mm(4 * INCH),
            ),
            placement=(a_frame_top_x, bottom_y, ZERO),
            parent_id=swing_set_id,
            properties={
                "complex_type": "playground_support_post",
                "assembly_role": "a_frame_leg",
                "material": "dark_metal",
                "label": f"East Yard Swing Set A-Frame Leg {index:02d}",
                "connected_to": "complex.site.east_yard_swing_set_top_beam",
                "leg_index": index,
            },
        )
    return beam_y, cfg.SWING_SET_PLATFORM_HEIGHT + cfg.SWING_SET_PLATFORM_THICKNESS, swing_set_id
