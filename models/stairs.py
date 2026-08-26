"""Stair and railing geometry collection; keep this focused module under 400 lines."""

from __future__ import annotations

import math
from typing import Any

from python_cad_tools.units import INCH, Length, mm, to_mm

import config as cfg
from models.shared import ZERO, Point2
from models.shared import slug as _slug


def rail_segment(builder: Any, name: str, start: Point2, end: Point2, z: Length, cfg_module: Any = cfg) -> None:
    rail_height = cfg_module.RAILING_HEIGHT
    rail_thickness = cfg_module.RAILING_RAIL_SIZE
    builder.add_prism(
        "railing",
        name,
        (start[0], start[1], z + rail_height - rail_thickness),
        (end[0], end[1], z + rail_height - rail_thickness),
        rail_thickness,
        rail_thickness,
        cfg_module.RAILING_COLOR,
    )
    builder.add_cylinder(
        "railing",
        f"{name}Midrail",
        (start[0], start[1], z + rail_height / 2),
        (end[0], end[1], z + rail_height / 2),
        rail_thickness / 2,
        cfg_module.RAILING_COLOR,
    )
    dx = to_mm(end[0] - start[0])
    dy = to_mm(end[1] - start[1])
    run = math.hypot(dx, dy)
    baluster_count = max(1, math.ceil(run / to_mm(cfg_module.RAILING_BALUSTER_MAX_SPACING)) - 1)
    first_baluster_index = 2 if name == "StairSideRail" else 1
    for index in range(first_baluster_index, baluster_count + 1):
        ratio = index / (baluster_count + 1)
        baluster_x = mm(to_mm(start[0]) + dx * ratio)
        baluster_y = mm(to_mm(start[1]) + dy * ratio)
        builder.add_cylinder(
            "railing",
            f"{name}Baluster_{index:03d}",
            (baluster_x, baluster_y, z + rail_thickness),
            (baluster_x, baluster_y, z + rail_height - rail_thickness),
            cfg_module.RAILING_BALUSTER_SIZE / 2,
            cfg_module.RAILING_COLOR,
            parent_id=f"complex.railing.{_slug(name)}",
            properties={
                "complex_type": "railing_baluster",
                "assembly_role": "guard_infill",
                "maximum_spacing_mm": to_mm(cfg_module.RAILING_BALUSTER_MAX_SPACING),
            },
        )


def rail_post(builder: Any, name: str, x: Length, y: Length, z: Length, cfg_module: Any = cfg) -> None:
    post_thickness = cfg_module.RAILING_POST_SIZE
    builder.add_box(
        "railing",
        name,
        post_thickness,
        post_thickness,
        cfg_module.RAILING_HEIGHT,
        x - post_thickness / 2,
        y - post_thickness / 2,
        z,
        cfg_module.RAILING_COLOR,
    )


def line_frame(start: Point2, end: Point2) -> tuple[float, float, float, float, float]:
    dx = to_mm(end[0] - start[0])
    dy = to_mm(end[1] - start[1])
    run = math.hypot(dx, dy)
    return dx, dy, run, -dy / run, dx / run


def stair_rail_top_points(
    start: Point2, end: Point2, width: Length = cfg.STAIR_WIDTH, left_rail_x_shift: Length = ZERO
) -> tuple[Point2, Point2]:
    _, _, _, px, py = line_frame(start, end)
    rail_offset = to_mm(width) / 2
    left_offset = -rail_offset + to_mm(left_rail_x_shift)
    left_top = (mm(to_mm(start[0]) + px * left_offset), mm(to_mm(start[1]) + py * left_offset))
    right_top = (mm(to_mm(start[0]) + px * rail_offset), mm(to_mm(start[1]) + py * rail_offset))
    return left_top, right_top


