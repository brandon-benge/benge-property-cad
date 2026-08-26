"""Ladder, slide, rungs, and belt-swing geometry for the play structure."""

from __future__ import annotations

import math
from typing import Any

from python_cad_tools.elements import Dimensions
from python_cad_tools.geometry import prism_between
from python_cad_tools.units import INCH, Length, mm, to_mm


def add_play_accessories(
    builder: Any,
    cfg: Any,
    swing_set_x: Length,
    swing_set_platform_y: Length,
    beam_y: Length,
    platform_top_z: Length,
    swing_set_id: str,
) -> None:
    ladder_rise = platform_top_z
    ladder_run = mm(math.sqrt(to_mm(cfg.SWING_SET_LADDER_LENGTH) ** 2 - to_mm(ladder_rise) ** 2))
    ladder_bottom_y = swing_set_platform_y - ladder_run
    ladder_top_y = swing_set_platform_y + 3 * INCH
    ladder_left_x = swing_set_x + 6 * INCH
    ladder_right_x = ladder_left_x + cfg.SWING_SET_LADDER_WIDTH
    for index, (x0, y0, z0, x1, y1, z1) in enumerate(
        (
            (ladder_left_x, ladder_bottom_y, 0 * INCH, ladder_left_x, ladder_top_y, platform_top_z),
            (ladder_right_x, ladder_bottom_y, 0 * INCH, ladder_right_x, ladder_top_y, platform_top_z),
        ),
        1,
    ):
        builder.add_shape(
            "site",
            f"EastYardSwingSetLadderRail_{index:02d}",
            prism_between((x0, y0, z0), (x1, y1, z1), 3 * INCH, 3 * INCH),
            cfg.SWING_SET_HARDWARE_COLOR,
            Dimensions(
                math.dist((to_mm(x0), to_mm(y0), to_mm(z0)), (to_mm(x1), to_mm(y1), to_mm(z1))),
                to_mm(3 * INCH),
                to_mm(3 * INCH),
            ),
            placement=(x0, y0, z0),
            parent_id=swing_set_id,
            properties={
                "complex_type": "playground_ladder",
                "assembly_role": "ladder_rail",
                "material": "pressure_treated_wood",
                "label": f"East Yard Swing Set Ladder Rail {index:02d}",
                "connected_to": swing_set_id,
            },
        )
    for index, rung_z in enumerate((12 * INCH, 24 * INCH, 36 * INCH, 48 * INCH), 1):
        rung_y = ladder_bottom_y + to_mm(rung_z) / to_mm(platform_top_z) * (ladder_top_y - ladder_bottom_y)
        builder.add_cylinder(
            "site",
            f"EastYardSwingSetLadderRung_{index:02d}",
            (ladder_left_x, rung_y, rung_z),
            (ladder_right_x, rung_y, rung_z),
            0.75 * INCH,
            cfg.SWING_SET_HARDWARE_COLOR,
            parent_id=swing_set_id,
            properties={
                "complex_type": "playground_ladder",
                "assembly_role": "ladder_rung",
                "material": "dark_metal",
                "label": f"East Yard Swing Set Ladder Rung {index:02d}",
                "connected_to": "complex.site.east_yard_swing_set_ladder_rail_01, complex.site.east_yard_swing_set_ladder_rail_02",
            },
        )
    slide_rise = platform_top_z - 6 * INCH
    slide_run = mm(math.sqrt(to_mm(cfg.SWING_SET_SLIDE_LENGTH) ** 2 - to_mm(slide_rise) ** 2))
    slide_start = (
        swing_set_x + cfg.SWING_SET_PLATFORM_LENGTH - cfg.SWING_SET_SLIDE_WIDTH / 2 - 6 * INCH,
        swing_set_platform_y + 3 * INCH,
        platform_top_z,
    )
    slide_end = (slide_start[0], swing_set_platform_y - slide_run, 6 * INCH)
    builder.add_shape(
        "site",
        "EastYardSwingSetSlide",
        prism_between(slide_start, slide_end, cfg.SWING_SET_SLIDE_WIDTH, 3 * INCH),
        cfg.SWING_SET_HARDWARE_COLOR,
        Dimensions(
            math.dist(tuple(to_mm(value) for value in slide_start), tuple(to_mm(value) for value in slide_end)),
            to_mm(cfg.SWING_SET_SLIDE_WIDTH),
            to_mm(3 * INCH),
        ),
        placement=slide_start,
        parent_id=swing_set_id,
        properties={
            "complex_type": "playground_slide",
            "assembly_role": "slide",
            "material": "dark_metal",
            "orientation": "south",
            "label": "East Yard Swing Set Slide",
            "connected_to": swing_set_id,
        },
    )
    swing_centers = (swing_set_x + 8.5 * cfg.FOOT, swing_set_x + 8.5 * cfg.FOOT + cfg.SWING_SET_SWING_SEAT_SPACING)
    seat_y = beam_y + cfg.SWING_SET_POST_SIZE / 2 - cfg.SWING_SET_SWING_SEAT_DEPTH / 2
    seat_z = cfg.SWING_SET_SWING_SEAT_HEIGHT
    for swing_index, center_x in enumerate(swing_centers, 1):
        seat_x = center_x - cfg.SWING_SET_SWING_SEAT_WIDTH / 2
        builder.add_box(
            "site",
            f"EastYardSwingSetBeltSwing_{swing_index:02d}Seat",
            cfg.SWING_SET_SWING_SEAT_WIDTH,
            cfg.SWING_SET_SWING_SEAT_DEPTH,
            cfg.SWING_SET_SWING_SEAT_THICKNESS,
            seat_x,
            seat_y,
            seat_z,
            cfg.SWING_SET_HARDWARE_COLOR,
            parent_id=swing_set_id,
            properties={
                "complex_type": "belt_swing",
                "assembly_role": "swing_seat",
                "material": "dark_metal",
                "swing_index": swing_index,
                "label": f"East Yard Swing Set Belt Swing {swing_index:02d} Seat",
                "connected_to": f"complex.site.east_yard_swing_set_belt_swing_{swing_index:02d}_chain_01, complex.site.east_yard_swing_set_belt_swing_{swing_index:02d}_chain_02",
            },
        )
        for chain_index, x_offset in enumerate((-6 * INCH, 6 * INCH), 1):
            chain_x, chain_y = center_x + x_offset, seat_y + cfg.SWING_SET_SWING_SEAT_DEPTH / 2
            builder.add_cylinder(
                "site",
                f"EastYardSwingSetBeltSwing_{swing_index:02d}Chain_{chain_index:02d}",
                (chain_x, chain_y, cfg.SWING_SET_BEAM_HEIGHT),
                (chain_x, chain_y, seat_z + cfg.SWING_SET_SWING_SEAT_THICKNESS),
                cfg.SWING_SET_SWING_CHAIN_DIAMETER / 2,
                cfg.SWING_SET_HARDWARE_COLOR,
                parent_id=swing_set_id,
                properties={
                    "complex_type": "belt_swing_chain",
                    "assembly_role": "swing_chain",
                    "material": "dark_metal",
                    "swing_index": swing_index,
                    "label": f"East Yard Swing Set Belt Swing {swing_index:02d} Chain {chain_index:02d}",
                    "connected_to": f"complex.site.east_yard_swing_set_top_beam, complex.site.east_yard_swing_set_belt_swing_{swing_index:02d}_seat",
                },
            )
