"""Shed slab, walls, roof, doors, and shed-to-grass rock transition."""

from __future__ import annotations

from typing import Any

from python_cad_tools.elements import Dimensions
from python_cad_tools.geometry import box
from python_cad_tools.units import INCH, Length, to_mm

from models.shared import CUT_MARGIN, ZERO


def add_shed(builder: Any, cfg: Any, shed_x: Length, shed_y: Length) -> tuple[Length, Length]:
    shed_parent_id = "complex.shed.yard_storage_shed"
    shed_front_y = shed_y + cfg.SHED_DEPTH
    shed_wall_top = cfg.SHED_WALL_HEIGHT
    shed_ridge_x = shed_x + cfg.SHED_WIDTH / 2
    shed_ridge_z = shed_wall_top + cfg.SHED_ROOF_RISE
    common = {
        "complex_type": "yard_storage_shed",
        "view_relationship": "negative-X yard; front at y=-24yd; body extends toward negative Y",
        "reference": "Photo 1 deck-to-yard view",
    }
    builder.add_box(
        "shed",
        "YardStorageShed",
        cfg.SHED_WIDTH,
        cfg.SHED_DEPTH,
        cfg.SHED_SLAB_THICKNESS,
        shed_x,
        shed_y,
        -cfg.SHED_SLAB_THICKNESS,
        (0.15, 0.15, 0.15),
        drawing_label=True,
        properties={**common, "assembly_role": "foundation"},
    )
    wall_thickness = 4 * INCH
    side_door_y = shed_front_y - cfg.SHED_SIDE_DOOR_WIDTH - 18 * INCH
    for name, length, depth, x, y in (
        ("ShedLeftWall", wall_thickness, cfg.SHED_DEPTH, shed_x, shed_y),
        ("ShedRightWall", wall_thickness, cfg.SHED_DEPTH, shed_x + cfg.SHED_WIDTH - wall_thickness, shed_y),
        ("ShedRearWall", cfg.SHED_WIDTH, wall_thickness, shed_x, shed_y),
        ("ShedFrontWall", cfg.SHED_WIDTH, wall_thickness, shed_x, shed_front_y - wall_thickness),
    ):
        wall_shape = box(length, depth, cfg.SHED_WALL_HEIGHT, origin=(x, y, ZERO))
        opening_for = None
        if name == "ShedRightWall":
            wall_shape = wall_shape.cut(
                box(
                    wall_thickness + CUT_MARGIN,
                    cfg.SHED_SIDE_DOOR_WIDTH + CUT_MARGIN,
                    cfg.SHED_SIDE_DOOR_HEIGHT + CUT_MARGIN,
                    origin=(x - CUT_MARGIN / 2, side_door_y - CUT_MARGIN / 2, -CUT_MARGIN / 2),
                )
            )
            opening_for = "complex.shed.shed_side_service_door"
        elif name == "ShedFrontWall":
            front_door_x = shed_x + (cfg.SHED_WIDTH - cfg.SHED_FRONT_DOOR_WIDTH) / 2
            wall_shape = wall_shape.cut(
                box(
                    cfg.SHED_FRONT_DOOR_WIDTH + CUT_MARGIN,
                    wall_thickness + CUT_MARGIN,
                    cfg.SHED_FRONT_DOOR_HEIGHT + CUT_MARGIN,
                    origin=(front_door_x - CUT_MARGIN / 2, y - CUT_MARGIN / 2, -CUT_MARGIN / 2),
                )
            )
            opening_for = "complex.shed.shed_front_double_door"
        properties: dict[str, Any] = {**common, "assembly_role": "wall"}
        if opening_for:
            properties.update({"opening_for": opening_for, "wall_opening": True})
        builder.add_shape(
            "shed",
            name,
            wall_shape,
            cfg.SHED_SIDING_COLOR,
            Dimensions(to_mm(length), to_mm(depth), to_mm(cfg.SHED_WALL_HEIGHT)),
            placement=(x, y, ZERO),
            parent_id=shed_parent_id,
            properties=properties,
        )
    slope_ratio = float(to_mm(cfg.SHED_ROOF_RISE)) / float(to_mm(cfg.SHED_WIDTH / 2))
    shed_eave_z = shed_wall_top - cfg.SHED_ROOF_OVERHANG * slope_ratio
    roof_y = shed_y - cfg.SHED_ROOF_OVERHANG
    roof_depth = cfg.SHED_DEPTH + 2 * cfg.SHED_ROOF_OVERHANG
    builder.add_prism(
        "shed",
        "ShedRoofLeftSlope",
        (shed_x - cfg.SHED_ROOF_OVERHANG, roof_y, shed_eave_z),
        (shed_ridge_x, roof_y, shed_ridge_z),
        roof_depth,
        cfg.SHED_ROOF_THICKNESS,
        cfg.SHED_ROOF_COLOR,
        parent_id=shed_parent_id,
        properties={**common, "assembly_role": "roof"},
    )
    builder.add_prism(
        "shed",
        "ShedRoofRightSlope",
        (shed_ridge_x, roof_y, shed_ridge_z),
        (shed_x + cfg.SHED_WIDTH + cfg.SHED_ROOF_OVERHANG, roof_y, shed_eave_z),
        roof_depth,
        cfg.SHED_ROOF_THICKNESS,
        cfg.SHED_ROOF_COLOR,
        parent_id=shed_parent_id,
        properties={**common, "assembly_role": "roof"},
    )
    front_door_x = shed_x + (cfg.SHED_WIDTH - cfg.SHED_FRONT_DOOR_WIDTH) / 2
    builder.add_box(
        "shed",
        "ShedFrontDoubleDoor",
        cfg.SHED_FRONT_DOOR_WIDTH,
        INCH,
        cfg.SHED_FRONT_DOOR_HEIGHT,
        front_door_x,
        shed_front_y,
        ZERO,
        cfg.SHED_TRIM_COLOR,
        parent_id=shed_parent_id,
        properties={**common, "assembly_role": "front_double_door"},
    )
    builder.add_box(
        "shed",
        "ShedSideServiceDoor",
        INCH,
        cfg.SHED_SIDE_DOOR_WIDTH,
        cfg.SHED_SIDE_DOOR_HEIGHT,
        shed_x + cfg.SHED_WIDTH,
        side_door_y,
        ZERO,
        cfg.SHED_TRIM_COLOR,
        parent_id=shed_parent_id,
        properties={**common, "assembly_role": "side_service_door"},
    )
    rock_bed_x = shed_x + cfg.SHED_WIDTH
    rock_bed_width = ZERO - rock_bed_x
    builder.add_box(
        "site",
        "ShedGrassRockBed",
        rock_bed_width,
        cfg.SHED_DEPTH,
        cfg.ROCK_BED_THICKNESS,
        rock_bed_x,
        shed_y,
        -cfg.ROCK_BED_THICKNESS,
        cfg.ROCK_COLOR,
        drawing_label=True,
        properties={
            "complex_type": "landscape_rock_bed",
            "assembly_role": "transition_between_shed_and_grass",
            "from_element_id": shed_parent_id,
            "to_element_id": "complex.site.unified_yard_grass",
            "surface": "landscape_rock",
        },
    )
    return rock_bed_x, rock_bed_width