def stair_run(
    builder: Any,
    prefix: str,
    start: Point2,
    end: Point2,
    start_z: Length,
    end_z: Length,
    width: Length = cfg.STAIR_WIDTH,
    left_rail_x_shift: Length = ZERO,
    axis: str = "y",
    cfg_module: Any = cfg,
) -> None:
    dx, dy, run, px, py = line_frame(start, end)
    steps = max(1, math.ceil(abs(to_mm(start_z - end_z)) / to_mm(cfg_module.MAX_RISER)))
    rise = to_mm(start_z - end_z) / steps
    direction_x, direction_y = dx / run, dy / run
    riser_thickness = 1.25 * INCH
    riser_center_setback = (to_mm(cfg_module.TREAD_DEPTH) - to_mm(riser_thickness)) / 2
    diagonal_riser_backset = to_mm(cfg_module.TREAD_DEPTH) - to_mm(riser_thickness)
    stair_skirt_width = 2 * INCH
    skirt_offset = to_mm(width) / 2 + to_mm(stair_skirt_width) / 2 + to_mm(0.125 * INCH)
    is_diagonal = abs(dx) > 0.1 and abs(dy) > 0.1
    for index in range(1, steps + 1):
        ratio = index / steps
        center_x = to_mm(start[0]) + dx * ratio
        center_y = to_mm(start[1]) + dy * ratio
        tread_z = to_mm(start_z) - rise * index
        if is_diagonal:
            tread_start = (
                mm(center_x - px * skirt_offset),
                mm(center_y - py * skirt_offset),
                mm(tread_z - to_mm(cfg_module.DECK_BOARD_THICKNESS)),
            )
            tread_end = (mm(center_x + px * skirt_offset), mm(center_y + py * skirt_offset), tread_start[2])
            builder.add_prism(
                "stair",
                f"{prefix}Tread_{index:02d}",
                tread_start,
                tread_end,
                cfg_module.TREAD_DEPTH,
                cfg_module.DECK_BOARD_THICKNESS,
                cfg_module.DECK_COLOR,
            )
            riser_center_x = center_x - direction_x * diagonal_riser_backset
            riser_center_y = center_y - direction_y * diagonal_riser_backset
            riser_start = (
                mm(riser_center_x - px * skirt_offset),
                mm(riser_center_y - py * skirt_offset),
                start_z + (end_z - start_z) * ratio,
            )
            riser_end = (mm(riser_center_x + px * skirt_offset), mm(riser_center_y + py * skirt_offset), riser_start[2])
            tread_id = f"complex.stair.{_slug(prefix)}_tread_{index:02d}"
            builder.add_prism(
                "stair",
                f"{prefix}Riser_{index:02d}",
                riser_start,
                riser_end,
                riser_thickness,
                mm(abs(rise)),
                cfg_module.SKIRTING_COLOR,
                parent_id=tread_id,
                properties={
                    "complex_type": "stair_riser",
                    "assembly_role": "vertical_step_closure",
                    "associated_tread_id": tread_id,
                    "position": "back_of_tread",
                },
            )
        else:
            tread_length = width if axis == "y" else cfg_module.TREAD_DEPTH
            tread_depth = cfg_module.TREAD_DEPTH if axis == "y" else width
            builder.add_box(
                "stair",
                f"{prefix}Tread_{index:02d}",
                tread_length,
                tread_depth,
                cfg_module.DECK_BOARD_THICKNESS,
                mm(center_x - to_mm(tread_length) / 2),
                mm(center_y - to_mm(tread_depth) / 2),
                mm(tread_z - to_mm(cfg_module.DECK_BOARD_THICKNESS)),
                cfg_module.DECK_COLOR,
            )
            riser_center_x = center_x - direction_x * riser_center_setback
            riser_center_y = center_y - direction_y * riser_center_setback
            riser_x_dim = tread_length if axis == "y" else riser_thickness
            riser_y_dim = riser_thickness if axis == "y" else tread_depth
            tread_id = f"complex.stair.{_slug(prefix)}_tread_{index:02d}"
            builder.add_box(
                "stair",
                f"{prefix}Riser_{index:02d}",
                riser_x_dim,
                riser_y_dim,
                mm(abs(rise)),
                mm(riser_center_x - to_mm(riser_x_dim) / 2),
                mm(riser_center_y - to_mm(riser_y_dim) / 2),
                mm(min(tread_z, tread_z + rise)),
                cfg_module.SKIRTING_COLOR,
                parent_id=tread_id,
                properties={
                    "complex_type": "stair_riser",
                    "assembly_role": "vertical_step_closure",
                    "associated_tread_id": tread_id,
                    "position": "back_of_tread",
                },
            )
    rail_height = cfg_module.RAILING_HEIGHT
    rail_thickness = cfg_module.RAILING_RAIL_SIZE
    for side_name, side_sign in (("Left", -1), ("Right", 1)):
        extra_shift = to_mm(left_rail_x_shift) if side_name == "Left" else 0.0
        offset = side_sign * to_mm(width) / 2 + extra_shift
        start_x, start_y = mm(to_mm(start[0]) + px * offset), mm(to_mm(start[1]) + py * offset)
        end_x, end_y = mm(to_mm(end[0]) + px * offset), mm(to_mm(end[1]) + py * offset)
        builder.add_cylinder(
            "railing",
            f"{prefix}{side_name}Handrail",
            (start_x, start_y, start_z + rail_height),
            (end_x, end_y, end_z + rail_height),
            rail_thickness,
            cfg_module.RAILING_COLOR,
        )
        builder.add_cylinder(
            "railing",
            f"{prefix}{side_name}Midrail",
            (start_x, start_y, start_z + rail_height / 2),
            (end_x, end_y, end_z + rail_height / 2),
            rail_thickness / 2,
            cfg_module.RAILING_COLOR,
        )
        skirt_extra = to_mm(left_rail_x_shift) if side_name == "Left" else 0.0
        skirt_start = (
            mm(to_mm(start[0]) + px * (side_sign * skirt_offset + skirt_extra)),
            mm(to_mm(start[1]) + py * (side_sign * skirt_offset + skirt_extra)),
            start_z - 8 * INCH,
        )
        skirt_end = (
            mm(to_mm(end[0]) + px * (side_sign * skirt_offset + skirt_extra)),
            mm(to_mm(end[1]) + py * (side_sign * skirt_offset + skirt_extra)),
            end_z - 8 * INCH,
        )
        builder.add_prism(
            "skirting",
            f"{prefix}{side_name}StairSkirt",
            skirt_start,
            skirt_end,
            stair_skirt_width,
            10 * INCH,
            cfg_module.SKIRTING_COLOR,
        )
        rail_post(builder, f"{prefix}{side_name}Post_Top", start_x, start_y, start_z, cfg_module)
        rail_post(builder, f"{prefix}{side_name}Post_Bottom", end_x, end_y, end_z, cfg_module)


