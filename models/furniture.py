"""Deck furniture geometry; keep this focused module below 400 lines.

The first item here is the small outdoor side table standing on the upper deck
beside the fireplace lounge: a tabletop slab on four square legs with a lower
storage shelf between them.  It is placed from the fireplace datum only (face on
X, front edge on Y) because the model has no lounge seating geometry yet.
"""

from __future__ import annotations

from typing import Any

from python_cad_tools.units import to_mm


def add_furniture(builder: Any, cfg: Any, fireplace_face_x: Any, fireplace_front_y: Any) -> None:
    """Append the upper-deck side table beside the fireplace lounge."""
    clearance = cfg.SIDE_TABLE_CLEARANCE_FROM_FIREPLACE
    width = cfg.SIDE_TABLE_WIDTH
    depth = cfg.SIDE_TABLE_DEPTH
    leg_size = cfg.SIDE_TABLE_LEG_SIZE
    deck_z = cfg.UPPER_DECK_ELEVATION

    # One clearance out from the fireplace face on X, and the same distance
    # forward of its front edge on Y, on open upper-deck boards.
    table_x = fireplace_face_x + clearance
    table_near_y = fireplace_front_y - clearance
    table_y = table_near_y - depth

    top_thickness = cfg.SIDE_TABLE_TOP_THICKNESS
    top_z = deck_z + cfg.SIDE_TABLE_HEIGHT - top_thickness
    leg_height = cfg.SIDE_TABLE_HEIGHT - top_thickness
    shelf_length = width - 2 * leg_size
    shelf_depth = depth - 2 * leg_size
    shelf_z = deck_z + cfg.SIDE_TABLE_SHELF_HEIGHT

    builder.add_box(
        "furniture",
        "SideTableTop",
        width,
        depth,
        top_thickness,
        table_x,
        table_y,
        top_z,
        cfg.SIDE_TABLE_COLOR,
        properties={
            "complex_type": "outdoor_side_table",
            "assembly_role": "table_surface",
            "supported_by": "complex.furniture.side_table_leg_*",
            "clear_of": "complex.fireplace.fireplace_masonry_body",
            "minimum_clearance_mm": to_mm(clearance),
        },
    )
    leg_corners = (
        (table_x, table_y),
        (table_x + width - leg_size, table_y),
        (table_x, table_y + depth - leg_size),
        (table_x + width - leg_size, table_y + depth - leg_size),
    )
    for index, (leg_x, leg_y) in enumerate(leg_corners, 1):
        builder.add_box(
            "furniture",
            f"SideTableLeg_{index}",
            leg_size,
            leg_size,
            leg_height,
            leg_x,
            leg_y,
            deck_z,
            cfg.SIDE_TABLE_COLOR,
            parent_id="complex.furniture.side_table_top",
            properties={
                "complex_type": "side_table_leg",
                "assembly_role": "table_support",
                "stands_on": "complex.deck_board.upper_*",
            },
        )
    builder.add_box(
        "furniture",
        "SideTableLowerShelf",
        shelf_length,
        shelf_depth,
        cfg.SIDE_TABLE_SHELF_THICKNESS,
        table_x + leg_size,
        table_y + leg_size,
        shelf_z,
        cfg.SIDE_TABLE_COLOR,
        parent_id="complex.furniture.side_table_top",
        properties={
            "complex_type": "side_table_lower_shelf",
            "assembly_role": "storage_shelf",
            "between": "complex.furniture.side_table_leg_*",
        },
    )
