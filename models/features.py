"""Fireplace, sliding-door, and outdoor-kitchen geometry; keep below 400 lines."""

from __future__ import annotations

from typing import Any

from python_cad_tools.elements import Dimensions
from python_cad_tools.geometry import box
from python_cad_tools.units import FOOT, INCH, Length, mm, to_mm

from models.shared import CUT_MARGIN, ZERO


def add_features(
    builder: Any,
    cfg: Any,
    roof_back_z: Length,
    roof_front_z: Length,
    sliding_door_x: Length,
    sliding_door_y: Length,
) -> None:
    """Append fireplace, sliding-door, and outdoor-kitchen elements in order."""
    _fp_front_y = -cfg.FIREPLACE_DEPTH
    _roof_back_y = cfg.ROOF_OVERHANG
    _roof_front_y = -cfg.UPPER_DECK_DEPTH - cfg.ROOF_OVERHANG
    _ratio = (_fp_front_y - _roof_back_y) / (_roof_front_y - _roof_back_y)
    _fireplace_height_mm = to_mm(roof_back_z) + _ratio * (to_mm(roof_front_z) - to_mm(roof_back_z))
    fireplace_body_height = mm(_fireplace_height_mm)
    fireplace_face_x = cfg.FIREPLACE_WIDTH
    fireplace_center_y = -cfg.FIREPLACE_DEPTH / 2
    firebox_y = fireplace_center_y - cfg.FIREPLACE_OPENING_WIDTH / 2
    firebox_z = cfg.UPPER_DECK_ELEVATION + 12 * INCH
    fireplace_body = box(
        cfg.FIREPLACE_WIDTH,
        cfg.FIREPLACE_DEPTH,
        fireplace_body_height,
        origin=(ZERO, -cfg.FIREPLACE_DEPTH, ZERO),
    )
    firebox_void = box(
        14 * INCH + CUT_MARGIN,
        cfg.FIREPLACE_OPENING_WIDTH + CUT_MARGIN,
        cfg.FIREPLACE_OPENING_HEIGHT + CUT_MARGIN,
        origin=(
            cfg.FIREPLACE_WIDTH - 14 * INCH - CUT_MARGIN / 2,
            firebox_y - CUT_MARGIN / 2,
            firebox_z - CUT_MARGIN / 2,
        ),
    )
    builder.add_shape(
        "fireplace",
        "FireplaceMasonryBody",
        fireplace_body.cut(firebox_void),
        cfg.BRICK_COLOR,
        Dimensions(to_mm(cfg.FIREPLACE_WIDTH), to_mm(cfg.FIREPLACE_DEPTH), to_mm(fireplace_body_height)),
        drawing_label=True,
        properties={
            "complex_type": "masonry_fireplace_with_firebox",
            "assembly_role": "fireplace_enclosure",
            "opening_for": "complex.fireplace.fireplace_opening",
            "wall_opening": True,
        },
    )
    builder.add_box(
        "fireplace",
        "FireplaceOpening",
        12 * INCH,
        cfg.FIREPLACE_OPENING_WIDTH,
        cfg.FIREPLACE_OPENING_HEIGHT,
        fireplace_face_x - 12 * INCH,
        firebox_y,
        firebox_z,
        (0.03, 0.03, 0.03),
        properties={
            "complex_type": "electric_firebox",
            "assembly_role": "recessed_insert_cavity",
            "opening_in": "complex.fireplace.fireplace_masonry_body",
        },
    )
    builder.add_box(
        "fireplace",
        "ElectricFireplaceGlow",
        1.5 * INCH,
        5 * FOOT,
        cfg.FIREPLACE_OPENING_HEIGHT - 6 * INCH,
        fireplace_face_x + INCH,
        fireplace_center_y - (5 * FOOT) / 2,
        cfg.UPPER_DECK_ELEVATION + 15 * INCH,
        (0.90, 0.28, 0.08),
    )
    builder.add_box(
        "fireplace",
        "FireplaceTV",
        INCH,
        cfg.TV_WIDTH,
        cfg.TV_HEIGHT,
        fireplace_face_x + 1.5 * INCH,
        fireplace_center_y - cfg.TV_WIDTH / 2,
        cfg.UPPER_DECK_ELEVATION + 56 * INCH,
        (0.02, 0.02, 0.025),
    )
    mantel_depth = 4 * INCH
    mantel_height = 2 * INCH
    mantel_width = cfg.FIREPLACE_OPENING_WIDTH + 2 * FOOT
    builder.add_box(
        "fireplace",
        "FireplaceMantel",
        mantel_depth,
        mantel_width,
        mantel_height,
        fireplace_face_x,
        fireplace_center_y - mantel_width / 2,
        cfg.UPPER_DECK_ELEVATION + 12 * INCH + cfg.FIREPLACE_OPENING_HEIGHT + 2 * INCH,
        (0.15, 0.10, 0.05),
    )
    chimney_center_x = cfg.FIREPLACE_WIDTH / 2
    chimney_x = chimney_center_x - cfg.CHIMNEY_WIDTH / 2
    chimney_y = -cfg.CHIMNEY_DEPTH
    chimney_bottom_z = fireplace_body_height
    roof_peak_z = roof_back_z
    chimney_top_z = roof_peak_z + cfg.CHIMNEY_HEIGHT_ABOVE_ROOF
    builder.add_box(
        "fireplace",
        "FireplaceChimney",
        cfg.CHIMNEY_WIDTH,
        cfg.CHIMNEY_DEPTH,
        chimney_top_z - chimney_bottom_z,
        chimney_x,
        chimney_y,
        chimney_bottom_z,
        cfg.BRICK_COLOR,
    )
    builder.add_box(
        "fireplace",
        "FireplaceChimneyCap",
        cfg.CHIMNEY_WIDTH + 2 * cfg.CHIMNEY_CAP_OVERHANG,
        cfg.CHIMNEY_DEPTH + 2 * cfg.CHIMNEY_CAP_OVERHANG,
        2 * INCH,
        chimney_x - cfg.CHIMNEY_CAP_OVERHANG,
        chimney_y - cfg.CHIMNEY_CAP_OVERHANG,
        chimney_top_z,
        (0.10, 0.10, 0.10),
    )
    builder.add_box(
        "fireplace",
        "FireplaceFlueHole",
        6 * INCH,
        INCH,
        6 * INCH,
        chimney_center_x - 3 * INCH,
        chimney_y - INCH,
        chimney_bottom_z + 2 * FOOT,
        (0.02, 0.02, 0.02),
    )

    door_frame = 2 * INCH
    builder.add_box(
        "feature",
        "SlidingDoor",
        cfg.DOOR_WIDTH - 2 * door_frame,
        1 * INCH,
        cfg.DOOR_HEIGHT - 2 * door_frame,
        sliding_door_x + door_frame,
        sliding_door_y,
        cfg.UPPER_DECK_ELEVATION + door_frame,
        (0.55, 0.70, 0.82),
        drawing_label=True,
        properties={
            "complex_type": "sliding_glass_door",
            "assembly_role": "glazing",
            "panel_count": 2,
        },
    )
    for frame_name, length, depth, height, x, y, z in (
        (
            "SlidingDoorFrameLeft",
            door_frame,
            3 * INCH,
            cfg.DOOR_HEIGHT,
            sliding_door_x,
            sliding_door_y,
            cfg.UPPER_DECK_ELEVATION,
        ),
        (
            "SlidingDoorFrameRight",
            door_frame,
            3 * INCH,
            cfg.DOOR_HEIGHT,
            sliding_door_x + cfg.DOOR_WIDTH - door_frame,
            sliding_door_y,
            cfg.UPPER_DECK_ELEVATION,
        ),
        (
            "SlidingDoorFrameHead",
            cfg.DOOR_WIDTH,
            3 * INCH,
            door_frame,
            sliding_door_x,
            sliding_door_y,
            cfg.UPPER_DECK_ELEVATION + cfg.DOOR_HEIGHT - door_frame,
        ),
        (
            "SlidingDoorFrameSill",
            cfg.DOOR_WIDTH,
            3 * INCH,
            door_frame,
            sliding_door_x,
            sliding_door_y,
            cfg.UPPER_DECK_ELEVATION,
        ),
        (
            "SlidingDoorMeetingRail",
            door_frame,
            3 * INCH,
            cfg.DOOR_HEIGHT - 2 * door_frame,
            sliding_door_x + cfg.DOOR_WIDTH / 2 - door_frame / 2,
            sliding_door_y,
            cfg.UPPER_DECK_ELEVATION + door_frame,
        ),
    ):
        builder.add_box(
            "feature",
            frame_name,
            length,
            depth,
            height,
            x,
            y,
            z,
            cfg.RAILING_COLOR,
            parent_id="complex.feature.sliding_door",
            properties={"complex_type": "door_frame_member", "assembly_role": "sliding_door_frame"},
        )

    kitchen_x = 10.5 * cfg.FOOT
    kitchen_y = -1 * INCH - cfg.KITCHEN_DEPTH - 2 * INCH
    builder.add_box(
        "outdoor-kitchen",
        "OutdoorKitchenCabinetRun",
        cfg.KITCHEN_LENGTH,
        cfg.KITCHEN_DEPTH,
        cfg.KITCHEN_COUNTER_HEIGHT - cfg.KITCHEN_COUNTER_THICKNESS,
        kitchen_x,
        kitchen_y,
        cfg.UPPER_DECK_ELEVATION,
        (0.12, 0.12, 0.12),
        drawing_label=True,
    )
    sink_x = kitchen_x + 18 * INCH
    sink_y = kitchen_y + (cfg.KITCHEN_DEPTH - cfg.KITCHEN_SINK_DEPTH) / 2
    counter_z = cfg.UPPER_DECK_ELEVATION + cfg.KITCHEN_COUNTER_HEIGHT - cfg.KITCHEN_COUNTER_THICKNESS
    countertop = box(
        cfg.KITCHEN_LENGTH + 4 * INCH,
        cfg.KITCHEN_DEPTH + 4 * INCH,
        cfg.KITCHEN_COUNTER_THICKNESS,
        origin=(kitchen_x - 2 * INCH, kitchen_y - 2 * INCH, counter_z),
    )
    sink_cutout = box(
        cfg.KITCHEN_SINK_WIDTH + CUT_MARGIN,
        cfg.KITCHEN_SINK_DEPTH + CUT_MARGIN,
        cfg.KITCHEN_COUNTER_THICKNESS + CUT_MARGIN,
        origin=(sink_x - CUT_MARGIN / 2, sink_y - CUT_MARGIN / 2, counter_z - CUT_MARGIN / 2),
    )
    builder.add_shape(
        "outdoor-kitchen",
        "OutdoorKitchenCountertop",
        countertop.cut(sink_cutout),
        (0.45, 0.45, 0.42),
        Dimensions(
            to_mm(cfg.KITCHEN_LENGTH + 4 * INCH),
            to_mm(cfg.KITCHEN_DEPTH + 4 * INCH),
            to_mm(cfg.KITCHEN_COUNTER_THICKNESS),
        ),
        placement=(kitchen_x - 2 * INCH, kitchen_y - 2 * INCH, counter_z),
        properties={
            "complex_type": "countertop_with_sink_cutout",
            "assembly_role": "work_surface",
            "opening_for": "complex.outdoor_kitchen.outdoor_kitchen_sink_basin",
        },
    )
    sink_outer = box(
        cfg.KITCHEN_SINK_WIDTH,
        cfg.KITCHEN_SINK_DEPTH,
        5 * INCH,
        origin=(sink_x, sink_y, cfg.UPPER_DECK_ELEVATION + cfg.KITCHEN_COUNTER_HEIGHT - 5 * INCH),
    )
    sink_inner = box(
        cfg.KITCHEN_SINK_WIDTH - 2 * INCH,
        cfg.KITCHEN_SINK_DEPTH - 2 * INCH,
        4.5 * INCH,
        origin=(sink_x + INCH, sink_y + INCH, cfg.UPPER_DECK_ELEVATION + cfg.KITCHEN_COUNTER_HEIGHT - 4.5 * INCH),
    )
    builder.add_shape(
        "outdoor-kitchen",
        "OutdoorKitchenSinkBasin",
        sink_outer.cut(sink_inner),
        (0.12, 0.15, 0.16),
        Dimensions(to_mm(cfg.KITCHEN_SINK_WIDTH), to_mm(cfg.KITCHEN_SINK_DEPTH), to_mm(5 * INCH)),
        placement=(sink_x, sink_y, cfg.UPPER_DECK_ELEVATION + cfg.KITCHEN_COUNTER_HEIGHT - 5 * INCH),
        properties={"complex_type": "open_sink_basin", "assembly_role": "sink"},
    )
    builder.add_cylinder(
        "outdoor-kitchen",
        "OutdoorKitchenFaucet",
        (
            sink_x + cfg.KITCHEN_SINK_WIDTH / 2,
            sink_y + cfg.KITCHEN_SINK_DEPTH,
            cfg.UPPER_DECK_ELEVATION + cfg.KITCHEN_COUNTER_HEIGHT,
        ),
        (
            sink_x + cfg.KITCHEN_SINK_WIDTH / 2,
            sink_y + cfg.KITCHEN_SINK_DEPTH,
            cfg.UPPER_DECK_ELEVATION + cfg.KITCHEN_COUNTER_HEIGHT + 10 * INCH,
        ),
        INCH,
        (0.75, 0.75, 0.72),
    )
    builder.add_cylinder(
        "outdoor-kitchen",
        "OutdoorKitchenFaucetSpout",
        (
            sink_x + cfg.KITCHEN_SINK_WIDTH / 2,
            sink_y + cfg.KITCHEN_SINK_DEPTH,
            cfg.UPPER_DECK_ELEVATION + cfg.KITCHEN_COUNTER_HEIGHT + 10 * INCH,
        ),
        (
            sink_x + cfg.KITCHEN_SINK_WIDTH / 2,
            sink_y + cfg.KITCHEN_SINK_DEPTH - 7 * INCH,
            cfg.UPPER_DECK_ELEVATION + cfg.KITCHEN_COUNTER_HEIGHT + 10 * INCH,
        ),
        0.75 * INCH,
        (0.75, 0.75, 0.72),
        parent_id="complex.outdoor_kitchen.outdoor_kitchen_faucet",
        properties={"complex_type": "faucet_spout", "assembly_role": "water_outlet"},
    )
    grill_x = kitchen_x + cfg.KITCHEN_LENGTH + 6 * INCH
    builder.add_box(
        "outdoor-kitchen",
        "OutdoorKitchenGrill",
        cfg.KITCHEN_GRILL_WIDTH,
        cfg.KITCHEN_DEPTH + 2 * INCH,
        36 * INCH,
        grill_x,
        kitchen_y - INCH,
        cfg.UPPER_DECK_ELEVATION,
        (0.05, 0.05, 0.05),
    )
    for index, door_x in enumerate((kitchen_x + 12 * INCH, kitchen_x + 36 * INCH, kitchen_x + 60 * INCH), 1):
        builder.add_box(
            "outdoor-kitchen",
            f"OutdoorKitchenDoor_{index}",
            cfg.KITCHEN_DOOR_WIDTH,
            INCH,
            24 * INCH,
            door_x,
            kitchen_y - INCH,
            cfg.UPPER_DECK_ELEVATION + 8 * INCH,
            (0.22, 0.22, 0.22),
        )