def add_upper_stairs(builder: Any, start: Point2, end: Point2, cfg_module: Any = cfg) -> tuple[Point2, Point2]:
    tops = stair_rail_top_points(start, end, cfg_module.STAIR_WIDTH)
    stair_run(
        builder,
        "UpperStraight",
        start,
        end,
        cfg_module.UPPER_DECK_ELEVATION,
        cfg_module.LOWER_DECK_ELEVATION,
        axis="y",
        cfg_module=cfg_module,
    )
    return tops


def add_lower_stairs(builder: Any, start: Point2, end: Point2, width: Length, cfg_module: Any = cfg) -> None:
    stair_run(builder, "LowerFront", start, end, cfg_module.LOWER_DECK_ELEVATION, ZERO, width, cfg_module=cfg_module)


def add_final_rails(
    builder: Any,
    upper_left_top: Point2,
    upper_right_top: Point2,
    upper_stair_start: Point2,
    lower_x: Length,
    lower_stair_width: Length,
    pool_left_edge_x: Length,
    pool_right_edge_x: Length,
    cfg_module: Any = cfg,
) -> None:
    upper_depth = cfg_module.UPPER_DECK_DEPTH
    upper_elevation = cfg_module.UPPER_DECK_ELEVATION
    lower_elevation = cfg_module.LOWER_DECK_ELEVATION
    post_thickness = cfg_module.RAILING_POST_SIZE
    rail_segment(builder, "UpperFrontRail", (ZERO, -upper_depth), upper_left_top, upper_elevation, cfg_module)
    rail_segment(
        builder,
        "UpperStraightHouseRail",
        upper_right_top,
        (cfg_module.UPPER_DECK_WIDTH, ZERO),
        upper_elevation,
        cfg_module,
    )
    rail_segment(
        builder,
        "StairSideRail",
        (cfg_module.UPPER_DECK_WIDTH - post_thickness, -upper_depth),
        upper_stair_start,
        upper_elevation,
        cfg_module,
    )
    rail_segment(
        builder, "LeftEdgeRail", (ZERO, -cfg_module.FIREPLACE_DEPTH), (ZERO, -upper_depth), upper_elevation, cfg_module
    )
    rail_segment(
        builder,
        "LowerRightRail",
        (lower_x + cfg_module.LOWER_DECK_WIDTH, -cfg_module.LOWER_DECK_DEPTH),
        (lower_x + cfg_module.LOWER_DECK_WIDTH, ZERO - 2 * INCH),
        lower_elevation,
        cfg_module,
    )
    rail_segment(
        builder,
        "LowerLeftRail",
        (ZERO, -upper_depth),
        (ZERO, -cfg_module.LOWER_DECK_DEPTH),
        lower_elevation,
        cfg_module,
    )
    lower_back_rail_y = ZERO - 2 * INCH
    rail_segment(
        builder,
        "LowerBackRail",
        (lower_x, lower_back_rail_y),
        (lower_x + cfg_module.LOWER_DECK_WIDTH, lower_back_rail_y),
        lower_elevation,
        cfg_module,
    )
    lower_front_y = -cfg_module.LOWER_DECK_DEPTH
    rail_post(builder, "LowerFrontRailStairBoundaryPost", lower_stair_width, lower_front_y, lower_elevation, cfg_module)
    rail_post(builder, "LowerFrontRailPoolLeftPost", pool_left_edge_x, lower_front_y, lower_elevation, cfg_module)
    rail_post(builder, "LowerFrontRailPoolRightPost", pool_right_edge_x, lower_front_y, lower_elevation, cfg_module)
    rail_segment(
        builder,
        "LowerFrontRailLeft",
        (lower_stair_width, lower_front_y),
        (pool_left_edge_x, lower_front_y),
        lower_elevation,
        cfg_module,
    )
    rail_segment(
        builder,
        "LowerFrontRailRight",
        (pool_right_edge_x, lower_front_y),
        (lower_x + cfg_module.LOWER_DECK_WIDTH, lower_front_y),
        lower_elevation,
        cfg_module,
    )
    for name, post_x, post_y, post_z in [
        ("UpperPost_L", ZERO, -upper_depth, upper_elevation),
        ("LowerPost_LH", lower_x, lower_back_rail_y, lower_elevation),
        ("LowerPost_RH", lower_x + cfg_module.LOWER_DECK_WIDTH, lower_back_rail_y, lower_elevation),
        ("LowerPost_RF", lower_x + cfg_module.LOWER_DECK_WIDTH, -cfg_module.LOWER_DECK_DEPTH, lower_elevation),
    ]:
        rail_post(builder, name, post_x, post_y, post_z, cfg_module)
