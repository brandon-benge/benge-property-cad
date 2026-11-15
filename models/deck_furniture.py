"""Upper-deck side table beside the fireplace lounge; keep below 400 lines."""

from __future__ import annotations

from typing import Any

from python_cad_tools.units import to_mm


def add_deck_furniture(builder: Any, cfg: Any) -> None:
    """Append the small side table that stands on the upper deck boards.

    The table sits just south-east of the masonry fireplace body so it belongs
    to the fireplace lounge while staying clear of the firebox face, the
    fireplace body, the left edge railing, the front railing, and the
    sliding-door approach.
    """
    deck_z = cfg.UPPER_DECK_ELEVATION
    top_size = cfg.DECK_SIDE_TABLE_TOP_SIZE
    top_x = cfg.DECK_SIDE_TABLE_CENTER_X - top_size / 2
    top_y = cfg.DECK_SIDE_TABLE_CENTER_Y - top_size / 2
    top_z = deck_z + cfg.DECK_SIDE_TABLE_HEIGHT - cfg.DECK_SIDE_TABLE_TOP_THICKNESS
    leg_height = top_z - deck_z
    inset = cfg.DECK_SIDE_TABLE_LEG_INSET
    leg_size = cfg.DECK_SIDE_TABLE_LEG_SIZE

    table_top = builder.add_box(
        "feature",
        "DeckSideTableTop",
        top_size,
        top_size,
        cfg.DECK_SIDE_TABLE_TOP_THICKNESS,
        top_x,
        top_y,
        top_z,
        cfg.DECK_COLOR,
        properties={
            "complex_type": "deck_side_table",
            "assembly_role": "table_top",
            "label": "Upper Deck Side Table",
            "located_on": "complex.deck_board.upper_*",
            "clear_of": "complex.fireplace.fireplace_masonry_body, complex.feature.sliding_door",
            "top_surface_above_deck_mm": to_mm(cfg.DECK_SIDE_TABLE_HEIGHT),
        },
    )

    far_x = top_x + top_size - inset - leg_size
    far_y = top_y + top_size - inset - leg_size
    leg_positions = (
        (top_x + inset, top_y + inset),
        (far_x, top_y + inset),
        (top_x + inset, far_y),
        (far_x, far_y),
    )
    for index, (leg_x, leg_y) in enumerate(leg_positions, 1):
        builder.add_box(
            "feature",
            f"DeckSideTableLeg_{index:02d}",
            leg_size,
            leg_size,
            leg_height,
            leg_x,
            leg_y,
            deck_z,
            cfg.DECK_SIDE_TABLE_FRAME_COLOR,
            parent_id=table_top.id,
            properties={
                "complex_type": "deck_side_table",
                "assembly_role": "table_leg",
                "supports": table_top.id,
            },
        )

    shelf_span = top_size - 2 * (inset + leg_size)
    shelf_x = top_x + inset + leg_size
    shelf_y = top_y + inset + leg_size
    builder.add_box(
        "feature",
        "DeckSideTableLowerShelf",
        shelf_span,
        shelf_span,
        cfg.DECK_SIDE_TABLE_SHELF_THICKNESS,
        shelf_x,
        shelf_y,
        deck_z + cfg.DECK_SIDE_TABLE_SHELF_ABOVE_DECK - cfg.DECK_SIDE_TABLE_SHELF_THICKNESS,
        cfg.DECK_COLOR,
        parent_id=table_top.id,
        properties={
            "complex_type": "deck_side_table",
            "assembly_role": "lower_shelf",
            "braces": ", ".join(
                f"complex.feature.deck_side_table_leg_{index:02d}" for index in range(1, len(leg_positions) + 1)
            ),
            "shelf_height_above_deck_mm": to_mm(cfg.DECK_SIDE_TABLE_SHELF_ABOVE_DECK),
        },
    )
